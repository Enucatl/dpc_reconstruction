"""Test the flats_every components and script."""

import pytest
import numpy as np

import pypes.pype
from dpc_reconstruction.flats_every import SplitFlatsEvery
from dpc_reconstruction.flats_every import MergeFlatsEvery

import stackless
import logging
import logging.config
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()
config_dictionary['handlers']['default']['level'] = 'DEBUG'
config_dictionary['loggers']['']['level'] = 'DEBUG'
logging.config.dictConfig(config_dictionary)


@pytest.fixture(scope="function")
def split_pype_and_tasklet():
    """Build pypes to send input and get output from the
    SplitFlatsEvery component.

    """
    files = 20 * ["fliccd_data.hdf5"]
    component = SplitFlatsEvery(files,
                                flats_every=6,
                                n_flats=4)
    pype = pypes.pype.Pype()
    component.connect_input("in", pype)
    component.connect_output("out0", pype)
    tasklet = stackless.tasklet(component.run)()
    return pype, tasklet, component


@pytest.fixture(scope="function")
def merge_pype_and_tasklet():
    """Build pypes to send input and get output from the
    MergeFlatsEvery component.

    """
    component = MergeFlatsEvery(n=2)
    pype0 = pypes.pype.Pype()
    pype1 = pypes.pype.Pype()
    component.connect_input("in0", pype0)
    component.connect_input("in1", pype1)
    component.connect_output("out", pype0)
    tasklet = stackless.tasklet(component.run)()
    return pype0, pype1, tasklet, component


@pytest.mark.usefixtures("packet")
class TestFlatsEvery(object):
    """Test the flats_every components

    """

    @pytest.mark.usefixtures("split_pype_and_tasklet")
    def test_split_flats_every(self, split_pype_and_tasklet):
        pype, tasklet, _ = split_pype_and_tasklet
        pype.send(None)
        tasklet.run()
        output = pype.recv()
        assert len(output.get('flat')) == 4
        assert len(output.get('sample')) == 6

    @pytest.mark.usefixtures("merge_pype_and_tasklet")
    def test_merge_flats_every(self, merge_pype_and_tasklet, packet):
        pype0, pype1, tasklet, _ = merge_pype_and_tasklet
        dataset0 = np.zeros((5, 10, 1, 3))
        dataset1 = np.zeros((5, 10, 1, 3))
        packet.set("data", dataset0)
        pype0.send(packet)
        packet.set("data", dataset1)
        pype1.send(packet)
        tasklet.run()
        output = pype0.recv()
        assert output.get('data').shape == ((5, 10, 2, 3))
