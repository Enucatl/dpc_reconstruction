#!/usr/bin/env python
# encoding: utf-8
"""Reconstruct the DPC signals from sample and flat datasets"""

from __future__ import division, print_function

import logging
import logging.config
import dpc_reconstruction
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()

import pypes.pipeline
import pypes.packet

from pypes.component import HigherOrderComponent
from dpc_reconstruction.commandline_parsers.basic import BasicParser
from pypes.plugins.hdf5 import Hdf5Writer
import dpc_reconstruction.networks.fourier_analysis as fca

description = "{1}\n\n{0}\n".format(dpc_reconstruction.__version__, __doc__)
commandline_parser = BasicParser(description=description)
commandline_parser.add_argument('files',
                                metavar='FILE(s)',
                                nargs='+',
                                help='''file(s) with the images''')
commandline_parser.add_argument('--flat',
                                metavar='FLATS(s)',
                                nargs='+',
                                help='''file(s) with the flat images''')
commandline_parser.add_argument('--steps', '-s',
                                nargs='?', default=1, type=int,
                                help='number of phase steps')


def main(file_names, flat_file_names, phase_steps,
         overwrite=False, jobs=1):
    """show on screen if not batch"""
    packet = pypes.packet.Packet()
    packet.set('sample', file_names)
    packet.set('flat', flat_file_names)
    fca_network = fca.fourier_analysis_network_factory(phase_steps)
    fca_analyzer = HigherOrderComponent(fca_network)
    fca_analyzer.__metatype__ = "ADAPTER"
    file_writer = Hdf5Writer()
    file_writer.set_parameter("group", "postprocessing")
    file_writer.set_parameter("overwrite", overwrite)
    network = {
        fca_analyzer: {
            file_writer: ("out", "in")
        },
    }
    pipeline = pypes.pipeline.Dataflow(network, n=jobs)
    log.debug("{0} {1}: analyzing {2} hdf5 files.".format(
        __name__, dpc_reconstruction.__version__, len(file_names)))
    pipeline.send(packet)
    pipeline.close()

if __name__ == '__main__':
    args = commandline_parser.parse_args()
    if args.verbose:
        config_dictionary['handlers']['default']['level'] = 'DEBUG'
        config_dictionary['loggers']['']['level'] = 'DEBUG'
    logging.config.dictConfig(config_dictionary)
    main(args.files, args.flat, args.steps,
         args.overwrite, args.jobs)
