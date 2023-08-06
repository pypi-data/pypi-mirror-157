"""
Module xengsort.hashfunctions

This module provides 
*  SRHash, a namedtuple to store hash information
*  create_SRHash(d), to create an SRHash from a dictionary

It provides helper functions for creating hashes.
*  parse_names
*  get_npages

It provides a builder function for hash functions:
*  build_get_page_fpr()
See docstring for details.

It also provides maker functions for hash table methods.
* ...

"""

from math import ceil, log2
from random import randrange
from collections import namedtuple

import numpy as np
from numpy.random import randint
from numba import njit, uint64, uint32, int64, boolean

from .mathutils import bitsfor, nextodd, inversemodprime, inversemodpow2


# An SRHash is filled at the end of build_hash in each concrete hash implementation.
# Thie namedtuple definition here specifies the attributes and methods of SRHash.
SRHash = namedtuple("SRHash", [
    # attributes
    "hashtype",
    "aligned",
    "universe",
    "n",
    "npages",
    "pagesize",
    "nfingerprints",
    "nvalues",
    "maxwalk",
    "hashfuncs",
    "hashtable",
    "mem_bytes",
    "luckybits",
    # methods
    "get_pf",  # method tuple (get_pf1, get_pf2, ...)
    "get_key", # method tuple (get_key1, get_key2, ...)
    "is_slot_empty_at",  # returns True iff the given (page, slot) is empty
    "get_signature_at",  # returns a single int, unpack with signature_parts
    "set_signature_at",
    "get_value_at",
    "set_value_at",
    "get_luckybits_at",  # get all bits
    "set_luckybit_at",   # set ONE of the lucky bits
    "signature_parts",  # signature -> (choice, fingerprint)
    "signature_full",   # (choice, fingerprint) -> signature
    "get_key_sig",
    "get_key_choice_sig",
    "store_item",
    "get_value",
    "get_value_choice",
    "get_occupancy",
    "is_tight",
    "prefetch_page",
    ])


def create_SRHash(d):
    """Return SRHash initialized from values in dictionary d"""
    # The given d does not need to provide mem_bytes; it is computed here.
    # The given d is copied and reduced to the required fields.
    # The hashfuncs tuple is reduced to a single ASCII bytestring.
    d0 = dict(d)
    d0['mem_bytes'] = d0['hashtable'].nbytes
    d1 = { name: d0[name] for name in SRHash._fields }
    d1['hashfuncs'] = (':'.join(d1['hashfuncs'])).encode("ASCII")
    return SRHash(**d1)


## Basic functions #########################################

def get_npages(n, pagesize, fill=1.0):
    return nextodd(ceil(n/fill/pagesize))
    # must be an odd number for equidistribution
    # TODO: write a more detailed reason

def get_nfingerprints(nfingerprints, universe, npages):
    if nfingerprints < 0:
        nfingerprints = int(ceil(universe / npages))
    elif nfingerprints == 0:
        nfingerprints = 1
    return nfingerprints

def check_bits(nbits, name, threshold=64):
    if threshold < 0:
        threshold = abs(threshold)
        if nbits < threshold:
            raise RuntimeError(f"cannot deal with {nbits} < {threshold} {name} bits")
    else:
        if nbits > threshold:
            raise RuntimeError(f"cannot deal with {nbits} > {threshold} {name} bits")


## builder for page and fingerprint functions  #######################

DEFAULT_HASHFUNCS = ("linear62591", "linear42953", "linear48271")

def parse_names(hashfuncs, choices, maxfactor=2**32-1):
    """
    Parse colon-separated string with hash function name(s),
    or string with a special name ("default", "random").
    Return tuple with hash function names.
    """
    if hashfuncs == "default":
        return DEFAULT_HASHFUNCS[:choices]
    elif hashfuncs == "random":
        while True:
            r = [randrange(3, maxfactor, 2) for _ in range(choices)]
            if len(set(r)) == choices: break
        hf = tuple(["linear"+str(x) for x in r])
        return hf
    hf = tuple(hashfuncs.split(":"))
    if len(hf) != choices:
        raise ValueError(f"Error: '{hashfuncs}' does not contain {choices} functions.")
    return hf


def build_get_page_fpr(name, universe, npages, nfingerprints=-1):
    """
    Build hash function 'name' for keys in {0..'universe'-1} that
    hashes injectively to 'npages' pages and 'nfingerprints' fingerprints.
    
    Return a pair of functions: (get_page_fingerprint, get_key), where
    * get_page_fingerprint(key) returns the pair (page, fingerprint),
    * get_key(page, fpr)        returns the key for given page and fingerprint,
    where page is in {0..npages-1}, fingerprint is in {0..nfingerprints-1}.
    
    Invariants:
    - get_key(*get_page_fingerprint(key)) == key for all keys in {0..universe-1}.
    
    The following hash function 'name's are implemented:
    1. linear{ODD}, e.g. linear123, with a positive odd number.
    ...
    
    Restrictions:
    Currently, universe must be a power of 4 (corresponding to a DNA k-mer).
    """
    if nfingerprints < 0:
        nfingerprints = int(ceil(universe / npages))
    elif nfingerprints == 0:
        nfingerprints = 1
    qbits = bitsfor(universe)
    pagebits = int(ceil(log2(npages)))
    pagemask = uint64(2**pagebits - 1)
    fprbits = int(ceil(log2(nfingerprints)))
    fprmask = uint64(2**fprbits - 1)
    codemask = uint64(2**qbits - 1)
    shift = qbits - pagebits

    if 4**(qbits//2) != universe:
        raise ValueError("hash functions require that universe is a power of 4")
    else:
        q = qbits // 2
     
    # define a default get_key function
    get_key = None  # will raise an error if called from numba as a function.
    if name.startswith("linear"):
        a = int(name[6:])
        ai = uint64(inversemodpow2(a, universe))
        a = uint64(a)
        
        @njit( ###__signature__ (uint64,),  # infer return type (uint64, uint64)
            nogil=True, locals=dict(
                code=uint64, swap=uint64, f=uint64, p=uint64))
        def get_page_fpr(code):
            swap = ((code << q) ^ (code >> q)) & codemask
            swap = (a * swap) & codemask
            p = swap % npages
            f = swap // npages
            return (p, f)

        @njit( ###__signature__ uint64(uint64, uint64), 
            nogil=True,
            locals=dict(key=uint64, page=uint64, fpr=uint64))
        def get_key(page, fpr):
            key = fpr * npages + page
            key = (ai * key) & codemask
            key = ((key << q) ^ (key >> q)) & codemask
            return key
    
    else:
        raise ValueError(f"unknown hash function '{name}'")
    return (get_page_fpr, get_key)


def extend_func_tuple(funcs, n):
    """Extend a tuple of functions to n functions by appending dummies"""
    n0 = len(funcs)
    if n0 < 1 or n0 > 3:
        raise ValueError("Only 1 to 3 hash functions are supported.")
    if n0 == n: return funcs
    if n0 > n: 
        raise ValueError(f"Function tuple {funcs} already has {n0}>{n} elements.")
    if n0 == 0:
        raise ValueError(f"Cannot extend an empty tuple.")
    return funcs + (funcs[0],) * (n - n0)


def get_hashfunctions(hashfuncs, choices, universe, npages, nfingerprints):
    # Define functions get_pf{1,2,3,4}(key) to obtain pages and fingerprints.
    # Define functions get_key{1,2,3,4}(page, fpr) to obtain keys back.
    hashfuncs = parse_names(hashfuncs, choices)

    if choices >= 1:
        (get_pf1, get_key1) = build_get_page_fpr(hashfuncs[0], universe, npages, nfingerprints)
    if choices >= 2:
        (get_pf2, get_key2) = build_get_page_fpr(hashfuncs[1], universe, npages, nfingerprints)
    if choices >= 3:
        (get_pf3, get_key3) = build_get_page_fpr(hashfuncs[2], universe, npages, nfingerprints)
    if choices >= 4:
        (get_pf4, get_key4) = build_get_page_fpr(hashfuncs[3], universe, npages, nfingerprints)

    if choices == 1:
        get_pf = (get_pf1,)
        get_key = (get_key1,)
    elif choices == 2:
        get_pf = (get_pf1, get_pf2)
        get_key = (get_key1, get_key2)
    elif choices == 3:
        get_pf = (get_pf1, get_pf2, get_pf3)
        get_key = (get_key1, get_key2, get_key3)
    elif choices == 4:
        get_pf = (get_pf1, get_pf2, get_pf3, get_pf4)
        get_key = (get_key1, get_key2, get_key3, get_key4)
    else:
        raise ValueError("Only 1 to 4 hash functions are supported.")

    return (hashfuncs, get_pf, get_key)


# Makers for get_pagestatus ####################################

def make_is_slot_empty_at_v(get_value_at):
    """
    Factory for VALUE-controlled hash table layouts.
    Return a compiled function 'is_slot_empty_at(table, page, slot)'
    that returns whether a given slot is empty (check by vaue)
    """
    @njit( ###__signature__ boolean(uint64[:], uint64, int64),
        nogil=True, locals=dict(b=boolean))
    def is_slot_empty_at(table, page, slot):
        """Return whether a given slot is empty (check by value)"""
        v = get_value_at(table, page, slot)
        b = (v==0)
        return b
    return is_slot_empty_at

def make_is_slot_empty_at_c(get_signature_at, signature_parts):
    """
    Factory for CHOICE-controlled hash table layouts.
    Return a compiled function 'is_slot_empty_at(table, page, slot)'
    that returns whether a given slot is empty (check by choice)
    """
    @njit( ###__signature__ boolean(uint64[:], uint64, int64),
        nogil=True, locals=dict(b=boolean))
    def is_slot_empty_at(table, page, slot):
        """Return whether a given slot is empty (check by choice)"""
        s = get_signature_at(table, page, slot)
        c = signature_parts(s)[0]
        b = (c == 0)
        return b
    return is_slot_empty_at

# Makers for get_pagestatus ####################################

def make_get_pagestatus_v(pagesize,
            get_value_at, get_signature_at,
            signature_parts, signature_full):
    """
    Factory for VALUE-controlled hash tables ('_v').
    [An empty slot is indicated by value == 0].
    Return a compiled function 'get_pagestatus(table, page, fpr, choice)'.
    """
    @njit( ###__signature__ (uint64[:], uint64, uint64, int64),   # infer return type
        nogil=True, locals=dict(
            page=uint64, fpr=uint64, choice=int64,
            query=uint64, slot=int64, v=uint64, s=uint64))
    def get_pagestatus(table, page, fpr, choice):
        """
        Attempt to locate a (fingerprint, choice) pair on a page,
        assuming value == 0 indicates an empty space.
        Return (int64, uint64):
        Return (slot, value) if the fingerprint 'fpr' was found,
            where 0 <= slot < pagesize.
        Return (-1, fill)    if the fingerprint was not found,
            where fill >= 0 is the number of slots already filled.
        Note: Return type is always (int64, uint64) !
        """
        query = signature_full(choice, fpr)
        for slot in range(pagesize):
            v = get_value_at(table, page, slot)
            if v == 0:
                return (-1, uint64(slot))  # free slot
            s = get_signature_at(table, page, slot)
            if s == query:
                return (slot, v)
        return (-1, uint64(pagesize))
    return get_pagestatus


def make_get_pagestatus_c(pagesize,
            get_value_at, get_signature_at,
            signature_parts, signature_full):
    """
    Factory for CHOICE-controlled hash tables ('_c').
    [An empty slot is indicated by choice == 0].
    Return a compiled function 'get_pagestatus(table, page, fpr, choice)'.
    """
    @njit( ###__signature__ (uint64[:], uint64, uint64, uint64),  # infer return type
        nogil=True, locals=dict(
            page=uint64, fpr=uint64, choice=int64,
            query=uint64, slot=int64, v=uint64, s=uint64))
    def get_pagestatus(table, page, fpr, choice):
        """
        Attempt to locate a (fingerprint, choice) pair on a page,
        assuming choice == 0 indicates an empty space.
        Return (int64, uint64):
        Return (slot, value) if the fingerprint 'fpr' was found,
            where 0 <= slot < pagesize.
        Return (-1, fill)    if the fingerprint was not found,
            where fill >= 0 is the number of slots already filled.
        Note: Return type is always (int64, uint64) !
        """
        query = signature_full(choice, fpr)
        for slot in range(pagesize):
            s = get_signature_at(table, page, slot)
            if s == query:
                v = get_value_at(table, page, slot)
                return (slot, v)
            c = signature_parts(s)[0]
            if c == 0:
                return (-1, uint64(slot))  # free slot
        return (-1, uint64(pagesize))
    return get_pagestatus


# Makers for is_tight #########################################

def make_is_tight_v(npages, pagesize,
        get_value_at, get_signature_at, signature_parts,
        get_key, get_pf, _get_pagestatus):
    """
    Factory for VALUE-controlled hash tables ('_v').
    [Empty slots are indicated by value == 0.]
    Return compiled 'is_tight(hashtable)' function.
    """
    choices = len(get_pf)
    if choices > 3:
        raise ValueError("make_is_tight currently supports only up to 3 hash functions")
    if choices == 1:  # hash is always tight for a single hash func.
        @njit( ###__signature__ (uint64[:],),  # infer return type (uint64, int64)
            nogil=True)
        def is_tight(ht):
            return (uint64(0), 0)
        return is_tight

    (get_pf1, get_pf2, get_pf3) = extend_func_tuple(get_pf, 3)
    (get_key1, get_key2, get_key3) = extend_func_tuple(get_key, 3)

    @njit( ###__signature__ (uint64[:],),  # infer return type
        nogil=True, locals=dict(
            page=uint64, slot=int64, v=uint64, sig=uint64, c=uint64, 
            f=uint64, key=uint64, p=uint64, s=int64, fill=uint64))
    def is_tight(ht):
        """return (0,0) if hash is tight, or problem (key, choice)"""
        for page in range(npages):
            for slot in range(pagesize):
                v = get_value_at(ht, page, slot)
                if v == 0: continue
                sig = get_signature_at(ht, page, slot)
                (c, f) = signature_parts(sig)
                if c == 0: continue
                if c == 1:
                    key = get_key2(page, f)
                    (p, f) = get_pf1(key)
                    (s, fill) = _get_pagestatus(ht, p, f, 0)
                    if s >= 0 or fill != pagesize:
                        return (uint64(key), 1)  # empty slot on 1st choice
                    continue  # ok
                if c == 2:
                    key = get_key3(page, f)
                    p, f = get_pf2(key)
                    (s, fill) = _get_pagestatus(ht, p, f, 1)
                    if s >= 0 or fill != pagesize:
                        return (uint64(key), 2)  # empty slot on 2nd choice
                    p, f = get_pf1(key)
                    (s, fill) = _get_pagestatus(ht, p, f, 0)
                    if s >= 0 or fill != pagesize:
                        return (uint64(key), 1)  # empty slot on 1st choice
                    continue  # ok
                return (uint64(key), 9)  # should never happen, c=0,1,2
        # all done, no problems
        return (uint64(0), 0)
    return is_tight


def make_is_tight_c(npages, pagesize,
        get_value_at, get_signature_at, signature_parts,
        get_key, get_pf, _get_pagestatus):
    """
    Factory for CHOICE-controlled hash tables ('_c').
    [Empty slots are indicated by choice == 0.]
    Return compiled 'is_tight(hashtable)' function.
    """
    choices = len(get_pf)    
    if choices != 3:
        raise ValueError("Only 3 hash functions are supported.")
    (_, get_key2, get_key3) = get_key
    (get_pf1, get_pf2, _) = get_pf

    @njit( ###__signature__ (uint64[:],),  # infer return type
        nogil=True, locals=dict(
            page=uint64, slot=int64, v=uint64, sig=uint64, c=uint64, 
            f=uint64, key=uint64, p=uint64, s=int64, fill=uint64))
    def is_tight(ht):
        """
        Return (0,0) if hash is tight, or problem (key, choice).
        In the latter case, it means that there is an empty slot
        for key 'key' on page choice 'choice', although key is
        stored at a higher choice.
        """
        for page in range(npages):
            for slot in range(pagesize):
                sig = get_signature_at(ht, page, slot)
                (c, f) = signature_parts(sig)  # should be in 0,1,2,3.
                if c <= 1: continue
                elif c == 2:
                    key = get_key2(page, f)
                    p, f = get_pf1(key)
                    (s, fill) = _get_pagestatus(ht, p, f, 1)
                    if s >= 0 or fill != pagesize:
                        return (uint64(key), 1)  # empty slot on 1st choice
                    continue
                elif c == 3:
                    key = get_key3(page, f)
                    p, f = get_pf2(key)
                    (s, fill) = _get_pagestatus(ht, p, f, 2)
                    if s >= 0 or fill != pagesize:
                        return (uint64(key), 2)  # empty slot on 2nd choice
                    p, f = get_pf1(key)
                    (s, fill) = _get_pagestatus(ht, p, f, 1)
                    if s >= 0 or fill != pagesize:
                        return (uint64(key), 1)  # empty slot on 1st choice
                    continue
                return (uint64(key), 9)  # should never happen, c=0,1,2,3.
        # all done, no problems                
        return (0, 0)
    return is_tight


## make_get_value functions  ################################

def make_get_value(pagesize, get_pf, _get_pagestatus, bits, get_luckybits_at, *, base=0):
    """
    Factory function that returns a pair of compiled functions:
    ( get_value(table, key), get_value_choice(table, key) );
    see their docstrings.
    """
    choices = len(get_pf)
    if choices < 1 or choices > 3:
        raise ValueError("Only 1 to 3 hash functions are supported.")
    (get_pf1, get_pf2, get_pf3) = extend_func_tuple(get_pf, 3)

    @njit( ###__signature__ uint64(uint64[:], uint64),
        nogil=True, locals=dict(
            key=uint64,
            page1=uint64, fpr1=uint64, slot1=int64, fill1=uint64,
            page2=uint64, fpr2=uint64, slot2=int64, fill2=uint64,
            page3=uint64, fpr3=uint64, slot3=int64, fill3=uint64,
            pagebits=uint32, check2=uint32, check3=uint32))
    def get_value(table, key):
        """
        Return uint64: the value for the given key,
        or 0 if the key is not present.
        """
        NOTFOUND = uint64(0)

        page1, fpr1 = get_pf1(key)
        (slot1, fill1) = _get_pagestatus(table, page1, fpr1, base+0)
        if slot1 >= 0: return fill1
        if fill1 < pagesize or choices <=1:
            return NOTFOUND
        # test for shortcut
        pagebits = get_luckybits_at(table, page1)  # returns all bits set if bits==0
        if not pagebits: return NOTFOUND
        check2 = pagebits & 1
        check3 = pagebits & 2 if bits >= 2 else 1

        # assert choices >= 2 (otherwise we returned above)
        if check2:
            page2, fpr2 = get_pf2(key)
            (slot2, fill2) = _get_pagestatus(table, page2, fpr2, base+1)
            if slot2 >= 0: return fill2
            if fill2 < pagesize or choices <= 2: 
                return NOTFOUND
            # test for shortcuts
            if bits != 0:
                pagebits = get_luckybits_at(table, page2)
                if bits == 1:
                    check3 = pagebits  # 1 or 0
                else:
                    check3 &= pagebits & 2

        # try the third choice only if necessary
        if choices <= 2 or not check3:
            return NOTFOUND
        page3, fpr3 = get_pf3(key)
        (slot3, fill3) = _get_pagestatus(table, page3, fpr3, base+2)
        if slot3 >= 0: return fill3
        return NOTFOUND


    @njit( ###__signature__ (uint64[:], uint64),  # infer return type (uint64, uint32)
        nogil=True, locals=dict(
            key=uint64,
            page1=uint64, fpr1=uint64, slot1=int64, fill1=uint64,
            page2=uint64, fpr2=uint64, slot2=int64, fill2=uint64,
            page3=uint64, fpr3=uint64, slot3=int64, fill3=uint64,
            pagebits=uint32, check2=uint32, check3=uint32))
    def get_value_choice(table, key):
        """
        Return (value, choice) for given key,
        where value is uint64 and choice is in {1,2,3} if key was found,
        but value==0 and choice==0 if key was not found.
        """
        NOTFOUND = (uint64(0), uint32(0))

        page1, fpr1 = get_pf1(key)
        (slot1, fill1) = _get_pagestatus(table, page1, fpr1, base+0)
        if slot1 >= 0: return (fill1, uint32(1))
        if fill1 < pagesize or choices <=1:
            return NOTFOUND
        # test for shortcut
        if bits != 0:  # this is resolved at compile time
            pagebits = get_luckybits_at(table, page1)
            if not pagebits: return NOTFOUND
        else:
            pagebits = 3
        check2 = pagebits & 1
        check3 = pagebits & 2 if bits >= 2 else 1

        # assert choices >= 2 (otherwise we returned above)
        if check2:
            page2, fpr2 = get_pf2(key)
            (slot2, fill2) = _get_pagestatus(table, page2, fpr2, base+1)
            if slot2 >= 0: return (fill2, uint32(2))
            if fill2 < pagesize or choices <= 2: 
                return NOTFOUND
            # test for shortcuts
            if bits != 0:
                pagebits = get_luckybits_at(table, page2)
                if bits == 1:
                    check3 = pagebits  # 1 or 0
                else:
                    check3 &= pagebits & 2

        # try the third choice only if necessary
        if choices <= 2 or not check3:
            return NOTFOUND
        page3, fpr3 = get_pf3(key)
        (slot3, fill3) = _get_pagestatus(table, page3, fpr3, base+2)
        if slot3 >= 0: return (fill3, uint32(3))
        return NOTFOUND

    return (get_value, get_value_choice)


# make_store_item functions #################################

def make_store_item(pagesize, get_pf, get_key_sig,
        _get_pagestatus, get_value_at, get_signature_at,
        set_value_at, set_signature_at,
        update_value, *, base=0, maxwalk=500):
    """
    Factory function that returns a compiled function
    store_item(table, key, value) -> walk_length.
    """
    choices = len(get_pf)
    if choices < 1 or choices > 3:
        raise ValueError("Only 1 to 3 hash functions are supported.")
    (get_pf1, get_pf2, get_pf3) = extend_func_tuple(get_pf, 3)
    LOCATIONS = choices * pagesize

    @njit( ###__signature__ int64(uint64[:], uint64, int64), 
        nogil=True, locals=dict(
            key=uint64, value=uint64, v=uint64,
            page1=uint64, fpr1=uint64, slot1=int64, fill1=uint64,
            page2=uint64, fpr2=uint64, slot2=int64, fill2=uint64,
            page3=uint64, fpr3=uint64, slot3=int64, fill3=uint64,
            fc=uint64, fpr=uint64, c=uint64, page=uint64,
            oldpage=uint64, lastlocation=uint64, steps=int64))
    def store_item(table, key, value):
        """
        Attempt to store given key with given value in hash table.
        Return values:
        > 0: success; number of pages visited
        < 0: failure; absolute value is number of pages visited (>=maxwalk)
        """
        oldpage = uint64(-1)
        lastlocation = uint64(-1)
        steps = 0
        while steps <= maxwalk:
            page1, fpr1 = get_pf1(key)
            if page1 != oldpage: steps += 1
            (slot1, fill1) = _get_pagestatus(table, page1, fpr1, base+0)
            if slot1 != -1:  # found on page1/choice1
                v = update_value(fill1, value)
                if v != fill1:
                    set_value_at(table, page1, slot1, v)
                return steps
            elif fill1 < pagesize:  # not found, but space available
                set_signature_at(table, page1, fill1, fpr1, base+0)
                set_value_at(table, page1, fill1, value)
                return steps
            
            if choices >= 2:
                page2, fpr2 = get_pf2(key)
                if page2 != oldpage: steps += 1
                (slot2, fill2) = _get_pagestatus(table, page2, fpr2, base+1)
                if slot2 != -1:  # found on page2/choice2
                    v = update_value(fill2, value)
                    if v != fill2: 
                        set_value_at(table, page2, slot2, v)
                    return steps
                elif fill2 < pagesize:  # not found, but space available
                    set_signature_at(table, page2, fill2, fpr2, base+1)
                    set_value_at(table, page2, fill2, value)
                    return steps
            
            if choices >= 3:
                page3, fpr3 = get_pf3(key)
                if page3 != oldpage: steps += 1
                (slot3, fill3) = _get_pagestatus(table, page3, fpr3, base+2)
                if slot3 != -1:  # found on page3/choice3
                    v = update_value(fill3, value)
                    if v != fill3:
                        set_value_at(table, page3, slot3, v)
                    return steps
                elif fill3 < pagesize:  # not found, but space available
                    set_signature_at(table, page3, fill3, fpr3, base+2)
                    set_value_at(table, page3, fill3, value)
                    return steps
            
            # We get here iff all pages are full.
            if choices <= 1:
                if steps == 0: steps = 1  # better safe than sorry
                return -steps  # only page is full: failed
            # Pick a random location; store item there and continue with evicted item.
            while True:
                location = randint(LOCATIONS)
                if location != lastlocation: break
            slot = location // choices
            c = location % choices
            if c == 0:
                page = page1; fpr = fpr1
            elif c == 1:
                page = page2; fpr = fpr2
            else:  # c == 2
                page = page3; fpr = fpr3
            xval = get_value_at(table, page, slot)
            xsig = get_signature_at(table, page, slot)
            set_signature_at(table, page, slot, fpr, base+c)
            set_value_at(table, page, slot, value)
            value = xval
            key = get_key_sig(page, xsig)
            lastlocation = location
            oldpage = page
            # loop again
        # maxwalk step exceeded; some item was kicked out :(
        return -steps
    return store_item


def make_get_key_sig(get_key, signature_parts, *, base=0):
    """
    Factory function for both VALUE- and CHOICE-controlled hashes.
    [For VALUE-controlled hashes, use base=0; for CHOICE-controlled hashes, base=1.]
    Return a compiled function 'get_key_sig(page, signature)'
    that returns the kmer code (key) given a page number and a signature.
    A signature is the pair (choice, fingerprint).
    """
    choices = len(get_key)
    if choices < 1 or choices > 3:
        raise ValueError("Only 1 to 3 hash functions are supported.")
    (get_key1, get_key2, get_key3) = extend_func_tuple(get_key, 3)

    @njit( ###__signature__ uint64(uint64, int64),
        nogil=True, locals=dict(
            page=uint64, sig=uint64, c=int64, fpr=uint64, key=uint64))
    def get_key_sig(page, sig):
        """
        Return the kmer-code (key) for a given page and signature.
        The signature 'sig' encodes both choice and fingerprint.
        """
        (c, fpr) = signature_parts(sig)
        c = c - base
        ##assert 0 <= c < choices 
        if c == 0:
            key = get_key1(page, fpr)
        elif c == 1:
            key = get_key2(page, fpr)
        elif c == 2:
            key = get_key3(page, fpr)
        else:
            key = uint64(-1)
        return key
    return get_key_sig


def make_get_key_choice_sig(get_key, signature_parts, *, base=0):
    """
    Factory function for both VALUE- and CHOICE-controlled hashes.
    [For VALUE-controlled hashes, use base=0; for CHOICE-controlled hashes, base=1.]
    Return a compiled function 'get_key_sig(page, signature)'
    that returns the kmer code (key) given a page number and a signature.
    A signature is the pair (choice, fingerprint).
    """    
    choices = len(get_key)
    if choices < 1 or choices > 3:
        raise ValueError("Only 1 to 3 hash functions are supported.")
    (get_key1, get_key2, get_key3) = extend_func_tuple(get_key, 3)

    @njit( ###__signature__ (uint64, uint64),  # infer return type (uint64, int64)
            nogil=True, locals=dict(
                page=uint64, sig=uint64, c=int64, fpr=uint64, key=uint64))
    def get_key_choice_sig(page, sig):
        """
        Return pair (key, choice) for the given page and signature,
        where choice is in {0,1,2} or -1 when empty.
        """
        (c, fpr) = signature_parts(sig)
        c = c - base
        ##assert 0 <= c < choices 
        if c == 0:
            key = get_key1(page, fpr)
        elif c == 1:
            key = get_key2(page, fpr)
        elif c == 2:
            key = get_key3(page, fpr)
        else:
            key = uint64(-1)
        return (key, c)
    return get_key_choice_sig

# define get_occupancy builders  ###################################

def make_get_occupancy_v(choices, npages, pagesize, nvalues, luckybits, 
    get_value_at, get_signature_at, signature_parts, get_luckybits_at):
    """
    Factory function for VALUE-controlled hashes ("_v").
    [Empty slots are indicated by value == 0.]
    Return a compiled function 'get_occupancy(table)' that returns
    a triple of histogram arrays: (valuehist, fillhist, chiocehist), all int64[:].
    """

    @njit( ###__signature__ (uint64[:],),  # infer return type (int64[:],int64[:],int64[:])
        nogil=True, locals=dict(
            page=uint64, last=int64, slot=int64, x=uint64, c=uint64, v=uint64))
    def get_occupancy(table):
        """
        Return a triple of arrays (valuehist, fillhist, choicehist),
        where valuehist[v] is the number of items with value v,
        fillhist[i] is the number of pages with i items filled,
        choicehist[i] is the number of slots with choice i.
        """
        valuehist = np.zeros(nvalues, dtype=np.int64)
        fillhist = np.zeros(pagesize+1, dtype=np.int64)
        choicehist = np.zeros(choices+1, dtype=np.int64)
        lbhist = np.zeros(4, dtype=np.int64)
        for page in range(npages):
            last = -1
            if luckybits != 0:
                lbhist[get_luckybits_at(table, page)] += 1
            for slot in range(pagesize):
                v = get_value_at(table, page, slot)
                valuehist[v] += 1
                if v == 0:
                    c = 0
                else:
                    last = slot
                    sig = get_signature_at(table, page, slot)
                    c = 1 + signature_parts(sig)[0]  # 1+ is correct!
                choicehist[c] += 1
            fillhist[last+1] += 1
        return (valuehist, fillhist, choicehist, lbhist)
    return get_occupancy

def make_get_occupancy_c(choices, npages, pagesize, nvalues, luckybits,
    get_value_at, get_signature_at, signature_parts, get_luckybits_at):
    """
    Factory function for CHOICE-controlled hashes ("_c").
    [Empty slots are indicated by choice == 0.]
    Return a compiled function 'get_occupancy(table)' that returns
    a triple of histogram arrays: (valuehist, fillhist, chiocehist), all int64[:].
    """
    @njit( ###__signature__ (uint64[:],),  # infer return type (int64[:],int64[:],int64[:])
        nogil=True, locals=dict(
            page=uint64, last=int64, slot=int64, x=uint64, c=uint64, v=uint64))
    def get_occupancy(table):
        """
        Return a triple of arrays (valuehist, fillhist, choicehist),
        where valuehist[v] is the number of items with value v,
        fillhist[i] is the number of pages with i items filled,
        choicehist[i] is the number of slots with choice i.
        """
        valuehist = np.zeros(nvalues, dtype=np.int64)
        fillhist = np.zeros(pagesize+1, dtype=np.int64)
        choicehist = np.zeros(choices+1, dtype=np.int64)
        lbhist = np.zeros(4, dtype=np.int64)
        for page in range(npages):
            last = -1
            if luckybits != 0:
                lbhist[get_luckybits_at(table, page)] += 1
            for slot in range(pagesize):
                sig = get_signature_at(table, page, slot)
                c = signature_parts(sig)[0]  # no +1 !
                choicehist[c] += 1
                if c != 0:
                    last = slot
                    v = get_value_at(table, page, slot)
                    valuehist[v] += 1
            fillhist[last+1] += 1
        return (valuehist, fillhist, choicehist, lbhist)
    return get_occupancy

