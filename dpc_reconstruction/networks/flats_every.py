"""Factory for the fourier component analysis
with flats every flats_every scans

"""

import dpc_reconstruction.networks.fourier_analysis as fca
from pypes.component import HigherOrderComponent
from dpc_reconstruction.io.hdf5 import output_name
from dpc_reconstruction.flats_every import SplitFlatSampleEvery
from dpc_reconstruction.flats_every import MergeFlatsEvery


def flats_every_network_factory(files, flats_every,
                                n_flats, phase_steps,
                                group="raw_images"):
    """Separate the files into groups with one flat section each that is
    then processed by the fourier analysis network.

    :files: Full list of all files
    :flats_every: Flat scan every this many files
    :n_flats: number of flats to average every time a flat is taken
    :phase_steps: number of phase steps
    :overwrite: overwrite the output dataset if it already exists
    :group: group for the raw images in the HDF5 files
    :returns: the network in the dictionary format

    """
    splitter = SplitFlatSampleEvery(files, flats_every, n_flats)
    network = {splitter: {}}
    n = len(files) // (flats_every + n_flats)
    merger = MergeFlatsEvery(n)
    output_file_name = output_name(
        files, merger.__class__.__name__)
    merger.set_parameter("full_path", output_file_name)
    for i in range(n):
        fourier_network = fca.fourier_analysis_network_factory(
            phase_steps, group)
        fca_analyzer = HigherOrderComponent(fourier_network)
        network[splitter][fca_analyzer] = ("out{0}".format(i),
                                           "in")
        network[fca_analyzer] = {
            merger: ("out", "in{0}".format(i))
        }
    return network
