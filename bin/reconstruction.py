#!/usr/bin/env python
# encoding: utf-8
"""Reconstruct the DPC signals from sample and flat datasets"""

from __future__ import division, print_function

import os
import argparse

import logging
import logging.config
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()

import pypes.pipeline
import pypesvds.lib.packet

from dpc_reconstruction.io.hdf5 import Hdf5Reader
from dpc_reconstruction.split_flats import SplitFlats
from dpc_reconstruction.stackers import Stacker
from dpc_reconstruction.average import Average
from dpc_reconstruction.stackers import PhaseStepsSplitter
from dpc_reconstruction.phase_stepping import FourierAnalyzer
from dpc_reconstruction.visibility import VisibilityCalculator
from dpc_reconstruction.io.hdf5 import Hdf5Writer
from dpc_reconstruction.version import get_git_version

commandline_parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

commandline_parser.add_argument('files',
        metavar='FILE(s)',
        nargs='+',
        help='''file(s) with the images''')
commandline_parser.add_argument('--flat', '-f'
        metavar='FLATS(s)',
        nargs='+',
        help='''file(s) with the images''')
commandline_parser.add_argument('--overwrite', '-o',
        action='store_true',
        help='overwrite hdf5 files if they already exist.')
commandline_parser.add_argument('--verbose', '-v',
        action='store_true',
        help='print all the debug information.')
commandline_parser.add_argument('--jobs', '-j',
        nargs='?', default=1, type=int,
        help='specifies the number of jobs running simultaneously.')
commandline_parser.add_argument('--batch', '-b', 
        action='store_true',
        help='batch mode (no drawing or user interaction)')
commandline_parser.add_argument('--steps', '-s',
        nargs='?', default=1, type=int,
        help='number of phase steps')

def main(file_names, flat_file_names, phase_steps,
         overwrite=False, jobs=1, batch=False):
    """show on screen if not batch"""
    packet = pypesvds.lib.packet.Packet()

    flat_splitter = SplitFlats()

    sample_reader = Hdf5Reader()
    flat_reader = Hdf5Reader()

    sample_stacker = Stacker()
    flat_stacker = Stacker()

    sample_step_splitter = PhaseStepsSplitter()
    flat_step_splitter = PhaseStepsSplitter()
    sample_step_splitter.set_parameter('phase_steps', phase_steps)
    flat_step_splitter.set_parameter('phase_steps', phase_steps)

    sample_fourier_analyzer = FourierAnalyzer()
    flat_fourier_analyzer = FourierAnalyzer()
    flat_average = Average()

    flat_sample_merger = MergeFlatSample()
    file_writer = Hdf5Writer()
    file_writer.set_parameter("group", "postprocessing")
    file_writer.set_parameter("overwrite", overwrite)

    packet.set('sample', file_names)
    packet.set('flat', flat_file_names)
    network = {
        flat_splitter: {
            sample_reader('out', 'in'),
            flat_reader('out2', 'in'),
        },
        sample_reader: {
            sample_stacker: ('out', 'in'),
        },
        sample_stacker: {
            sample_fourier_analyzer: ('out', 'in'),
        },
        flat_reader: {
            flat_stacker: ('out', 'in'),
        },
        flat_stacker: {
            flat_fourier_analyzer: ('out', 'in'),
        },
        sample_fourier_analyzer: {
            flat_sample_merger: ('out', 'in'),
        },
        flat_fourier_analyzer: {
            flat_average: ('out', 'in')
        },
        flat_average: {
            flat_sample_merger: ('out', 'in2')
        },
        flat_sample_merger: {
            file_writer: ('out', 'in'),
        }
    }
    pipeline = pypes.pipeline.Dataflow(network, n=jobs)
    log.info("{0} {1}: analyzing {2} hdf5 files.".format(
        __name__, get_git_version(), len(file_names)))
    pipeline.send(packet)
    pipeline.close()

if __name__ == '__main__':
    import sys
    args = commandline_parser.parse_args()
    if args.verbose:
        config_dictionary['handlers']['default']['level'] = 'DEBUG'
        config_dictionary['loggers']['']['level'] = 'DEBUG'
    logging.config.dictConfig(config_dictionary)
    main(args.files, args.flat, args.steps,
            args.overwrite, args.jobs, args.batch)
