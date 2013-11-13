from glob import glob
import os
import pytest

TEST_DATA_FOLDER = "fliccd_data"
TEST_INPUT_FILES = glob(os.path.join(TEST_DATA_FOLDER, "*.raw"))

import logging
import logging.config
from dpc_reconstruction.logger_config import config_dictionary

log = logging.getLogger()
config_dictionary['handlers']['default']['level'] = 'DEBUG'
config_dictionary['loggers']['']['level'] = 'DEBUG'
logging.config.dictConfig(config_dictionary)

def function_to_classname(test_function_name):
    """return the class name of the component to be tested by converting the
    test function name to camelcase.

    >>> function_to_classname("test_fli_raw_reader")
    FliRawReader
    >>> function_to_classname("test_hdf5_writer")
    Hdf5Writer

    """
    #drop "test_" at the beginning
    split_along_underscores = test_function_name.split("_")[1:]
    classname = "".join(w.capitalize() for w in split_along_underscores)
    return classname

@pytest.fixture(scope="function")
def pype_and_tasklet(request):
    """Build pypes to send input and get output from one component at a time.
    The component class name is passed by adding it as an attribute to the test
    function.

    Tries to guess the component name from the function name if not
    explicitly set.

    """
    try:
        component = request.function.component()
    except AttributeError:
        class_name = function_to_classname(request.function.__name__)
        if class_name not in globals():
            raise NameError("{0} not defined!".format(class_name))
        else:
            component = globals()[class_name]()
    pype = pypes.pype.Pype()
    component.connect_input("in", pype)
    if component.has_port("out"):
        component.connect_output("out", pype)
    tasklet = stackless.tasklet(component.run)()
    return pype, tasklet, component

@pytest.fixture(scope="function")
def packet():
    return pypesvds.lib.packet.Packet()

