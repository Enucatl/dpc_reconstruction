#!/usr/bin/env python
# encoding: utf-8
"""Reconstruct the DPC signals with multiple flats take every flats_every
scans"""

from __future__ import division, print_function

import logging
import logging.config
import dpc_reconstruction
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()

import pypes.pipeline

from pypes.component import HigherOrderComponent
from dpc_reconstruction.commandline_parsers.basic import BasicParser
from pypes.plugins.hdf5 import Hdf5Writer
import dpc_reconstruction.networks.flats_every as fe

description = "{1}\n\n{0}\n".format(dpc_reconstruction.__version__, __doc__)
commandline_parser = BasicParser(description=description)
commandline_parser.add_argument('files',
                                metavar='FILE(s)',
                                nargs='+',
                                help='''file(s) with the images''')
commandline_parser.add_argument('--steps', '-s',
                                nargs='?', default=1, type=int,
                                help='number of phase steps')
commandline_parser.add_argument('--flats_every',
                                nargs='?', default=1, type=int,
                                help='flats every this many scans')
commandline_parser.add_argument('--n_flats',
                                nargs='?', default=5, type=int,
                                help='''flats to average every time a flat
                                is taken''')


def main(files, flats_every, n_flats, phase_steps,
         overwrite=False, jobs=1):
    """show on screen if not batch"""
    fe_network = fe.flats_every_network_factory(files,
                                                flats_every,
                                                n_flats, phase_steps)
    fe_analyzer = HigherOrderComponent(fe_network)
    file_writer = Hdf5Writer()
    file_writer.set_parameter("group", "postprocessing")
    file_writer.set_parameter("overwrite", overwrite)
    network = {
        fe_analyzer: {
            file_writer: ("out", "in")
        },
    }
    pipeline = pypes.pipeline.Dataflow(network, n=jobs)
    log.debug("{0} {1}: analyzing {2} hdf5 files.".format(
        __name__, dpc_reconstruction.__version__, len(files)))
    pipeline.send(None)
    pipeline.close()

if __name__ == '__main__':
    args = commandline_parser.parse_args()
    if args.verbose:
        config_dictionary['handlers']['default']['level'] = 'DEBUG'
        config_dictionary['loggers']['']['level'] = 'DEBUG'
    logging.config.dictConfig(config_dictionary)
    main(args.files, args.flats_every, args.n_flats,
         args.steps, args.overwrite, args.jobs)
