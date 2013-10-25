"""
Read the RAW images saved by the CCDFLI camera and merge them into a single
HDF5 file.
"""

from __future__ import division, print_function

import os
from glob import glob
from itertools import islice

import h5py
import numpy as np

from dpc_reconstruction.progress_bar import progress_bar

#number of lines in a CCD FLI header
_HEADER_LINES = 16

def _analyse_header(input_file_name):
    """Analyse a CCD FLI header in a RAW file

    Return the bytes in the header, exposure, min_x, max_x, min_y, max_y.

    """
    input_file = open(input_file_name, 'rb')
    header = list(islice(input_file, _HEADER_LINES))
    header_len = len("".join(header))
    exposure_time = float(header[4].split()[-1])
    min_y, min_x, max_y, max_x = [
            int(x) for x in header[-2].split()[2:]]
    input_file.close()
    return header_len, exposure_time, min_x, max_x, min_y, max_y

def _read_data(input_file_name):
    """Read a single image into a numpy array,
    shaped according to the header."""
    (header_len, _,
                    min_x, max_x, 
                    min_y, max_y) = _analyse_header(input_file_name)
    input_file = open(input_file_name, 'rb')
    input_file.read(header_len + 1)
    image = np.reshape(
            np.fromfile(input_file, dtype=np.uint16),
            (max_y - min_y, max_x - min_x),
            order='FORTRAN')
    input_file.close()
    return image

def raw_folder_to_hdf5(folder_name, output_name):
    """Convert a folder with RAW files to a single hdf5 file.
    
    """
    if not os.path.isdir(folder_name):
        error = "make_hdf5.py: not a folder: " + folder_name
        raise OSError(error)
    print("make_hdf5.py: converting", folder_name)
    files = sorted(glob(os.path.join(folder_name, "*.raw")))
    output_file = h5py.File(output_name, 'w')
    n_files = len(files)
    for i, input_file_name in enumerate(files):
        print(progress_bar((i + 1) / n_files), end="\r")
        if i == 0:
            #create dataset with the size of the first image
            (_, exposure_time,
                    min_x, max_x, 
                    min_y, max_y) = _analyse_header(input_file_name)
            dataset = output_file.create_dataset("raw_images", 
                    (max_y - min_y,
                    max_x - min_x,
                    len(files)),
                    dtype=np.uint16)
            dataset.attrs['exposure_time'] = exposure_time
            dataset.attrs['min_x'] = min_x
            dataset.attrs['min_y'] = min_y
            dataset.attrs['max_x'] = max_x
            dataset.attrs['max_y'] = max_y
        dataset[:, :, i] = _read_data(input_file_name)
    output_file.close()
    print()
    print("make_hdf5.py: written", output_name)
    print("make_hdf5.py: done!")
    return output_name
