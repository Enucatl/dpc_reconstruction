"""Test the make_hdf5.py script.

How to write a test function.

- use the pype_and_tasklet fixture to get a pype and a tasklet
- send the input with pype.send
- run the tasklet with stackless.tasklet.run
- get the output on the same pype (pype.recv)
- write all the needed assertions on the results
- after the function, set the component to be tested with
test_method.component = Component

"""

import pytest
import stackless
import os
from glob import glob
import numpy as np
import h5py

import pypes.component
import pypes.pype
import pypesvds.lib.packet

from dpc_reconstruction.io.file_reader import FileReader
from dpc_reconstruction.io.hdf5 import Hdf5Writer

TEST_DATA_FOLDER = "fliccd_data"

@pytest.fixture(scope="function")
def pype_and_tasklet(request):
    """Build pypes to send input and get output from one component at a time.
    The component class name is passed by adding it as an attribute to the test
    function.

    """
    component = request.function.component()
    pype = pypes.pype.Pype()
    component.connect_input("in", pype)
    if component.has_port("out"):
        component.connect_output("out", pype)
    tasklet = stackless.tasklet(component.run)()
    return pype, tasklet, component

@pytest.fixture(scope="function")
def packet():
    return pypesvds.lib.packet.Packet()

    
@pytest.mark.usefixtures("packet")
@pytest.mark.usefixtures("pype_and_tasklet")
class TestMakeHdf5(object):
    """Test all the components of the make hdf5 pipeline."""

    @pytest.mark.parametrize("input_file_name",
            glob(os.path.join(TEST_DATA_FOLDER, "*.raw")))
    def test_file_reader(self, pype_and_tasklet,
            input_file_name):
        pype, tasklet, _ = pype_and_tasklet
        pype.send(input_file_name)
        tasklet.run()
        data = pype.recv()
        assert data.get("data") == open(input_file_name).read()
        assert data.get("full_path") == os.path.abspath(input_file_name)

    test_file_reader.component = FileReader

    @pytest.mark.parametrize("input_file_name",
            glob(os.path.join(TEST_DATA_FOLDER, "*.raw")))
    def test_hdf5_writer(self, pype_and_tasklet,
            packet, input_file_name):
        pype, tasklet, component = pype_and_tasklet
        component.set_parameter("overwrite", True)
        random_image = np.random.rand(5, 25)
        packet.set("full_path", input_file_name)
        packet.set("image", random_image)
        pype.send(packet)
        tasklet.run()
        output_hdf5, dataset_name = os.path.split(input_file_name)
        output_hdf5 += ".hdf5"
        dataset_name = os.path.splitext(dataset_name)[0]
        output_file = h5py.File(output_hdf5)
        output_group = output_file[
                component.get_parameter("group")]
        assert (output_group[dataset_name][...] == random_image).all()
        assert not packet.has("image")

    test_hdf5_writer.component = Hdf5Writer


