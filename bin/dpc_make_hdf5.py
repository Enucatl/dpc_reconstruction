#!/usr/bin/env python
# encoding: utf-8
"""Convert each folder with raw images to an hdf5 dataset."""

from __future__ import division, print_function

import os
import argparse
import requests
from glob import glob
import StringIO
import gzip

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
        file_names = sorted(glob(os.path.join(folder, "*.raw")))
        server = "http://localhost:5000/data"
        for file_name in file_names:
            raw_image = open(file_name, 'rb')
            headers = {'content-encoding': 'gzip'}
            stringio = StringIO.StringIO()
            gzip_file = gzip.GzipFile(fileobj=stringio, mode='w')
            gzip_file.write(os.path.abspath(file_name))
            gzip_file.write("\n")
            gzip_file.write(raw_image.read())
            gzip_file.close()
            requests.post(server,
                    data=stringio.getvalue(),
                    headers=headers)

if __name__ == '__main__':
    main(commandline_parser.parse_args())
