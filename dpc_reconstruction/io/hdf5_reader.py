import h5py
import numpy as np


def read_group(filename, group):
    input_file = h5py.File(filename)
    datasets = [
        dataset[...]
        for dataset in input_file[group].values()
        if isinstance(dataset, h5py.Dataset)
    ]
    return np.stack(datasets, axis=1)
