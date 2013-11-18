"""Test the dpc reconstructions."""

import pytest
import numpy as np

from dpc_reconstruction.stackers import PhaseStepsSplitter
from dpc_reconstruction.phase_stepping import FourierAnalyzer

import logging
import logging.config
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()
config_dictionary['handlers']['default']['level'] = 'DEBUG'
config_dictionary['loggers']['']['level'] = 'DEBUG'
logging.config.dictConfig(config_dictionary)

def phase_stepping_curve(c, v, phi, n, periods):
    """Return the phase stepping curve sampled over 'periods' periods
    with average c, visibility v, shift phi and n steps.

        >>> phase_stepping_curve(0.5, 1, 0, 4)
        array([ 1. ,  0.5,  0. ,  0.5])
    """
    p = 2 * np.pi * periods / n #period
    #last step (n + 1) taken here and discarded in
    #phase_stepping_utils.get_signals
    xs = np.arange(n)
    angles = p * xs + phi
    return c * (1 + v * np.cos(angles))

@pytest.mark.usefixtures("packet")
@pytest.mark.usefixtures("pype_and_tasklet")
class TestDPCReconstruction(object):
    """Test the phase stepping curve reconstruction.
    
    """

    def test_phase_steps_splitter(self, pype_and_tasklet,
                                  packet):
        pype, tasklet, component = pype_and_tasklet
        component.set_parameter('phase_steps', 25)
        input_data = np.random.rand(5, 10, 100)
        packet.set('data', input_data)
        pype.send(packet)
        tasklet.run()
        output = pype.recv()
        assert output.get('data').shape == (5, 10, 4, 25)
    test_phase_steps_splitter.component = PhaseStepsSplitter

    def test_fourier_analyzer(self, pype_and_tasklet,
                              packet):
        pype, tasklet, _ = pype_and_tasklet
        input_data = np.random.rand(5, 10, 4, 25)
        packet.set('data', input_data)
        pype.send(packet)
        tasklet.run()
        output = pype.recv()
        assert output.get('data').shape == (5, 10, 4, 3)
    test_fourier_analyzer.component = FourierAnalyzer
