from glob import glob
import os
import pytest
import stackless

TEST_DATA_FOLDER = "fliccd_data"
TEST_INPUT_FILES = glob(os.path.join(TEST_DATA_FOLDER, "*.raw"))

import logging
import logging.config
from dpc_reconstruction.logger_config import config_dictionary

log = logging.getLogger()
config_dictionary['handlers']['default']['level'] = 'DEBUG'
config_dictionary['loggers']['']['level'] = 'DEBUG'
logging.config.dictConfig(config_dictionary)

import pypes.pype
import pypes.packet.packet


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
    return pypes.packet.packet.Packet()
