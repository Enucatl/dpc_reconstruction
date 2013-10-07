"""Test the dpc reconstructions."""

import numpy as np
from numpy import pi
import h5py
import tempfile
import os
import random

from dpc.phase_stepping_utils import get_signals

def phase_stepping_curve(c, v, phi, n, periods):
    """Return the phase stepping curve sampled over 'periods' periods
    with average c, visibility v, shift phi and n steps.

        >>> phase_stepping_curve(0.5, 1, 0, 4)
        array([ 1. ,  0.5,  0. ,  0.5])
    """
    p = 2 * pi * periods / n #period
    #last step (n + 1) taken here and discarded in
    #phase_stepping_utils.get_signals
    xs = np.arange(n + 1)
    angles = p * xs + phi
    return c * (1 + v * np.cos(angles))

class TestDPCRadiography(object):
    """Test the phase stepping curve reconstruction.
    
    """

    def test_retrieving_signals(self):
        """Generate N phase stepping curves and check that they are
        correctly reconstructed.

        """
        N = 100
        pixels = 1024
        for i in range(N):
            temp_file_name = "test_dpc_radiography_{0}.hdf5".format(i)
            #hdf_file = h5py.File(temp_file_name)
            constant = random.uniform(100, 100000)
            phase = random.uniform(-pi / 2, pi / 2)
            visibility = random.uniform(0, 1)
            periods = random.randint(1, 3)
            steps = random.randint(4, 24) * periods
            curve = phase_stepping_curve(constant, visibility,
                    phase, steps, periods)
            all_pixels = np.transpose(
                    np.tile(curve, (pixels, 1)))[:, np.newaxis]
            print(steps, periods)
            print(all_pixels.shape)
            a0, phi, a1 = get_signals(
                    all_pixels, None, periods)
            assert np.allclose(a0 / steps, constant)
            assert np.allclose(phi, phase)
            assert np.allclose(2 * a1 / a0, visibility)
