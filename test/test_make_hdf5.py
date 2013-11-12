"""Test the make_hdf5.py script.

"""

import pytest
import stackless

import pypes.component
import pypes.pipeline

from dpc_reconstruction.io.file_reader import FileReader

class PublisherTest(pypes.component.Component):
    # defines the type of component we're creating.
    __metatype__ = 'PUBLISHER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)
        
        self.set_parameter("attribute_name", "data")
        # Optionally add/remove component ports
        self.remove_output('out')

    def run(self):
        # Define our components entry point
        while True:
            # for each packet waiting on our input port
            attribute_name = self.get_parameter("attribute_name")
            packet = self.receive('in')
            self.result = packet.get(attribute_name)
            # yield the CPU, allowing another component to run
            assert 0
            self.yield_ctrl()

@pytest.fixture(scope="function")
def pipeline_and_publisher(request):
    """Build a mini pipeline to test one component at a time.
    The component is passed by adding it as an attribute to the test
    function.

    """
    component = request.function.component
    publisher = PublisherTest()
    network = {
            component: {
                publisher: ("out", "in")
                }
            }
    pipeline = pypes.pipeline.Dataflow(network)
    def fin():
        pipeline.close()
    request.addfinalizer(fin)
    return pipeline, publisher
    
@pytest.mark.usefixtures("pipeline_and_publisher")
class TestMakeHdf5(object):
    """Test all the components of the make hdf5 pipeline."""

    def test_file_reader(self, pipeline_and_publisher):
        expected_output = 0
        pipeline, publisher = pipeline_and_publisher
        publisher.set_parameter("attribute_name", "data")
        pipeline.send("fliccd_data/ccdimage_00045_00000_00.raw")
    test_file_reader.component = FileReader()
