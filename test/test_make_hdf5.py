"""Test the make_hdf5.py script.

"""

import h5py
import os
from glob import glob
import numpy as np
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../bin")))

from dpc_make_hdf5 import main
from itertools import islice

FOLDER = ["fliccd_data"]
PROGRAMME = "dpc_make_hdf5.py"
OUTPUT_FILE = FOLDER[0] + ".hdf5"

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
            order='F')
    input_file.close()
    return image

class TestMakeHdf5(object):
    """Tests:
        - header analysis
        - file creation
        - file content
        - overwrite flag.
        
        """

    def test_file_content(self):
        """Test that the file contains the same data as the original raw
        file.

        """
        main(FOLDER, overwrite=True)
        h5_file = h5py.File(OUTPUT_FILE, "r")
        for i, input_file_name in enumerate(
                sorted(glob("fliccd_data/*.raw"))):
            image = _read_data(input_file_name)
            key = os.path.splitext(
                    os.path.basename(
                        input_file_name))[0]
            hdf5_data = h5_file[key][...]
            print(i, input_file_name, key)
            print(hdf5_data.shape, image.shape)
            assert hdf5_data.shape == image.shape
            #assert header_len == 340
            #assert exposure_time == 5
            #assert min_x == 4
            #assert max_x == 1028
            #assert min_y == 500
            #assert max_y == 560
            assert (hdf5_data[0, :] == image[0, :]).all()
            assert (hdf5_data == image).all()
        h5_file.close()
    
    def test_overwrite(self):
        """Test the overwrite flag.

        """
        main(FOLDER, overwrite=True)
        date_created = os.path.getmtime(OUTPUT_FILE)
        main(FOLDER)
        date_created2 = os.path.getmtime(OUTPUT_FILE)
        """Check that it was not overwritten."""
        assert date_created <= date_created2
        """Check that it was overwritten."""
        main(FOLDER, overwrite=True)
        date_created3 = os.path.getctime(OUTPUT_FILE)
        assert date_created3 > date_created
