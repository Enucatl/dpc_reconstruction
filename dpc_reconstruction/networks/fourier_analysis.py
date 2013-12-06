"""Factory for the fourier component analysis

"""

from dpc_reconstruction.io.hdf5 import Hdf5Reader
from dpc_reconstruction.split_flats import SplitFlats
from dpc_reconstruction.split_flats import MergeFlatSample
from dpc_reconstruction.stackers import Stacker
from dpc_reconstruction.average import Average
from dpc_reconstruction.stackers import PhaseStepsSplitter
from dpc_reconstruction.phase_stepping import FourierAnalyzer
from dpc_reconstruction.io.hdf5 import Hdf5Writer


def fourier_analysis_network_factory(phase_steps,
                                     overwrite, group="raw_images"):
    """Build the network for the reconstruction pipeline.
    """
    flat_splitter = SplitFlats()

    sample_reader = Hdf5Reader()
    flat_reader = Hdf5Reader()
    sample_reader.__metatype__ = "TRANSFORMER"
    flat_reader.__metatype__ = "TRANSFORMER"
    sample_reader.set_parameter("group", group)
    flat_reader.set_parameter("group", group)

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
    network = {
        flat_splitter: {
            sample_reader: ('out', 'in'),
            flat_reader: ('out2', 'in'),
        },
        sample_reader: {
            sample_stacker: ('out', 'in'),
        },
        sample_stacker: {
            sample_step_splitter: ('out', 'in'),
        },
        sample_step_splitter: {
            sample_fourier_analyzer: ('out', 'in'),
        },
        flat_reader: {
            flat_stacker: ('out', 'in'),
        },
        flat_stacker: {
            flat_step_splitter: ('out', 'in'),
        },
        flat_step_splitter: {
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
    return network