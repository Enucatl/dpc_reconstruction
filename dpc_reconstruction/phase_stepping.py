"""
Functions for reconstructing the DPC images from the raw phase steps.

"""

from __future__ import division, print_function

import numpy as np
import math

def get_signals(phase_stepping_curves, n_periods=1, flat=None):
    """Get the average a_0, the phase phi and the amplitude 
    |a_1| from the phase stepping curves.

    Input:
    phase_stepping_curves is a numpy array with the phase stepping curves
    along the second axis (axis=2).

    n_periods is the number of periods used in the phase stepping

    flat contains a0, phi and a1 from the flat image.
    The parameters for the flat can be computed with this same function, by
    simply providing flat=None (which is the default).

    returns a0, phi and a1 in a tuple, after division (subtraction for phi)
    by the flat parameters if a flat was provided.

    """

    n_phase_steps = phase_stepping_curves.shape[2]
    transformed = np.fft.rfft(
            phase_stepping_curves,
            n_phase_steps - 1,
            axis=2)
    a0 = np.abs(transformed[:, :, 0]) 
    a1 = np.abs(transformed[:, :, n_periods]) 
    phi1 = np.angle(transformed[:, :, n_periods])
    if flat:
        a0_flat, phi_flat, a1_flat = flat
        a0 /= a0_flat
        a1 /= a1_flat / a0
        phi1 -= phi_flat
        #unwrap the phase values
        phi1 = np.mod(phi1 + math.pi, 2 * math.pi) - math.pi
    return a0, phi1, a1

