"""
xengsort.index:
Build index for host and graft reference genomes.
by Jens Zentgraf & Sven Rahmann, 2019--2021

Example:
xengsort index test.h5 -H <(zcat /scratch/data/xenograft/mouse_GCF_000001635.26_GRCm38.p6_genomic.fn.gz) -G <(zcat /scratch/data/xenograft/human_GCF_000001405.26_GRCh38_genomic.fna.gz) -k 13 -P 40000000 3FCVbb:a --hashfunctions linear945:linear9123641:linear349341847 -p 8 --fill 0.9
"""

import sys
import datetime
from importlib import import_module
import numpy as np
from numba import njit, uint8, uint32, uint64, int64, jit, prange

from .mathutils import print_histogram, print_histogram_tail
from .hashfunctions import get_npages
from .build import build_from_fasta, verify_from_fasta, build_from_dump, make_calc_lucky_bits
from .hashio import save_hash
from .dnaencode import generate_revcomp_and_canonical_code
from .h5utils import load_from_h5group

DEFAULT_HASHTYPE = "3FCVbb"


# parameters ############################################

def get_valueset_parameters(valueset, *, rcmode=None, k=None, strict=True):
    # process valueset
    vimport = "values." + valueset[0]
    vmodule = import_module("."+vimport, __package__)
    values = vmodule.initialize(*(valueset[1:]))
    vstr =  " ".join([vimport] + valueset[1:])
    if not rcmode: rcmode = values.RCMODE
    parameters = None  # no specific dataset parameters given
    return (values, vstr, rcmode, k, parameters)


def parse_parameters(parameters, args, *, singles=True):
    (nobjects, hashtype, aligned, hashfuncs, pagesize, nfingerprints, fill) \
        = parameters if parameters is not None \
          else (10_000_000, "default", False, "random", 0, -1, 0.9)
    # process args.parameters first
    P = args.parameters
    if P:
        print(f"# Overwriting parameters with {P}")
        p = P[0]
        if p != "_":
            nobjects = int(p)
        if len(P) > 1:
            p = P[1]
            if p != "_":
                hashtype, _, al = p.partition(":")
                if al:
                    aligned = (al.lower() == "a")
        if len(P) > 2:
            p = P[2]
            if p != "_":
                hashfuncs = p
        if len(P) > 3:
            p = P[3]
            if p != "_":
                pagesize = int(p)
        if len(P) > 4:
            p = P[4]
            if p != "_":
                fill = float(p)
    # process single command line arguments
    if singles:
        if args.nobjects is not None:
            nobjects = args.nobjects
        if args.type is not None:
            hashtype = args.type
        if args.aligned is not None:
            aligned = args.aligned
        if args.hashfunctions is not None:
            hashfuncs = args.hashfunctions
        if args.pagesize is not None:
            pagesize = args.pagesize
        if args.fill is not None:
            fill = args.fill
    # pack up and return
    parameters = (nobjects, hashtype, aligned, hashfuncs, pagesize, nfingerprints, fill)
    return parameters


@njit(nogil=True, locals=dict(
    elem1=uint64, elem2=uint64, h=uint64, mask=uint64, onebit=uint32))
def calc_hamming_dist_one(elem1, elem2):
    mask = uint64(6148914691236517205)  # Mask for ....01010101 for uint64
    h = elem1 ^ elem2
    h = (h | (h >> 1)) & mask
    onebit = (h & uint64(h - 1)) == uint64(0)
    return onebit


def make_get_block_borders(prefix_length, k):

    @njit(nogil=True, locals=dict(prefix=int64))
    def get_block_borders(codes):
        prefix = -1
        blocks = 0
        # Get number of blocks
        for i, code in enumerate(codes):
            new_prefix = code >> (2 * (k - prefix_length))
            if new_prefix != prefix:
                prefix = new_prefix
                blocks += 1

        # Find block borders
        block_borders = np.zeros(blocks + 1, dtype=np.uint64)
        block = 0
        prefix = -1
        for i, code in enumerate(codes):
            new_prefix = code >> (2 * (k - prefix_length))
            if new_prefix != prefix:
                prefix = new_prefix
                block_borders[block] = i
                block += 1
        block_borders[block] = len(codes)
        return block_borders

    return get_block_borders


def make_update_hashtable(store_item, cc, WEAKBIT):
    
    @njit(nogil=True, locals=dict(nweak=uint64))
    def update_hashtable(ht, codes, values):
        nweak = 0
        for pos in range(len(codes)):
            if values[pos] & WEAKBIT:
                wl = store_item(ht, cc(codes[pos]), 0)
                assert wl < 4
                nweak += 1
        return nweak
    
    return update_hashtable


def make_calculate_weak_kmers_end(prefix_length, k, WEAKBIT):
    get_block_borders = make_get_block_borders(prefix_length, k)

    @njit(nogil=True, parallel=True, locals=dict(
            pos=uint64, mid=uint64, code=uint64, end=uint64,
            prefix_mask=uint64, suffix_mask=uint64) )  # parallel=True ??
    def calculate_weak_kmers_at_end(codes, values):
        block_borders = get_block_borders(codes)
        for block in range(len(block_borders) - 1):
            for pos in prange(block_borders[block], block_borders[block + 1]):
                element = codes[pos]
                value = values[pos] & 3
                found = False
                for pos2 in range(pos + 1, block_borders[block + 1]):
                    # Check wether both elements are host or graft
                    if ((value & 3) == (values[pos2] & 3)): continue
                    sec_element = codes[pos2]
                    if calc_hamming_dist_one(element, sec_element):
                        found = True
                        values[pos2] |= WEAKBIT
                if found:
                    values[pos] |= WEAKBIT
    return calculate_weak_kmers_at_end


def make_calculate_weak_kmers_middle(prefix_length, k, WEAKBIT):
    suffix_mask = 2**(2 * (prefix_length - 1)) - 1
    prefix_mask = suffix_mask << (2 * (prefix_length))

    @njit(nogil=True, parallel=True, locals=dict(pos=uint64, mid=uint64, code=uint64, end=uint64,
          prefix_mask=uint64, suffix_mask=uint64))
    def calculate_weak_kmers_middle(codes, values):
        for pos in prange(len(codes)):
            codes[pos] = (codes[pos] & prefix_mask) | ((codes[pos] & suffix_mask) << 2) | ((codes[pos] >> (2 * (k // 2))) & 3)
        out_order = np.argsort(codes)
        for pos in prange(len(codes) - 1):
            element = codes[out_order[pos]]
            for i in range(1, 4):
                if (pos + i) > (len(codes) - 1):
                    break
                sec_element = codes[out_order[pos + i]]
                if ((values[out_order[pos]] & 3) == (values[out_order[pos + i]] & 3)): continue
                if ((element >> 2) == (sec_element >> 2)):
                    values[out_order[pos]] |= WEAKBIT
                    values[out_order[pos + i]] |= WEAKBIT
                else:
                    break  # inner for loop
        for pos in prange(len(codes)):
            codes[pos] = (codes[pos] & prefix_mask) | ((codes[pos] & 3) << (2 * (k // 2))) | ((codes[pos] & (suffix_mask << 2)) >> 2)

    return calculate_weak_kmers_middle


def make_calculate_weak_kmers(h, k, cc, T, block_prefix_length):
    if k % 2 == 0:
        prefix_length = (k // 2)
        check_middle = False
    else:
        prefix_length = (k // 2) + 1
        check_middle = True

    store_item = h.store_item
    WEAKBIT = uint8(4)

    update_hashtable = make_update_hashtable(store_item, cc, WEAKBIT)
    calculate_weak_kmers_end = make_calculate_weak_kmers_end(prefix_length, k, WEAKBIT)
    calculate_weak_kmers_middle = make_calculate_weak_kmers_middle(prefix_length, k, WEAKBIT)
    
    @njit(nogil=True)
    def calculate_all_weak_kmers(ht, codes, values):
        calculate_weak_kmers_end(codes, values)
        if check_middle:
            calculate_weak_kmers_middle(codes, values)
        return update_hashtable(ht, codes, values)

    return calculate_all_weak_kmers


def make_get_blocksizes(h, k, prefix_length, rcmode, xenome = False):
    rc, cc = generate_revcomp_and_canonical_code(k, rcmode)
    npages = h.npages
    pagesize = h.pagesize
    get_signature_at = h.get_signature_at
    signature_parts = h.signature_parts
    get_value_at = h.get_value_at
    get_key_sig = h.get_key_sig
    is_slot_empty_at = h.is_slot_empty_at

    # Determine block size
    @njit(nogil=True)
    def get_block_sizes(ht):
        blocks = 4**prefix_length
        blocksizes = np.zeros(blocks, dtype=np.uint64)
        for p in range(npages):
            for s in range(pagesize):
                if is_slot_empty_at(ht, p, s):  continue
                sig = get_signature_at(ht, p, s)
                value = get_value_at(ht, p, s)
                key = get_key_sig(p, sig)
                rev_key = rc(key)
                if k % 2 == 0 and rev_key == key:
                    blocksizes[(key >> (2 * (k - prefix_length)))] += 1
                else:
                    blocksizes[(key >> (2 * (k - prefix_length)))] += 1
                    if not xenome:
                        blocksizes[(rev_key >> (2 * (k - prefix_length)))] += 1
        return blocksizes

    return get_block_sizes


def make_build_block(h, k, prefix_length, rcmode, xenome=False):
    rc, cc = generate_revcomp_and_canonical_code(k, rcmode)
    npages = h.npages
    pagesize = h.pagesize
    get_signature_at = h.get_signature_at
    signature_parts = h.signature_parts
    get_value_at = h.get_value_at
    get_key_sig = h.get_key_sig
    is_slot_empty_at = h.is_slot_empty_at

    @njit(locals=dict(key=uint64, rev_key=uint64, value=uint64))
    def build_block(ht, prefix, blocksize):
        codes = np.empty(blocksize, dtype=np.uint64)
        block_position = 0
        for p in range(npages):
            for s in range(pagesize):
                if is_slot_empty_at(ht, p, s): continue
                value = get_value_at(ht, p, s)
                sig = get_signature_at(ht, p, s)
                key = get_key_sig(p, sig)
                rev_key = rc(key)

                if k % 2 == 0 and rev_key == key:
                    if (key >> (2 * (k - prefix_length))) == prefix:
                        codes[block_position] = (key << 2) | (value & 3)
                        block_position += 1
                else:
                    if (key >> (2 * (k - prefix_length))) == prefix:
                        codes[block_position] = (key << 2) | (value & 3)
                        block_position += 1
                    if not xenome:
                        if (rev_key >> (2 * (k - prefix_length))) == prefix:
                            codes[block_position] = (rev_key << 2) | (value & 3)
                            block_position += 1
            if block_position == blocksize:
                break
        return codes

    return build_block


# calculate weak k-mers ###############################
def make_calculate_weak_set(h, prefix_length, k, rcmode, T, xenome):
    # typical: prefix_length=2; k=25; rcmode="max"
    rc, cc = generate_revcomp_and_canonical_code(k, rcmode)
    get_block_sizes = make_get_blocksizes(h, k, prefix_length, rcmode, xenome = xenome)
    build_block = make_build_block(h, k, prefix_length, rcmode, xenome = xenome)
    calculate_weak_kmers = make_calculate_weak_kmers(h, k, cc, T, prefix_length)
    store_item = h.store_item

    @njit(locals=dict(code=uint64))
    def sort_and_split(codes, values):
        codes.sort()
        for i in range(len(codes)):
            code = codes[i]
            values[i] = code & 3
            codes[i] = code >> 2

    @njit()
    def calculate_weak_set(ht):
        blocksizes = get_block_sizes(ht)
        ##print(blocksizes)
        for prefix in range(len(blocksizes)):
            ##print('# Prefix: ', prefix)
            codes = build_block(ht, prefix, blocksizes[prefix])
            values = np.empty(len(codes), dtype=np.uint8)
            sort_and_split(codes, values)
            weak_kmers = calculate_weak_kmers(ht, codes, values)
            ##print("# Number of weak k-mers: ", weak_kmers)

    return calculate_weak_set



# build index #########################################

def build_index_precomputed(args):
    """build index from precomputed kmers/values"""
    data = load_from_h5group(args.precomputed, "data")
    codes = data["kmercodes"]
    choices = data["choices"]  # is this really necessary?
    valuearray = data["values"]

    valueinfo = load_from_h5group(args.precomputed, "valueinfo")
    valueset = valueinfo['valueset'].decode('ASCII')
    valuestr = valueset  # needed as return value
    print(f"# Importing value set '{valueset}'...")
    valueset = valueset.split()
    if valueset[0].startswith('xengsort.'):
        valueset[0] = valueset[0][len('xengsort.'):]
    vmodule = import_module("."+valueset[0], __package__)
    values = vmodule.initialize(*(valueset[1:]))
    update_value = values.update

    info = load_from_h5group(args.precomputed, "info")["info"]
    hashtype = info['hashtype'].decode("ASCII")
    aligned = bool(info['aligned'])
    universe = int(info['universe'])
    n = int(info['n'])
    k = int(info['k'])
    nkmers = int(info['kmers'])
    rcmode = info['rcmode']
    npages = int(info['npages'])
    pagesize = int(info['pagesize'])
    nfingerprints = int(info['nfingerprints'])
    nvalues = int(info['nvalues'])
    assert nvalues == values.NVALUES, f"Error: inconsistent nvalues (info: {nvalues}; valueset: {values.NVALUES})"
    maxwalk = int(info['maxwalk'])
    hashfuncs = info['hashfuncs'].decode("ASCII")
    print(f"# Hash functions: {hashfuncs}")
    print(f"# Building hash table of type '{hashtype}'...")
    hashmodule = "hash_" + hashtype
    m = import_module(".."+hashmodule, __package__)
    h = m.build_hash(universe, n, pagesize,
        hashfuncs, nvalues, update_value,
        aligned=aligned, nfingerprints=nfingerprints,
        maxwalk=maxwalk, lbits=args.shortcutbits)
    (total, failed, walkstats) = build_from_dump(h, k, nkmers, codes, choices, valuearray)
    return (h, total, failed, walkstats, valuestr, k, rcmode)


def build_index_fasta(args):
    # obtain the parameters
    P = get_valueset_parameters(
        args.valueset, k=args.kmersize, rcmode=args.rcmode)
    (values, valuestr, rcmode, k, parameters) = P
    if not isinstance(k, int):
        print(f"Error: k-mer size k not given; k={k}")
        sys.exit(1)
    print(f"# Imported value set '{valuestr}'.")
    print(f"# Dataset parameters: {parameters}")
    parameters = parse_parameters(parameters, args)
    print(f"# Updated parameters: {parameters}")
    (nobjects, hashtype, aligned, hashfuncs, pagesize, nfingerprints, fill) = parameters

    # create the hash table
    if hashtype == "default":
        hashtype = DEFAULT_HASHTYPE
    hashmodule = import_module(".hash_" + hashtype, __package__)
    build_hash = hashmodule.build_hash
    universe = int(4**k)
    nvalues = values.NVALUES
    value_update = values.update
    n = get_npages(nobjects, pagesize, fill) * pagesize
    print(f"# Allocating hash table for {n} objects, functions '{hashfuncs}'...")
    h = build_hash(universe, n, pagesize,
        hashfuncs, nvalues, value_update,
        aligned=aligned, nfingerprints=nfingerprints,
        maxwalk=args.maxwalk, lbits=args.shortcutbits)
    print(f"# Memory for hash table: {h.mem_bytes/(2**20):.3f} MB")
    print(f"# Info:  rcmode={rcmode}, walkseed={args.walkseed}")
    print(f'# Number of threads for computing weak k-mers: {args.threads}')
    calc_shortcutbits = make_calc_lucky_bits(h)
    # fill the hash table
    value_from_name = values.get_value_from_name_host
    # store all k-mers from host genome
    (total_host, failed_host, walkstats_host) = build_from_fasta(
        args.host, k, h, value_from_name,
        rcmode=rcmode, walkseed=args.walkseed, maxfailures=args.maxfailures)
    if failed_host:
        return (h, total_host, failed_host, walkstats_host, valuestr, k, rcmode)

    # store all k-mers from graft genome
    value_from_name = values.get_value_from_name_graft
    (total_graft, failed_graft, walkstats_graft) = build_from_fasta(
        args.graft, k, h, value_from_name,
        rcmode=rcmode, walkseed=args.walkseed, maxfailures=args.maxfailures)
    if failed_graft:
        return (h, total_graft, failed_graft, walkstats_graft, valuestr, k, rcmode)

    # calculate shortcut bits
    if args.shortcutbits > 0:
        startshort = datetime.datetime.now()
        print(f'# {startshort:%Y-%m-%d %H:%M:%S}: Begin calculating shortcut bits ({args.shortcutbits})...')
        calc_shortcutbits(h.hashtable)
        now = datetime.datetime.now()
        elapsed = (now-startshort).total_seconds()
        print(f'# {now:%Y-%m-%d %H:%M:%S}: Done calculating shortcut bits after {elapsed:.2f} sec.')

    # calculate weak k-mers
    startweak = datetime.datetime.now()
    print(f'# {startweak:%Y-%m-%d %H:%M:%S}: Begin computing weak k-mers...')
    calculate_weak_set = make_calculate_weak_set(
            h, args.chunkprefixlength, k, rcmode, args.threads, args.xenome)
    calculate_weak_set(h.hashtable)
    now = datetime.datetime.now()
    elapsed = (now-startweak).total_seconds()
    print(f'# {now:%Y-%m-%d %H:%M:%S}: Done computing weak k-mers after {elapsed:.2f} sec.')

    # TODO: This does not work, check walkstats
    total = total_host + total_graft
    failed = failed_host + failed_graft
    walkstats = walkstats_host + walkstats_graft
    return (h, total, failed, walkstats, valuestr, k, rcmode)


def compute_absent_average(fillhist, choicehist):
    """Return average memory lookups needed when searching an absent item"""
    ch = len(choicehist) - 1  # number of hash functions (choices)
    s = fillhist.sum()
    z = 1.0 - fillhist[-1] / s  # fraction of pages with an empty slot
    # if a page with an empty slot is seen, we bail out
    r = 1.0
    ex = 0.0
    for i in range(1, ch):  # 1 .. (ch-1)
        ex += i*z
        r *= (1-z)
    ex += ch * r
    return ex


# main #########################################

def main(args):
    """main method for indexing"""
    starttime = datetime.datetime.now()
    source = f"precomputed kmers/values '{args.precomputed}'" if args.precomputed else "FASTAs"
    print(f"# {starttime:%Y-%m-%d %H:%M:%S}: Will build index '{args.index}' from {source}.")

    build_index = build_index_precomputed if args.precomputed else build_index_fasta
    (h, total, failed, walkstats, valueset, k, rcmode) = build_index(args)

    now = datetime.datetime.now()
    if failed == 0:
        print(f"# {now:%Y-%m-%d %H:%M:%S}: SUCCESS, processed {total} k-mers.")
        print(f"# Writing index file '{args.index}'...")
        save_hash(args.index, h, valueset,
            additional=dict(k=k, walkseed=args.walkseed, rcmode=rcmode))
        failed = False
    else:
        print(f"# {now:%Y-%m-%d %H:%M:%S}: FAILED for {failed}/{total} processed k-mers.")
        print(f"# Index file '{args.index}' will NOT be written.")

    show_statistics = not args.nostatistics
    if show_statistics:
        now = datetime.datetime.now()
        print(f"# {now:%Y-%m-%d %H:%M:%S}: Collecting statistics...")
        print()
        valuehist, fillhist, choicehist, shortcuthist = h.get_occupancy(h.hashtable)
        if args.longwalkstats:
            print_histogram(walkstats, title="Walk length statistics:", shorttitle="walk", fractions=".", average=True)
        else:
            print_histogram_tail(walkstats, [1,2,10], title="Extreme walk lengths:", shorttitle="walk", average=True)
        print_histogram(valuehist, title="Value statistics:", shorttitle="values", fractions="%+")
        print_histogram(fillhist, title="Page fill statistics:", shorttitle="fill", fractions="%", average=True, nonzerofrac=True)
        print_histogram(choicehist, title="Choice statistics:", shorttitle="choice", fractions="%+", average="+")
        print_histogram(shortcuthist, title="shortcut bits statistics:", shorttitle="shortcutbits", fractions="%")
        absent = compute_absent_average(fillhist, choicehist)
        print(f"absent average: {absent:.4f}\n")

    endtime = datetime.datetime.now()
    elapsed = (endtime - starttime).total_seconds()
    print(f"time sec: {elapsed:.1f}")
    print(f"time min: {elapsed/60:.3f}")
    print()
    print(f"# {endtime:%Y-%m-%d %H:%M:%S}: Done.")
    if failed:
        print(f"# FAILED! Index file '{args.index}' was NOT written.")
        sys.exit(1)
