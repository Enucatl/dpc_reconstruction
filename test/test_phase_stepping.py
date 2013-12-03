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
    p = 2 * np.pi * periods / n  # period
    # last step (n + 1) taken here and discarded in
    # phase_stepping_utils.get_signals
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

    @pytest.mark.parametrize("c", np.random.randint(100, 100000, size=2))
    @pytest.mark.parametrize("v", np.random.random(size=2))
    @pytest.mark.parametrize("phi", -2 + 4 * np.random.random(size=2))
    @pytest.mark.parametrize("steps_per_period", range(3, 7))
    @pytest.mark.parametrize("periods", np.random.randint(1, 3, size=3))
    def test_fourier_analyzer(self, pype_and_tasklet, packet,
                              c, v, phi, steps_per_period, periods):
        pype, tasklet, component = pype_and_tasklet
        steps = steps_per_period * periods
        pixels_x = 1
        pixels_y = 2
        pixels_z = 3
        curve = phase_stepping_curve(c, v, phi, steps, periods)
        input_data = np.tile(curve, (pixels_x, pixels_y, pixels_z, 1))
        packet.set('data', input_data)
        component.set_parameter("n_periods", periods)
        pype.send(packet)
        tasklet.run()
        output = pype.recv()
        assert output.get('data').shape == (pixels_x, pixels_y, pixels_z, 3)
        assert np.allclose(output.get('data')[..., 0], c * steps)
        assert np.allclose(output.get('data')[..., 2], v * c * steps / 2)
        assert np.allclose(output.get('data')[..., 1], phi)
    test_fourier_analyzer.component = FourierAnalyzer
