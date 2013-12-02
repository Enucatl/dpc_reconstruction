#!/usr/bin/env python
# encoding: utf-8
"""Convert each folder with raw images to an hdf5 dataset."""

from __future__ import division, print_function

import os
from glob import glob

import logging
import logging.config
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()

import pypes.pipeline

from dpc_reconstruction.networks.fliccd2hdf5 import fliccd2hdf5_factory
from dpc_reconstruction.version import get_git_version
from dpc_reconstruction.commandline_parsers.basic import BasicParser

description = "{1}\n\n{0}\n".format(get_git_version(), __doc__)
commandline_parser = BasicParser(description=description)
commandline_parser.add_argument('folder',
        metavar='FOLDER(s)',
        nargs='+',
        help='''folder(s) with the raw files. If you pass multiple
        folders you will get one hdf5 file for each folder.''')
commandline_parser.add_argument('--remove', '-r',
        action='store_true',
        help='remove the folder after converting the files.')

def main(folders, overwrite=False, jobs=1, remove_source=False):
    network = fliccd2hdf5_factory(overwrite, remove_source)
    pipeline = pypes.pipeline.Dataflow(network, n=jobs)
    for folder in folders:
        if not os.path.exists(folder) or not os.path.isdir(folder):
            log.error("{0}: folder {1} not found!".format(
                __name__, folder))
            raise OSError
        file_names = sorted(glob(os.path.join(folder, "*.raw")))
        log.debug("{0} {1}: converting {2} raw files.".format(
            __name__, get_git_version(), len(file_names)))
        for file_name in file_names:
            pipeline.send(file_name)
    pipeline.close()
            
if __name__ == '__main__':
    import sys
    args = commandline_parser.parse_args()
    if args.verbose:
        config_dictionary['handlers']['default']['level'] = 'DEBUG'
        config_dictionary['loggers']['']['level'] = 'DEBUG'
    logging.config.dictConfig(config_dictionary)
    main(args.folder, args.overwrite, args.jobs, args.remove)
