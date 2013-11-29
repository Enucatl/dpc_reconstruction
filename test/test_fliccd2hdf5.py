"""Test the make_hdf5.py script.

How to write a test function:

- use the pype_and_tasklet fixture to get a pype and a tasklet
- send the input with pype.send
- run the tasklet with stackless.tasklet.run
- get the output on the same pype (pype.recv)
- write all the needed assertions on the results
- after the function, set the component to be tested with
test_method.component = Component
"""

import pytest
import numpy as np
import h5py
import os

import pypes.component
import pypes.pipeline

from dpc_reconstruction.io.file_reader import FileReader
from dpc_reconstruction.io.hdf5 import Hdf5Writer
from dpc_reconstruction.io.fliccd_hedpc import FliRawReader
from dpc_reconstruction.io.fliccd_hedpc import FliRawHeaderAnalyzer
from dpc_reconstruction.io.fliccd_hedpc import FliRaw2Numpy
from dpc_reconstruction.networks.fliccd2hdf5 import fliccd2hdf5_factory

from conftest import TEST_INPUT_FILES

import logging
import logging.config
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()
config_dictionary['handlers']['default']['level'] = 'DEBUG'
config_dictionary['loggers']['']['level'] = 'DEBUG'
logging.config.dictConfig(config_dictionary)

@pytest.mark.usefixtures("packet")
@pytest.mark.usefixtures("pype_and_tasklet")
class TestFliccd2Hdf5(object):
    """Test all the components of the make hdf5 pipeline."""

    @pytest.mark.parametrize("input_file_name", TEST_INPUT_FILES)
    def test_file_reader(self, pype_and_tasklet,
            input_file_name):
        pype, tasklet, _ = pype_and_tasklet
        pype.send(input_file_name)
        tasklet.run()
        data = pype.recv()
        assert data.get("data") == open(input_file_name, "rb").read()
        assert data.get("full_path") == os.path.abspath(input_file_name)
    test_file_reader.component = FileReader

    @pytest.mark.parametrize("input_file_name", TEST_INPUT_FILES)
    def test_hdf5_writer(self, pype_and_tasklet,
            packet, input_file_name):
        pype, tasklet, component = pype_and_tasklet
        component.set_parameter("overwrite", True)
        random_image = np.random.rand(5, 25)
        packet.set("full_path", input_file_name)
        packet.set("data", random_image)
        pype.send(packet)
        tasklet.run()
        output_hdf5, dataset_name = os.path.split(input_file_name)
        output_hdf5 += ".hdf5"
        dataset_name = os.path.splitext(dataset_name)[0]
        output_file = h5py.File(output_hdf5)
        output_group = output_file[
                component.get_parameter("group")]
        assert (output_group[dataset_name][...] == random_image).all()
        assert not packet.has("data")
    test_hdf5_writer.component = Hdf5Writer

    @pytest.mark.parametrize("input_file_name", TEST_INPUT_FILES)
    def test_fli_raw_reader(self, pype_and_tasklet,
            packet, input_file_name):
        pype, tasklet, _ = pype_and_tasklet
        content = open(input_file_name, "rb").read()
        packet.set("data", content)
        pype.send(packet)
        tasklet.run()
        output = pype.recv()
        assert output.get("header") == content.splitlines()[:16]
        assert output.get("data") == content.splitlines()[-1][1:]
    test_fli_raw_reader.component = FliRawReader

    @pytest.mark.parametrize("input_file_name", TEST_INPUT_FILES)
    def test_fli_raw_header_analyzer(self, pype_and_tasklet,
            packet, input_file_name):
        pype, tasklet, _ = pype_and_tasklet
        header = open(input_file_name, "rb").readlines()[:16]
        #header = "".join(header)
        packet.set("header", header)
        pype.send(packet)
        tasklet.run()
        output = pype.recv()
        assert output.get("min_y") == 500
        assert output.get("min_x") == 4
        assert output.get("max_x") == 1028
        assert output.get("max_y") == 560
        assert output.get("exposure_time") == 5
    test_fli_raw_header_analyzer.component = FliRawHeaderAnalyzer

    @pytest.mark.parametrize("tries", range(5))
    def test_fli_raw_2_numpy(self, pype_and_tasklet,
            packet, tries):
        pype, tasklet, _ = pype_and_tasklet
        random_image = np.random.randint(5, 25, (10, 10)).astype(np.uint16)
        packet.set("min_x", 0)
        packet.set("max_x", 10)
        packet.set("max_y", 10)
        packet.set("min_y", 0)
        packet.set("data", random_image.tostring(order="F"))
        pype.send(packet)
        tasklet.run()
        output = pype.recv()
        assert (output.get("data") == random_image).all()
    test_fli_raw_2_numpy.component = FliRaw2Numpy

class TestFliccd2Hdf5Network(object):
    """Test the complete network"""

    def test_complete_network(self):
        network = fliccd2hdf5_factory(overwrite=True, remove_source=False)
        pipeline = pypes.pipeline.Dataflow(network)
        for file_name in TEST_INPUT_FILES:
            pipeline.send(file_name)
        pipeline.close()
