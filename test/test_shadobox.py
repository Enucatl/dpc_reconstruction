"""Test the dpc reconstructions."""

import pytest
from dpc_reconstruction.io.shadobox import ShadoboxToNumpy

import logging
import logging.config
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()
config_dictionary['handlers']['default']['level'] = 'DEBUG'
config_dictionary['loggers']['']['level'] = 'DEBUG'
logging.config.dictConfig(config_dictionary)


@pytest.mark.usefixtures("packet")  # pylint: disable=E1101
@pytest.mark.usefixtures("pype_and_tasklet")  # pylint: disable=E1101
class TestShadobox(object):
    """Test the shadobox reader

    """

    def test_shadobox_to_numpy(self, pype_and_tasklet,
                               packet):
        pype, tasklet, _ = pype_and_tasklet
        packet.set('data',
                   open('shadobox_data/shadobox_test.raw', 'rb').read())
        pype.send(packet)
        tasklet.run()
        output = pype.recv()
        assert output.get('data').shape == (10, 10)
    test_shadobox_to_numpy.component = ShadoboxToNumpy
