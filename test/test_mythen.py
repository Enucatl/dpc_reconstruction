"""Test the dpc reconstructions."""

import pytest
from dpc_reconstruction.io.mythen import MythenToNumpy

import logging
import logging.config
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()
config_dictionary['handlers']['default']['level'] = 'DEBUG'
config_dictionary['loggers']['']['level'] = 'DEBUG'
logging.config.dictConfig(config_dictionary)


@pytest.mark.usefixtures("packet")  # pylint: disable=E1101
@pytest.mark.usefixtures("pype_and_tasklet")  # pylint: disable=E1101
class TestMythen(object):
    """Test the mythen reader

    """

    def test_mythen_to_numpy(self, pype_and_tasklet,
                               packet):
        pype, tasklet, _ = pype_and_tasklet
        packet.set('data',
                   open('mythen_data/image_ct_033300_0.raw', 'r').read())
        packet.set('file_name', 'mythen_data/image_ct_033300_0.raw')
        pype.send(packet)
        tasklet.run()
        output = pype.recv()
        assert output.get('data').shape == (2560, )
    test_mythen_to_numpy.component = MythenToNumpy
