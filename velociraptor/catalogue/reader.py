"""
Main objects for the velociraptor reading library.

This is based upon the reading routines in the SWIFTsimIO library.
"""

import h5py
import re
import numpy as np


class VelociraptorCatalogueReader(object):
    def __init__(self, filename):
        with h5py.File(filename, "r") as handle:
            num_files = handle["Num_of_files"][0]
        if num_files == 1:
            self.filenames = [filename]
        else:
            basename = re.match("(\S+properties)\.\d+\Z", filename).groups()[0]
            self.filenames = [f"{basename}.{idx}" for idx in range(num_files)]

    def read_field(self, field):
        if len(self.filenames) == 1:
            with h5py.File(self.filenames[0], "r") as handle:
                try:
                    value = handle[field][...]
                except KeyError:
                    print(f"Could not read {field}")
                    return None
            return value
        else:
            # figure out the shape and dtype of the return value
            dtype = None
            shape = None
            for filename in self.filenames:
                with h5py.File(filename, "r") as handle:
                    try:
                        ds = handle[field]
                    except KeyError:
                        print(f"Could not read {field}")
                        return None
                    if dtype is None:
                        dtype = ds.dtype
                        shape = ds.shape
                    else:
                        shape[0] += ds.shape[0]

            # create an empty array to store the return value
            value = np.zeros(shape, dtype=dtype)
            # now read the data (no need to check for existence again)
            offset = 0
            for filename in self.filenames:
                with h5py.File(filename, "r") as handle:
                    size = handle[field].shape[0]
                    value[offset : offset + size] = handle[field][...]
                    offset += size
            return value
