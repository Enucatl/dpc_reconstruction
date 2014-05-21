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
import pypes.component
from pypes.component import HigherOrderComponent

from pypes.plugins.name_changer import NameChanger
from dpc_reconstruction.commandline_parsers.phase_stepping\
    import PhaseSteppingParser
from pypes.plugins.hdf5 import Hdf5Writer
from dpc_reconstruction.commandline_parsers.basic import BasicParser
from dpc_reconstruction.networks.visibility import visibility_factory

description = "{1}\n\n{0}\n".format(dpc_reconstruction.__version__, __doc__)
commandline_parser = PhaseSteppingParser(description=description)
commandline_parser.add_argument('files',
                                metavar='FILE(s)',
                                nargs='+',
                                help='''file(s) with the images''')


def main(file_names, phase_steps,
         group="/",
         overwrite=False, jobs=1,
         batch=True):
    """show on screen if not batch"""
    vis_network = visibility_factory(phase_steps, group, overwrite, batch)
    file_writer = Hdf5Writer()
    name_changer = NameChanger({
        "data": "visibility_map",
    })
    file_writer.set_parameter("group", "postprocessing")
    file_writer.set_parameter("overwrite", overwrite)
    visibility_calculator = pypes.component.HigherOrderComponent(vis_network)
    visibility_calculator.__metatype__ = "ADAPTER"
    network = {
        visibility_calculator: {
            name_changer: ("out", "in"),
        },
        name_changer: {
            file_writer: ("out", "in"),
        },
    }
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
        packet.set("data", group)
        pipeline.send(packet)
    pipeline.close()

if __name__ == '__main__':
    args = commandline_parser.parse_args()
    if args.verbose:
        config_dictionary['handlers']['default']['level'] = 'DEBUG'
        config_dictionary['loggers']['']['level'] = 'DEBUG'
    logging.config.dictConfig(config_dictionary)
    main(args.files, args.steps,
         args.group, args.overwrite,
         args.jobs, args.batch)
