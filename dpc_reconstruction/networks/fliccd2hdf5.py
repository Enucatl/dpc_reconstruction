"""A factory for the fliccd to hdf5 converter. """

#!/usr/bin/env python
# encoding: utf-8

from __future__ import division, print_function

from dpc_reconstruction.io.file_reader import FileReader
from dpc_reconstruction.io.fliccd_hedpc import FliRawReader
from dpc_reconstruction.io.fliccd_hedpc import FliRawHeaderAnalyzer
from dpc_reconstruction.io.fliccd_hedpc import FliRaw2Numpy
from dpc_reconstruction.io.hdf5 import Hdf5Writer

def fliccd2hdf5_factory(overwrite, remove_source):
    """Build a network that converts a fliccd raw file to a hdf5 dataset.

    :overwrite: overwrite target dataset if it exists
    :remove_source: remove original raw file
    :returns: the network as a dictionary

    """
    file_reader = FileReader()
    file_reader.set_parameter("remove_source", remove_source)
    fliraw_reader = FliRawReader()
    header_analyzer = FliRawHeaderAnalyzer()
    numpy_converter = FliRaw2Numpy()
    hdf_writer = Hdf5Writer()
    hdf_writer.set_parameter("overwrite", overwrite)
    FliRawReader.__metatype__ = "TRANSFORMER"
    network = {
            file_reader: {
                fliraw_reader: ('out', 'in'),
                },
            fliraw_reader: {
                header_analyzer: ('out', 'in'),
                },
            header_analyzer: {
                numpy_converter: ('out', 'in'),
                },
            numpy_converter: {
                hdf_writer: ('out', 'in'),
                },
            }
    return network
