"""A factory for the visibility calculator. """

from __future__ import division, print_function

from pypes.plugins.hdf5 import Hdf5Writer
from pypes.plugins.hdf5 import Hdf5ReadGroup
from dpc_reconstruction.stackers import Stacker
from dpc_reconstruction.phase_stepping import FourierAnalyzer
from dpc_reconstruction.visibility import VisibilityCalculator


def visibility_factory(overwrite, batch):
    """Build a network that calculates the visibility of the phase stepping
    curves.

    :overwrite: overwrite target dataset if it exists
    :batch: show on screen if not batch
    :returns: the network as a dictionary

    """
    file_reader = Hdf5ReadGroup()
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
    return network
