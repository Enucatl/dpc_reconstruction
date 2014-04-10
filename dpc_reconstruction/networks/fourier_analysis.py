"""Factory for the fourier component analysis

"""

from pypes.component import HigherOrderComponent
from pypes.plugins.hdf5 import Hdf5ReadGroup
from dpc_reconstruction.split_flats import SplitFlatSample
from dpc_reconstruction.split_flats import MergeFlatSample
from dpc_reconstruction.stackers import Stacker
from dpc_reconstruction.average import Average
from dpc_reconstruction.stackers import PhaseStepsSplitter
from dpc_reconstruction.phase_stepping import FourierAnalyzer


def fourier_components_network_factory(phase_steps, group="raw_images"):
    """Subnetwork that needs to be performed on both the sample and flat
    data:
        - read the HDF5 files
        - stack the datasets
        - split according to the number of phase steps
        - fourier transform and keep three signals

    :phase_steps: the number of phase steps
    :group: group for the raw images in the HDF5 files
    :returns: the network in the dictionary format

    """
    reader = Hdf5ReadGroup()
    reader.__metatype__ = "TRANSFORMER"
    stacker = Stacker()
    step_splitter = PhaseStepsSplitter()
    step_splitter.set_parameter('phase_steps', phase_steps)
    fourier_analyzer = FourierAnalyzer()
    network = {
        reader: {
            stacker: ('out', 'in'),
        },
        stacker: {
            step_splitter: ('out', 'in'),
        },
        step_splitter: {
            fourier_analyzer: ('out', 'in'),
        },
    }
    return network


def fourier_analysis_network_factory(phase_steps,
                                     group="raw_images"):
    """Build the network for the reconstruction pipeline.
    - the flats and sample images are split and separately reconstructed by
      the same code (provided by the fourier_components_network_factory).
    - the flats are averaged
    - the sample data are merged with the flat data (division/subtraction)
    - the final images are saved to an output HDF5 file.

    :phase_steps: the number of phase steps
    :overwrite: overwrite the output dataset if it already exists
    :group: group for the raw images in the HDF5 files
    :returns: the network in the dictionary format
    """
    flat_splitter = SplitFlatSample()
    flat_component_calculator = HigherOrderComponent(
        fourier_components_network_factory(phase_steps, group))
    sample_component_calculator = HigherOrderComponent(
        fourier_components_network_factory(phase_steps, group))
    flat_average = Average()

    flat_sample_merger = MergeFlatSample()
    network = {
        flat_splitter: {
            sample_component_calculator: ('out', 'in'),
            flat_component_calculator: ('out2', 'in'),
        },
        sample_component_calculator: {
            flat_sample_merger: ('out', 'in'),
        },
        flat_component_calculator: {
            flat_average: ('out', 'in')
        },
        flat_average: {
            flat_sample_merger: ('out', 'in2')
        },
    }
    return network
