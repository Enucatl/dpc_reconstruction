"""Test the visibility.py script.

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

from dpc_reconstruction.networks.visibility import visibility_factory

import logging
import logging.config
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()
config_dictionary['handlers']['default']['level'] = 'DEBUG'
config_dictionary['loggers']['']['level'] = 'DEBUG'
logging.config.dictConfig(config_dictionary)


class VisibilityNetwork(pypes.component.HigherOrderComponent):
    def __init__(self):
        super(VisibilityNetwork, self).__init__(
            visibility_factory(overwrite=True, batch=True))


@pytest.mark.usefixtures("packet")
@pytest.mark.usefixtures("pype_and_tasklet")
class TestVisibility(object):
    """Test the visibility pipeline."""

    def test_visibility_network(self, pype_and_tasklet, packet):
        pype, tasklet, _ = pype_and_tasklet
        file_name = "visibility_test_data.hdf5"
        packet.set("file_name", file_name)
        packet.set("data", "raw_images")
        pype.send(packet)
        tasklet.run()
        data = pype.recv()
        h5file = h5py.File(file_name)
        old_visibility_result = h5file[
            "postprocessing/visibility_505"][1, :]
        h5file.close()
        result = data.get("data")[0, 300:800]
        print(old_visibility_result.shape, result.shape)
        assert (result == old_visibility_result).all()
    test_visibility_network.component = VisibilityNetwork
