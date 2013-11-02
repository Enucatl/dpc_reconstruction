#!/usr/bin/env python
# encoding: utf-8
"""Convert each folder with raw images to an hdf5 dataset."""

from __future__ import division, print_function

import os
import argparse
from glob import glob

import pypes.pipeline

from dpc_reconstruction.io.file_reader import FileReader
from dpc_reconstruction.io.fliccd_hedpc import FliRawReader
from dpc_reconstruction.io.fliccd_hedpc import FliRawHeaderAnalyzer
from dpc_reconstruction.io.fliccd_hedpc import FliRaw2Numpy
from dpc_reconstruction.io.hdf5 import Hdf5Writer

commandline_parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

commandline_parser.add_argument('folder',
        metavar='FOLDER(s)',
        nargs='+',
        help='''folder(s) with the raw files. If you pass multiple
        folders you will get one hdf5 file for each folder.''')
commandline_parser.add_argument('--overwrite', '-o',
        action='store_true',
        help='overwrite hdf5 files if they already exist.')
commandline_parser.add_argument('--jobs', '-j',
        nargs='?', default=1, type=int,
        help='specifies the number of jobs running simultaneously.')

def main(folders, overwrite=False, jobs=1):
    file_reader = FileReader()
    fliraw_reader = FliRawReader()
    header_analyzer = FliRawHeaderAnalyzer()
    numpy_converter = FliRaw2Numpy()
    hdf_writer = Hdf5Writer()
    hdf_writer.set_parameter("overwrite", overwrite)
    FliRawReader.__metatype__ = "TRANSFORMER"
    network = {
            file_reader: {
                fliraw_reader: ('out', 'in'),
                },
            fliraw_reader: {
                header_analyzer: ('out', 'in'),
                },
            header_analyzer: {
                numpy_converter: ('out', 'in'),
                },
            numpy_converter: {
                hdf_writer: ('out', 'in'),
                },
            }
    pipeline = pypes.pipeline.Dataflow(network, n=jobs)
    for folder in folders:
        file_names = sorted(glob(os.path.join(folder, "*.raw")))
        for file_name in file_names:
            pipeline.send(file_name)
    pipeline.close()
            
if __name__ == '__main__':
    import sys
    import logging
    import logging.config
    from dpc_reconstruction.logger_config import config_dictionary
    root_logger = logging.getLogger()
    logging.config.dictConfig(config_dictionary)
    args = commandline_parser.parse_args()
    main(args.folder, args.overwrite, args.jobs)
