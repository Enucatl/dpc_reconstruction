#!/usr/bin/env python
# encoding: utf-8
"""Calculate the visibility."""

from __future__ import division, print_function

import os

import logging
import logging.config
import dpc_reconstruction
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()

import pypes.pipeline
import pypes.packet

from dpc_reconstruction.networks.visibility import visibility_factory
from dpc_reconstruction.commandline_parsers.basic import BasicParser

description = "{1}\n\n{0}\n".format(dpc_reconstruction.__version__, __doc__)
commandline_parser = BasicParser(description=description)
commandline_parser.add_argument('files',
                                metavar='FILE(s)',
                                nargs='+',
                                help='''file(s) with the images''')


def main(file_names, overwrite=False, jobs=1,
         batch=True):
    """show on screen if not batch"""
    network = visibility_factory(overwrite, batch)
    pipeline = pypes.pipeline.Dataflow(network, n=jobs)
    log.debug("{0} {1}: analyzing {2} hdf5 files.".format(
        __name__, dpc_reconstruction.__version__, len(file_names)))
    for file_name in file_names:
        if not os.path.exists(file_name) or not os.path.isfile(file_name):
            log.error("{0}: file {1} not found!".format(
                __name__, file_name))
            raise OSError
        packet = pypes.packet.Packet()
        packet.set("file_name", file_name)
        packet.set("data", "raw_images")
        pipeline.send(packet)
    pipeline.close()

if __name__ == '__main__':
    args = commandline_parser.parse_args()
    if args.verbose:
        config_dictionary['handlers']['default']['level'] = 'DEBUG'
        config_dictionary['loggers']['']['level'] = 'DEBUG'
    logging.config.dictConfig(config_dictionary)
    main(args.files, args.overwrite,
         args.jobs, args.batch)
