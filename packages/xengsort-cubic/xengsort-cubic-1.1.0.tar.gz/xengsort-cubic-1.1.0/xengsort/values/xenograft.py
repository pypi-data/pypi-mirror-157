"""
xengsort.values.xenograft

0 = 00 = weak
1 = 01 = host
2 = 10 = graft
3 = 11 = both
"""

from collections import namedtuple

import numpy as np
from numba import njit, uint64, int64, boolean

ValueInfo = namedtuple("ValueInfo", [
    "NVALUES",
    "RCMODE",
    "get_value_from_name_host",
    "get_value_from_name_graft",
    "update",
    "is_compatible",
    "bits",
    ])


def initialize(bits, rcmode="max"):
    nvalues = 2** int(bits)

    def get_value_from_name_host(name, onetwo=1):
        return 1
        
    def get_value_from_name_graft(name, onetwo=1):
        return 2 

    @njit( ###__signature__ uint64(uint64, uint64),
        nogil=True, locals=dict(
            old=uint64, new=uint64))
    def update(old, new):
        """
        update(uint64, uint64) -> uint64
        Update old value (stored) with a new value (from current seq.).
        Return upated value.
        """
        
        if bits == 2:
            if new == 0:
                return 0
            else:
                return old | new
        else:
            if new == 0:
                return old | 4
            else:
                return old | new
    
    @njit( ###__signature__ boolean(uint64, uint64),
        nogil=True, locals=dict(observed=uint64, stored=uint64))
    def is_compatible(observed, stored):
        assert observed != 0
        assert stored != 0
        return (observed & stored > 0)
        return (stored < 4)

    return ValueInfo(
        NVALUES = nvalues,
        RCMODE = rcmode,
        get_value_from_name_host = get_value_from_name_host,
        get_value_from_name_graft = get_value_from_name_graft,
        update = update,
        is_compatible = is_compatible,
        bits = bits
        )

