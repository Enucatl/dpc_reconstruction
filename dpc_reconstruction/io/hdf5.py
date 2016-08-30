import os
import h5py
import numpy as np


def read_group(filename, group, drop_last_dataset=False):
    input_file = h5py.File(filename)
    datasets = [
        dataset[...]
        for dataset in input_file[group].values()
        if isinstance(dataset, h5py.Dataset)
    ]
    if drop_last_dataset:
        datasets = datasets[:-1]
    return np.stack(datasets, axis=-1)


def output_name(files):
    """
    Get the name of the output hdf5 file from a list of input files.

    """
    first_file_name, _ = os.path.splitext(os.path.basename(files[0]))
    last_file_name = os.path.splitext(os.path.basename(files[-1]))[0]
    extension = os.path.splitext(os.path.basename(files[-1]))[1]
    dir_name = os.path.dirname(files[0])
    if len(files) > 1:
        file_name = os.path.join(
            dir_name, "{0}_{1}{2}".format(
                first_file_name,
                last_file_name,
                extension))
    else:
        file_name = os.path.join(
            dir_name, "{0}{1}".format(
                first_file_name,
                extension))
    return file_name
