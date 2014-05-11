"""A factory for the visibility calculator. """

from __future__ import division, print_function

from pypes.component import HigherOrderComponent
from pypes.plugins.hdf5 import Hdf5Writer
from pypes.plugins.hdf5 import Hdf5ReadGroup

from dpc_reconstruction.stackers import Stacker
from dpc_reconstruction.visibility import VisibilityCalculator
import dpc_reconstruction.networks.fourier_analysis as fca


def visibility_factory(phase_steps, overwrite, batch):
    """Build a network that calculates the visibility of the phase stepping
    curves.

    :overwrite: overwrite target dataset if it exists
    :batch: show on screen if not batch
    :returns: the network as a dictionary

    """
    file_reader = Hdf5ReadGroup()
    stacker = Stacker()
    fca_network = fca.fourier_components_network_factory(phase_steps)
    fourier_analyzer = HigherOrderComponent(fca_network)
    visibility_calculator = VisibilityCalculator()
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
    }
    return network
