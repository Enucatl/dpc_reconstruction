#!/usr/bin/env python
# encoding: utf-8
"""Convert each folder with raw images to an hdf5 dataset."""

from __future__ import division, print_function

import os
from glob import glob

import logging
import logging.config
import dpc_reconstruction
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()

import pypes.pipeline

from dpc_reconstruction.io.file_reader import FileReader
from dpc_reconstruction.io.mythen import MythenToNumpy
from pypes.plugins.hdf5 import Hdf5Writer
from dpc_reconstruction.io.fliccd_hedpc import FileName2DatasetName

from dpc_reconstruction.commandline_parsers.basic import BasicParser

description = "{1}\n\n{0}\n".format(dpc_reconstruction.__version__, __doc__)
commandline_parser = BasicParser(description=description)
commandline_parser.add_argument('folder',
                                metavar='FOLDER(s)',
                                nargs='+',
                                help='''folder(s) with the raw files. If you
                                pass multiple folders you will get one hdf5
                                file for each folder.''')
commandline_parser.add_argument('--remove', '-r',
                                action='store_true',
                                help='''remove the folder after converting the
                                files.''')


def main(folders, overwrite=False, remove=False, jobs=1):
    file_reader = FileReader()
    file_reader.set_parameter("mode", "r")
    file_reader.set_parameter("remove_source", remove)
    mythen_to_numpy = MythenToNumpy()
    hdf_writer = Hdf5Writer()
    hdf_writer.set_parameter("group", "raw_images")
    file_name = FileName2DatasetName()
    hdf_writer.set_parameter("overwrite", overwrite)
    network = {
        file_reader: {
            mythen_to_numpy: ('out', 'in')
        },
        mythen_to_numpy: {
            file_name: ('out', 'in')
        },
        file_name: {
            hdf_writer: ('out', 'in')
        }
    }
    pipeline = pypes.pipeline.Dataflow(network, n=jobs)
    for folder in folders:
        if not os.path.exists(folder) or not os.path.isdir(folder):
            log.error("{0}: folder {1} not found!".format(
                __name__, folder))
            pipeline.close()
            raise OSError
        file_names = sorted(glob(os.path.join(folder, "*.raw")))
        log.debug("{0} {1}: converting {2} raw files.".format(
            __name__, dpc_reconstruction.__version__, len(file_names)))
        for file_name in file_names:
            pipeline.send(file_name)
    pipeline.close()

if __name__ == '__main__':
    args = commandline_parser.parse_args()
    if args.verbose:
        config_dictionary['handlers']['default']['level'] = 'DEBUG'
        config_dictionary['loggers']['']['level'] = 'DEBUG'
    logging.config.dictConfig(config_dictionary)
    main(args.folder, args.overwrite, args.remove, args.jobs)
