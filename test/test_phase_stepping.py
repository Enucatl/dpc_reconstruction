"""Test the dpc reconstructions."""

import numpy as np
from numpy import pi
import random

from dpc_reconstruction.phase_stepping import get_signals

def phase_stepping_curve(c, v, phi, n, periods):
    """Return the phase stepping curve sampled over 'periods' periods
    with average c, visibility v, shift phi and n steps.

        >>> phase_stepping_curve(0.5, 1, 0, 4)
        array([ 1. ,  0.5,  0. ,  0.5])
    """
    p = 2 * pi * periods / n #period
    #last step (n + 1) taken here and discarded in
    #phase_stepping_utils.get_signals
    xs = np.arange(n)
    angles = p * xs + phi
    return c * (1 + v * np.cos(angles))

class TestDPCReconstruction(object):
    """Test the phase stepping curve reconstruction.
    
    """

    def test_retrieving_signals(self):
        """Generate N phase stepping curves and check that they are
        correctly reconstructed.

        """
        N = 100
        pixels = 10
        for _ in range(N):
            constant = random.uniform(100, 100000)
            phase = random.uniform(-pi / 2, pi / 2)
            visibility = random.uniform(0, 1)
            periods = random.randint(1, 3)
            steps = random.randint(4, 24) * periods
            curve = phase_stepping_curve(constant, visibility,
                    phase, steps, periods)
            #repeat the curve for 10x10 pixels
            all_pixels = np.tile(curve, (pixels, pixels, 1))
            a0, phi, a1 = get_signals(all_pixels, n_periods=periods)
            assert np.allclose(a0 / steps, constant)
            assert np.allclose(phi, phase)
            assert np.allclose(2 * a1 / a0, visibility)
