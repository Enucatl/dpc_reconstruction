"""Test the dpc reconstructions."""

import pytest
import numpy as np
import tensorflow as tf

import logging
import logging.config
import dpc_reconstruction.phase_stepping as m
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


class TestDPCReconstruction(object):
    """Test the phase stepping curve reconstruction.

    """

    @pytest.mark.parametrize("c", np.random.randint(100, 100000, size=1))
    @pytest.mark.parametrize("v", np.random.random(size=1))
    @pytest.mark.parametrize("phi", -2 + 4 * np.random.random(size=1))
    @pytest.mark.parametrize("steps_per_period", range(3, 4))
    @pytest.mark.parametrize("periods", np.random.randint(1, 3, size=1))
    def test_fourier_analyzer(self, c, v, phi, steps_per_period, periods):
        steps = steps_per_period * periods
        pixels_x = 1
        pixels_y = 2
        curve = phase_stepping_curve(c, v, phi, steps, periods)
        input_data = tf.constant(
            np.tile(curve, (pixels_x, pixels_y, 1))
        )
        with tf.Session() as sess:
            output = sess.run(m.get_signals(input_data, periods))
            assert output.shape == (pixels_x, pixels_y, pixels_z, 3)
            assert np.allclose(output[..., 0], c * steps)
            assert np.allclose(output[..., 2], v * c * steps / 2)
            assert np.allclose(output[..., 1], phi)
