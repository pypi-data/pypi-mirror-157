"""
xengsort/build.py

Utilities to build a hash table from a data source,
e.g. FASTA or FASTQ files or arrays of k-mer codes.

all_fasta_seqs():
    Yield each sequence and two values for each sequence in a FASTA file
generate_kmer_iterator():
    Return a generator function that yields each k-mer (canonical) code in a sequence
DEPRECATED generate_kmer_array_iterator():
    Return a generator function that yields each k-mer sub-array in a sequence

build_from_fasta():
    Fill a hash table with the k-mers and values from FASTA files,
    used by index.py.
verify_from_fasta():
    Check that a hash table is correctly filled with all k-mers from FASTA files,
    used by verify.py.
build_from_fastq():
    Fill a hash table with the k-mers and values from FASTQ files,
    used by index.py.

"""


import numpy as np
from numpy.random import seed as randomseed
from numba import njit, uint8, void, int64, uint64, boolean

import numba

from .dnaio import fasta_reads, fastq_chunks
from .dnaencode import (generate_revcomp_and_canonical_code,
                        dna_to_2bits, quick_dna_to_2bits)
from .hashfunctions import make_get_pagestatus_c
from .intbitarray import intbitarray


# Generator that yields all sequences and values from FASTA files ##############

def all_fasta_seqs(fastas, value_from_name, both, skipvalue, *, progress=False):
    """
    Yield a (sq, v1, v2) triple for each sequence in given fastas, where:
    - sq is the two-bit-encoded sequence,
    - v1 is the first value derived from the header using value_from_name,
    - v2 is the second value derived from the header using value_from_name,
      or identical to v1 if both==False.
    Sequences whose v1 evaluates to skipvalue are skipped.
    Progress is printed to stdout if progress=True.
    """
    for fasta in fastas:
        print(f"# Processing '{fasta}':")
        for header, seq in fasta_reads(fasta):
            name = header.split()[0]
            v1 = value_from_name(name, 1)
            if v1 == skipvalue:
                if progress:
                    print(f"  Entry '{name.decode()}': length {len(seq)}, skipping")
                continue
            v2 = value_from_name(name, 2) if both else v1
            if progress:
                print(f"#   Entry '{name.decode()}': length {len(seq)}, values {v1}, {v2}")
            sq = dna_to_2bits(seq)
            yield (sq, v1, v2)


def generate_kmer_iterator(shp, rcmode="f"):
    """
    Return a compiled k-mer iterator (generator function)
    for the given shape 'shp', which can be 
    - an integer k for a contiguous shape,
    - or a tuple of growing indices, where k is the length of the tuple.
    """
    both = (rcmode == "both")
    if isinstance(shp, int):
        # special case: contiguous k-shape
        k = shp
        shp = None
    elif isinstance(shp, tuple):
        k = len(shp)
        if shp == tuple(range(k)): shp = None  # back to special case
    else:
        raise TypeError(f"shape shp={shp} must be int or k-tuple, but is {type(shp)}.")
    if k < 1: 
        raise ValueError(f"only k>=1 is supported (k>32 with restrictions), but k={k}.")
    if k > 32:
        if rcmode != f or shp is not None:
            raise ValueError(f"for k > 32, only rcmode='f' and contiguous shapes are supported")
        return generate_kmer_array_iterator(k)
    codemask = uint64(4**(k-1) - 1)
    revcomp, ccode = generate_revcomp_and_canonical_code(k, rcmode)

    if shp is None:
        # special case: contiguous k-mer
        print(f"# processing contiguous {k}-mers")
        @njit( ###__signature__ (uint8[:], int64, int64),
            nogil=True, locals=dict(
                code=uint64, endpoint=int64, i=int64, j=int64, c=uint64))
        def kmers(seq, start, end):
            endpoint = end - (k-1)
            valid = False
            i = start
            while i < endpoint:
                if not valid:
                    code = 0
                    for j in range(k):
                        c = seq[i+j]
                        if c > 3:
                            i += j + 1  # skip invalid
                            break
                        code = (code << 2) | c
                    else:  # no break
                        valid = True
                    if not valid: continue  # with while
                else:  # was valid, we have an old code
                    c = seq[i+k-1]
                    if c > 3:
                        valid = False
                        i += k  # skip invalid
                        continue  # with while
                    code = ((code & codemask) << 2) | c
                # at this point, we have a valid code
                if both:
                    yield code
                    yield revcomp(code)
                else:
                    yield ccode(code)
                i += 1
            pass  # all done here
    else:
        # general shape: k:int and shp:tuple are set
        print(f"# processing general {k}-mers: {shp}")
        @njit( ###__signature__ (uint8[:], int64, int64),
            nogil=True, locals=dict(
                code=uint64, startpoint=int64, i=int64, j=int64, c=uint64))
        def kmers(seq, start, end):
            startpoints = (end - start) - shp[k-1]
            for i in range(start, start+startpoints):
                code = 0
                for j in shp:
                    c = seq[i+j]
                    if c > 3:
                        break
                    code = (code << 2) + c
                else:  # no break
                    if both:
                        yield code
                        yield revcomp(code)
                    else:
                        yield ccode(code)
            # all done here

    return k, kmers



def generate_kmer_array_iterator(k):
    """
    Return a pair (k, kmers),
    where kmers is a compiled k-mer array iterator (generator function)
    for the given value of k,
    which yields each (valid) contiguous sub-array of a sequence.
    """
    # TODO: improve efficiency (rolling)
    @njit( ###__signature__ (uint8[:], int64, int64), 
        nogil=True, locals=dict(
            code=uint64, startpoint=int64, i=int64, j=int64, c=uint64))
    def kmers(seq, start, end):
        end = min(start + 200, end)
        startpoints = (end - start) - (k-1)
        for i in range(start, start+startpoints):
            for j in range(k):
                c = seq[i+j]
                if c > 3:
                    break
                else:  # no break
                    yield seq[i:i+k]  # should be a view
            # all done here
    return k, kmers



# efficient k-mer processor for arbitrary shapes with function injection ###

def generate_kmer_processor(shp, func, rcmode="f"):
    """
    Return a compiled k-mer iterator that executes a function 'func'
    for each valid k-mer of for the given shape 'shp', which can be 
    - an integer k for a contiguous shape,
    - or a tuple of growing indices, where k is the length of the tuple.

    Signature of func must be as follows:
    def func(hashtable, kmercode, param1, param2, param3, ...):
        ...
        return boolean(failure)
    Parameters param1, ... can be an arbitrary number of arrays.
    """

    both = (rcmode == "both")
    if isinstance(shp, int):
        # special case: contiguous k-shape
        k = shp
        shp = None
    elif isinstance(shp, tuple):
        k = len(shp)
        if shp == tuple(range(k)): shp = None  # back to special case
    else:
        raise TypeError(f"shape shp={shp} must be int or k-tuple, but is {type(shp)}.")
    if k < 1 or k > 32:
        raise ValueError(f"only 1<=k<=32 is supported, but k={k}.")
    codemask = uint64(4**(k-1) - 1)
    revcomp, ccode = generate_revcomp_and_canonical_code(k, rcmode)
    
    if shp is None:
        # special case: contiguous k-mer
        print(f"# processing contiguous {k}-mers")
        @njit(
            nogil=True, locals=dict(
                code=uint64, endpoint=int64, i=int64, j=int64, c=uint64))
        def kmers(ht, seq, start, end, *parameters):
            endpoint = end - (k-1)
            valid = failed = False
            i = start
            while i < endpoint:
                if not valid:
                    code = 0
                    for j in range(k):
                        c = seq[i+j]
                        if c > 3:
                            i += j + 1  # skip invalid
                            break
                        code = (code << 2) | c
                    else:  # no break
                        valid = True
                    if not valid: continue  # with while
                else:  # was valid, we have an old code
                    c = seq[i+k-1]
                    if c > 3:
                        valid = False
                        i += k  # skip invalid
                        continue  # with while
                    code = ((code & codemask) << 2) | c
                # at this point, we have a valid code
                if both:
                    failed  = func(ht, code, *parameters)
                    failed |= func(ht, revcomp(code), *parameters)
                else:
                    failed = func(ht, ccode(code), *parameters)
                i += 1
                if failed: break
            pass  # all done here; end of def kmers(...).
    else:
        # general shape: k:int and shp:tuple are given
        print(f"# processing general {k}-mers: {shp}")
        @njit( ###__signature__ (uint8[:], int64, int64),
            nogil=True, locals=dict(
                code=uint64, startpoint=int64, i=int64, j=int64, c=uint64))
        def kmers(ht, seq, start, end, *parameters):
            startpoints = (end - start) - shp[k-1]
            failed = False
            for i in range(start, start+startpoints):
                code = 0
                for j in shp:
                    c = seq[i+j]
                    if c > 3:
                        break
                    code = (code << 2) + c
                else:  # no break
                    if both:
                        failed  = func(ht, code, *parameters)
                        failed |= func(ht, revcomp(code), *parameters)
                    else:
                        failed = func(ht, ccode(code), *parameters)
                if failed: break
            # all done here

    return k, kmers


# build from FASTA #####################################

def build_from_fasta(
    fastas,  # list of FASTA files
    shp,  # k-mer size or shape
    h,  # hash data structure, pre-allocated, to be filled (h.store_item)
    value_from_name,  # function mapping FASTA entry names to numeric values
    *,
    rcmode="min",  # from 'f', 'r', 'both', 'min', 'max'
    skipvalue=0,  # value that skips a FASTA entry
    walkseed=7,
    maxfailures=0,
    ):
    """
    Build (fill) pre-allocated (and correctly sized) hash table 'h'
    with 'k'-mers from FASTA files 'fastas'.

    Each entry from each FASTA file is processed sequentially.
    The name of the entry (after '>' up to the first space or '_') is converted
    into a numeric value using function value_from_name(name, 1) 
    and/or value_from_name(name, 2), depending on 'rcmode'.
    Each k-mer (and/or reverse complementary k-mer) of the entry is inserted into 'h'
    with the computed value.
    If the k-mer is already present, its value is updated accordint to h's value update policy.

    rcmode has the following effect:
    rcmode=='f': insert k-mers as they appear in the file using value_from_name(name, 1)
    rcmode=='r': insert reverse complementary k-mers using value_from_name(name, 2)
    rcmode=='both': insert both k-mers using two different values
    rcmode=='min': insert the smaller of the two k-mers using value_from_name(name, 1)
    rcmode=='max': insert the larger of the two k-mers using value_from_name(name, 1)

    Return (total, failed, walkstats), where:
      total is the total number of valid k-mers read, 
      failed is the number of k-mers unsuccessfully processed,
      walkstats is an array indexed 0 to h.maxwalk+slack, counting walk lengths
    """
    print(f"# Building from FASTA, using rcmode={rcmode}, maxfailures={maxfailures}")
    
    @njit
    def store_in_table(ht, code, status, stats):
        breakout = False
        vx = status[0] - status[1]  # vsum - vx
        status[2] += 1  # total
        result = store_item(ht, code, vx)
        stats[abs(result)] += 1
        if result < 0:
            status[3] += 1  # fail
            if maxfailures >= 0 and status[3] > maxfailures:
                breakout = True
        status[1] = status[0] - status[1]  # vx = vsum - vx
        return breakout  # flag: finally FAILED if nonzero
    
    k, process_kmers = generate_kmer_processor(shp, store_in_table, rcmode)
    # because the supplied function 'store_in_table' has TWO extra parameterd (status, stats),
    # the generated function 'process_kmers' also gets the same TWO extra parameters.

    assert 4**k == h.universe, f"Error: k={k}; 4**k={4**k}; but universe={h.universe}"
    store_item = h.store_item
    
    revcomp, ccode = generate_revcomp_and_canonical_code(k, rcmode)
    codemask = uint64(4**(k-1) - 1)

    @njit( ###__signature__ void(),
        nogil=True)
    def set_seed():
        randomseed(walkseed)

    @njit( ###__signature__ (uint64[:], uint8[:], int64, int64, int64, int64, uint64[:], int64),
        nogil=True, 
        #locals=dict(code=uint64, result=int64, fail=int64, endpoint=int64, i=int64, j=int64, c=uint64))
        locals=dict(total=int64, fail=int64, v1=uint64, v2=uint64, vsum=uint64))
    def add_kmers(ht, seq, start, end, v1, v2, status, stats):
        vsum = v1 + v2
        status[0:3] = (vsum, v1, uint64(0))  # status[3]==fail is kept
        process_kmers(ht, seq, start, end, status, stats)
        total, fail = status[2], status[3]
        return (total, fail)  # stats has been modified, too!
    
    set_seed()
    ht = h.hashtable
    both = (rcmode=="both")
    total = fail = 0
    stats = np.zeros(h.maxwalk+5, dtype=np.uint64)
    status = np.zeros(4, dtype=np.uint64)
    for (sq, v1, v2) in all_fasta_seqs(
            fastas, value_from_name, both, skipvalue):
        (dtotal, fail) = add_kmers(ht, sq, 0, len(sq), v1, v2, status, stats)
        total += dtotal
        if maxfailures >= 0 and fail > maxfailures: 
            break
    # done; hashtable h is now filled; return statistics
    return (total, fail, stats)


# verify from FASTA #####################################

def verify_from_fasta(
    fastas,  # list of FASTA files
    shp,     # k-mer shape or size
    h,       # populated hash data structure to be checked (h.get_value)
    value_from_name,      # function mapping FASTA entry names to numeric values
    value_is_compatible,  # function checking whether observed value 
    *,                    # is compatible with stored value (observed, stored)
    rcmode="min",  # from {'f', 'r', 'both', 'min', 'max'}
    skipvalue=0,   # value that skips a FASTA entry
    ):
    """
    Verify that all k-mers from FASTA files 'fastas'
    are correctly represented in hash table 'h' (present and compatible value).    with 'k'-mers from FASTA files 'fastas'.
    
    For name-to-value conversion, see build_from_fasta().
    For rcmode options {'f', 'r', 'both', 'min', 'max'}, see build_from_fasta().

    Return (ok, kmer, fasta_value, stored_value) om failure;
    return (ok, nsequences, -1, -1) on success, where
    - ok is the number of successfully verified k-mers before failure
    - kmer is the kmer encoding
    - fasta_value, stored_value are the incompatible values >= 0,
    - nsequences is the number of successfully processed sequences.
    """
    print(f"# Verifying from FASTA, using rcmode={rcmode}")
    k, kmers = generate_kmer_iterator(shp, rcmode)
    assert 4**k == h.universe, f"Error: k={k}; 4**k={4**k}; but universe={h.universe}"
    get_value = h.get_value

    @njit( ###__signature__ (uint64[:], uint8[:], int64, int64, int64, int64),
        nogil=True, locals=dict(
            code=uint64, v=int64, v1=int64, v2=int64, vx=int64, vsum=int64))
    def check_kmers(ht, seq, start, end, v1, v2):
        ok = 0
        vsum = v1 + v2
        vx = v1
        for code in kmers(seq, start, end):
            v = get_value(ht, code)
            if not value_is_compatible(vx, v): # (observed, stored)
                return (ok, code, v, vx)  # (stored, observed)
            ok += 1
            vx = vsum - vx
        return (ok, 0, -1, -1)

    ht = h.hashtable
    both = (rcmode == "both")
    ok = 0
    for (i,(sq, v1, v2)) in enumerate(all_fasta_seqs(
            fastas, value_from_name, both, skipvalue, progress=True)):
        ##print(i, len(sq), v1, v2, ht.shape)
        (dok, key, value, expected) = check_kmers(ht, sq, 0, len(sq), v1, v2)
        ok += int(dok)
        if value != -1:
            return (ok, int(key), int(value), int(expected))
    nsequences = i+1
    return (ok, nsequences, -1, -1)


# FASTQ #####################################

def build_from_fastq(
    fastqs,  # list of FASTQ files
    shp,  # k-mer size or shape
    h,  # hash data structure, pre-allocated, to be filled (h.store_item)
    values, # pair of values for indexing
    *,
    rcmode="min",  # from 'f', 'r', 'both', 'min', 'max'
    walkseed=7,
    maxfailures=0,
    bufsize=2**23,
    chunkreads=2**23//200,
    ):
    """
    Build (fill) pre-allocated (and correctly sized) hash table 'h'
    with 'k'-mers from FASTQ files 'fastqs'.

    Each entry from each FASTQ file is processed sequentially.
    Each k-mer (and/or reverse complementary k-mer) of the entry 
    is inserted into 'h' with one of the given value.
    If the k-mer is already present, its value is updated,
    according to h's value update policy.

    rcmode has the following effect:
    rcmode=='f': insert k-mers as they appear in the file using value1.
    rcmode=='r': insert reverse complementary k-mers using value2.
    rcmode=='both': insert both k-mers using value1 and value2, respectively.
    rcmode=='min': insert the smaller of the two k-mers using value1.
    rcmode=='max': insert the larger of the two k-mers using value1.

    Return (total, failed, walkstats), where:
      total is the total number of valid k-mers read, 
      failed is the number of k-mers unsuccessfully processed,
      walkstats is an array indexed 0 to h.maxwalk+slack, counting walk lengths
    """
    print(f"# Building from FASTQ, using rcmode={rcmode}, values={values}")
    print(f"# shp={shp}, rcmode={rcmode}, maxfailures={maxfailures}.")
    k, kmers = generate_kmer_iterator(shp, rcmode)
    assert 4**k == h.universe, f"Error: k={k}; 4**k={4**k}; but universe={h.universe}"
    store_item = h.store_item
    print("## DEBUG values: {v1}, {v2}")  # DEBUG
    v1, v2 = values
    if rcmode == "r":
        v1 = v2
    elif rcmode == "both":
        pass
    else:
        v2 = v1
    vsum = v1 + v2

    @njit( ###__signature__ void(),
        nogil=True)
    def set_seed():
        randomseed(walkseed)

    @njit( ###__signature__ (uint64[:], uint8[:], uint64[:], int64),
        nogil=True, locals=dict(code=uint64, vx=uint64, result=int64))
    def add_kmers(ht, seq, stats, fail):
        # note that v1, v2 are known constants
        vx = v1
        total = 0
        for code in kmers(seq, 0, len(seq)):
            total += 1
            result = store_item(ht, code, vx)
            stats[abs(result)] += 1
            if result < 0:
                fail += 1
                if maxfailures >= 0 and fail > maxfailures:
                    break
            vx = vsum - vx
        return (total, fail)

    @njit( ###__signature__ (uint8[:], int32[:,:], uint64[:], uint64[:], uint64),  # infer return type
        nogil=True)
    def add_kmers_chunkwise(buf, linemarks, ht, stats, fail):
        total = 0
        n = linemarks.shape[0]
        for i in range(n):
            sq = buf[linemarks[i,0]:linemarks[i,1]]
            quick_dna_to_2bits(sq)
            (dtotal, fail) = add_kmers(ht, sq, stats, fail)
            total += dtotal
            if maxfailures >= 0 and fail > maxfailures: 
                break
        return total, fail
   
    set_seed()
    ht = h.hashtable
    total = fail = 0
    stats = np.zeros(h.maxwalk+5, dtype=np.uint64)
    for chunk in fastq_chunks(fastqs, bufsize=bufsize, maxreads=chunkreads):
        dtotal, fail = add_kmers_chunkwise(chunk[0], chunk[1], ht, stats, fail)
        total += dtotal
        if maxfailures >= 0 and fail > maxfailures: 
            break
    # done; hashtable h is now filled; return statistics
    return (total, fail, stats)


def build_from_dump(h, k, nkmers, acodes, achoices, avalues):
    npages = h.npages
    pagesize = h.pagesize
    (get_pf1, get_pf2, get_pf3) = h.get_pf
    set_signature_at = h.set_signature_at
    set_value_at = h.set_value_at
    get_pagestatus = make_get_pagestatus_c(h.pagesize,
            h.get_value_at, h.get_signature_at,
            h.signature_parts, h.signature_full)
    choices = intbitarray(nkmers, 2, init=achoices)
    values = intbitarray(nkmers, 3, init=avalues)
    codes = intbitarray(nkmers, 2*k, init=acodes)
    get_code = codes.get
    get_value = values.get
    get_choice = choices.get
    @njit
    def _insert_elements(ht):
        total = 0
        for i in range(nkmers):
            total += 1
            code = get_code(acodes, i)
            value = get_value(avalues, i)
            choice = get_choice(achoices, i)
            assert choice >= 1
            if choice == 1:
                page, fpr = get_pf1(code)
            elif choice == 2:
                page, fpr = get_pf2(code)
            elif choice == 3:
                page, fpr = get_pf3(code)
            else:
                assert False
            (slot, fill) = get_pagestatus(ht, page, fpr, choice)
            assert fill != pagesize
            assert slot == -1

            set_signature_at(ht, page, fill, fpr, choice)
            set_value_at(ht, page, fill, value)
        return total

    total = _insert_elements(h.hashtable)
    walklength = np.zeros(h.maxwalk+5, dtype=np.uint64)
    walklength[0] = total
    return (total, 0, walklength)



def make_calc_lucky_bits(h):
    bits = h.luckybits  # 0, 1 or 2
    is_slot_empty_at = h.is_slot_empty_at
    signature_parts = h.signature_parts
    get_signature_at = h.get_signature_at
    set_luckybit_at = h.set_luckybit_at
    (get_pf1, get_pf2, get_pf3) = h.get_pf
    get_key_choice_sig = h.get_key_choice_sig
    npages = h.npages
    pagesize = h.pagesize

    if bits < 0 or bits > 2: 
        print("# WARNING: Illegal number of lucky bits; using 0")
        bits = 0

    if bits == 0:
        @njit
        def calc_lucky_bits(table):
            pass
        return calc_lucky_bits

    if bits == 1:
        @njit
        def calc_lucky_bits(table):
            for page in range(npages):
                for slot in range(pagesize):
                    if is_slot_empty_at(table, page, slot):
                        continue
                    key, c = get_key_choice_sig(page, get_signature_at(table, page, slot))
                    if c == 0:
                        continue
                    # treat c >= 1
                    firstpage, _ = get_pf1(key)
                    set_luckybit_at(table, firstpage, 1)
                    if c >= 2:
                        secpage, _ = get_pf2(key)
                        set_luckybit_at(table, secpage, 1)
        return calc_lucky_bits
    
    # bits == 2
    @njit
    def calc_lucky_bits(table):
        for page in range(npages):
            for slot in range(pagesize):
                if is_slot_empty_at(table, page, slot):
                    continue
                key, c = get_key_choice_sig(page, get_signature_at(table, page, slot))
                if c == 0:
                    continue
                if c == 1:
                    firstpage, _ = get_pf1(key)
                    set_luckybit_at(table, firstpage, 1)
                    continue
                # now c == 2:
                firstpage, _ = get_pf1(key)
                set_luckybit_at(table, firstpage, 2)
                secpage, _ = get_pf2(key)
                set_luckybit_at(table, secpage, 2)
    return calc_lucky_bits

