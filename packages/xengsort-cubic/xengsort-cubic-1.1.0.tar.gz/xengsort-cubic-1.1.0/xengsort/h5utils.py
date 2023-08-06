"""
h5utils.py:
utilities for dealing with HDF5 files that store a k-mer index
"""

from collections import defaultdict
import pickle
import numpy as np
import h5py


def guess_q(path, q=None):
    """
    for the hdf5 file at the given path,
    find the group with maximum q and return that value of q.
    Return None if nothing was found.
    """
    if q is not None:
        return q
    with h5py.File(path, 'r') as f:
        for q in range(31, 0, -1):
            testname = "x"*q + '-'
            if testname in f:
                return q
    return None


def guess_group(path, q, group=None):
    """
    for the hdf5 file at the given path and the given q,
    find the given or first named group with counts.
    Return the hdf5 group object.
    Return None if nothing was found.
    """
    if group is not None:
        return group
    shape = "x"*q + '-'  # the final '-' is for canonical codes
    with h5py.File(path, 'r') as f:
        for grp in f[shape]:
            return grp
    return None


def guess_only_group(path, suffix=None, error=True):
    """
    for the hdf5 file at the given path,
    check whether a single group (with the given suffix) exists
    and return the group name.
    If no group is found return None, or throw an error if error=True.
    """
    with h5py.File(path, 'r') as f:
        groups = list()
        for grp in f:
            if suffix is not None:
                if not grp.endswith(suffix): continue
            groups.append(grp)
    if len(groups) == 1:
        return groups[0]
    if error:
        raise RuntimeError(f"found {len(groups)} groups in '{path}'")
    return None


def common_datasets(paths):
    """
    Given a list of HDF5 file paths,
    return a list of datasets that occur in all of these files
    """
    datasets = defaultdict(list)
    for inputfile in paths:
        def _collect_datasets(name, node):
            if isinstance(node, h5py.Dataset):
                datasets[name].append(inputfile)
        with h5py.File(inputfile, 'r') as fin:
            fin.visititems(_collect_datasets)
    ninput = len(paths)
    D = [name for name, inputfiles in datasets.items() if len(inputfiles)==ninput]
    return D


## saving and loading to HDF5 groups with auto-pickling (names with suffix '!p') #

def save_to_h5group(path, group, **kwargs):
    with h5py.File(path, 'a', libver='latest') as f:
        g = f.require_group(group)
        for name, data in kwargs.items():
            if isinstance(data, (list, tuple, dict)):
                name = name + '!p'
                data = np.frombuffer(pickle.dumps(data), dtype=np.uint8)
            if name in g: del g[name]
            g.create_dataset(name, data=data)


def load_from_h5group(path, group, names=None):
    """
    Load all datasets from a group in a HDF5 file.
    Return them as a dict {name: data}.
    If names is not None, but an iterable of strings,
    ensure that all given names exist as keys;
    otherwise raise a KeyError.
    (The returned dict may contain more than the given names,
    but it will be checked that the given names are keys of the dict.)
    """
    results = dict()
    with h5py.File(path, 'r') as f:
        g = f[group]
        for name, data in g.items():
            if (names is not None) and (name not in names):
                continue
            if name.endswith('!p'):
                results[name[:-2]] = pickle.loads(data[:])
            else:
                dims = len(data.shape)
                if dims > 0:
                    results[name] = data[:]
                else:
                    results[name] = data[()]
    if names is not None:
        for name in names:
            if name.endswith('!p'):
                name = name[:-2]
            if name not in results:
                raise KeyError(f"did not get dataset '{name}'' from {path}/{group}")
    return results


def get_h5_dataset(path, dataset):
    with h5py.File(path, 'r') as f:
        d = f[dataset]
    return d


