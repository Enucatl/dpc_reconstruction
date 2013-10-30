#!/usr/bin/env python
# encoding: utf-8
"""Convert each folder with raw images to an hdf5 dataset."""

from __future__ import division, print_function

import argparse
import os
from glob import glob

from pypes.pipeline import Dataflow
from pypesvds.plugins.mergeoperator.mergeoperator import Merge

from dpc_reconstruction.io.fliccd_hedpc import FliRawHeaderSplitter
from dpc_reconstruction.io.fliccd_hedpc import FliRawHeaderAnalyzer
from dpc_reconstruction.io.fliccd_hedpc import FliRaw2Numpy
from dpc_reconstruction.io.fliccd_hedpc import Printer
from dpc_reconstruction.io.hdf5 import Hdf5Publisher

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

def main(args):
    for folder in args.folder:
        files = sorted(glob(os.path.join(folder, "*.raw")))
        files = [open(file_name) for file_name in files]
        header_splitter = FliRawHeaderSplitter(files)
        header_analyzer = FliRawHeaderAnalyzer()
        merger = Merge()
        raw2numpy = FliRaw2Numpy()
        printer = Printer()
        hdf5publisher = Hdf5Publisher(args.overwrite)
        network = {
                header_splitter: {
                    header_analyzer: ('header', 'in'),
                    merger: ('out', 'in'),
                    },
                header_analyzer: {
                    merger: ('out', 'in2'),
                    },
                merger: {
                    raw2numpy: ('out', 'in'),
                    },
                raw2numpy: {
                    hdf5publisher: ('out', 'in')
                    },
                }
        pipe = Dataflow(network)
        pipe.send(None)
        pipe.close()

if __name__ == '__main__':
    main(commandline_parser.parse_args())
