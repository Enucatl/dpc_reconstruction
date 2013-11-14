#!/usr/bin/env python
# encoding: utf-8
"""Calculate the visibility."""

from __future__ import division, print_function

import os
import argparse

import logging
import logging.config
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()

import pypes.pipeline

from dpc_reconstruction.io.hdf5 import Hdf5Reader
from dpc_reconstruction.stackers import Stacker
from dpc_reconstruction.phase_stepping import FourierAnalyzer
from dpc_reconstruction.visibility import VisibilityCalculator
from dpc_reconstruction.io.hdf5 import Hdf5Writer
from dpc_reconstruction.version import get_git_version

commandline_parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

commandline_parser.add_argument('files',
        metavar='FOLDER(s)',
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


def main(file_names, overwrite=False, jobs=1,
        batch=False):
    """show on screen if not batch"""
    file_reader = Hdf5Reader()
    stacker = Stacker()
    fourier_analyzer = FourierAnalyzer()
    visibility_calculator = VisibilityCalculator()
    file_writer = Hdf5Writer()
    file_writer.set_parameter("group", "postprocessing")
    file_writer.set_parameter("overwrite", overwrite)
    network = {
            file_reader: {
                stacker: ('out', 'in'),
                },
            stacker: {
                fourier_analyzer: ('out', 'in'),
                },
            fourier_analyzer: {
                visibility_calculator: ('out', 'in'),
                },
            visibility_calculator: {
                file_writer: ('out', 'in'),
                },
            }
    if not batch:
        from pypesvds.plugins.splitoperator.splitoperator import Split
        from dpc_reconstruction.io.plots import VisibilityPlotter
        visibility_plotter = VisibilityPlotter()
        splitter = Split()
        network[visibility_calculator] = {
                splitter: ('out', 'in'),
                }
        network[splitter] = {
                file_writer: ('out', 'in'),
                visibility_plotter: ('out2', 'in'),
                }
    pipeline = pypes.pipeline.Dataflow(network, n=jobs)
    log.info("{0} {1}: analyzing {2} hdf5 files.".format(
        __name__, get_git_version(), len(file_names)))
    for file_name in file_names:
        if not os.path.exists(file_name) or not os.path.isfile(file_name):
            log.error("{0}: file {1} not found!".format(
                __name__, folder))
            raise OSError
        pipeline.send(file_name)
    pipeline.close()
            
if __name__ == '__main__':
    import sys
    args = commandline_parser.parse_args()
    if args.verbose:
        config_dictionary['handlers']['default']['level'] = 'DEBUG'
        config_dictionary['loggers']['']['level'] = 'DEBUG'
    logging.config.dictConfig(config_dictionary)
    main(args.files, args.overwrite,
            args.jobs, args.batch)
