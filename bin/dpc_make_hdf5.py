#!/usr/bin/env python
# encoding: utf-8
"""Convert each folder with raw images to an hdf5 dataset."""

from __future__ import division, print_function

import argparse
import os

import ruffus

from dpc_reconstruction.io.fliccd_hedpc import raw_folder_to_hdf5

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
    output_files = [os.path.normpath(f) + ".hdf5"
            for f in args.folder]
    target = ruffus.files(zip(args.folder, output_files))(raw_folder_to_hdf5)
    if args.overwrite:
        force_run = [target]
    else:
        force_run = []
    ruffus.pipeline_run([target],
            forcedtorun_tasks=force_run, one_second_per_job=False,
            multiprocess=args.jobs, verbose=5)

if __name__ == '__main__':
    main(commandline_parser.parse_args())
