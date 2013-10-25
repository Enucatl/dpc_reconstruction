"""Test the make_hdf5.py script.

"""

import h5py
import os
from glob import glob

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../bin")))

import dpc_reconstruction.io.fliccd_hedpc as make_hdf5
from dpc_make_hdf5 import main, commandline_parser
from subprocess import check_call

FOLDER = "fliccd_data"
PROGRAMME = "dpc_make_hdf5.py"
OUTPUT_FILE = FOLDER + ".hdf5"

class TestMakeHdf5(object):
    """Tests:
        - header analysis
        - file creation
        - file content
        - overwrite flag.
        
        """

    def test_header(self):
        """Test the header analysis of a known file.

        """
        (header_len, exposure_time,
                min_x, max_x, 
                min_y, max_y) = make_hdf5._analyse_header(
                        "fliccd_data/ccdimage_00045_00000_00.raw")
        assert header_len == 340
        assert exposure_time == 5
        assert min_x == 4
        assert max_x == 1028
        assert min_y == 500
        assert max_y == 560

    def test_main(self):
        """Test that the file is written,
        and that it contains the same number of images as
        the input folder.

        """
        args = commandline_parser.parse_args(
                ["--overwrite", "fliccd_data"])
        main(args)
        assert os.path.exists(OUTPUT_FILE)
        h5_file = h5py.File(OUTPUT_FILE, "r")
        assert "raw_images" in h5_file
        folder_name = OUTPUT_FILE.replace(".hdf5", "")
        n_original_files = len(glob(os.path.join(folder_name, "*.raw"))) 
        n_hdf5_images = h5_file["raw_images"].shape[2]
        assert n_original_files == n_hdf5_images
        h5_file.close()

    def test_file_content(self):
        """Test that the file contains the same data as the original raw
        file.

        """
        h5_file = h5py.File(OUTPUT_FILE, "r")
        for i, input_file_name in enumerate(
                sorted(glob("fliccd_data/*.raw"))):
            image = make_hdf5._read_data(input_file_name)
            check_call([PROGRAMME, "--overwrite", FOLDER])
            hdf5_data = h5_file["raw_images"][:, :, i]
            print(i, input_file_name)
            assert (hdf5_data == image).all()
        h5_file.close()
    
    def test_overwrite(self):
        """Test the overwrite flag.

        """
        check_call([PROGRAMME, "--overwrite", FOLDER])
        date_created = os.path.getctime(OUTPUT_FILE)
        check_call([PROGRAMME, FOLDER])
        date_created2 = os.path.getctime(OUTPUT_FILE)
        """Check that it was not overwritten."""
        assert date_created == date_created2
        """Check that it was overwritten."""
        check_call([PROGRAMME, "--overwrite", FOLDER])
        date_created3 = os.path.getctime(OUTPUT_FILE)
        assert date_created3 >= date_created
