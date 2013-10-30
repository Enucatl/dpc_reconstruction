"""
Functions for reconstructing the DPC images from the raw phase steps.

"""

from __future__ import division, print_function

import numpy as np

def get_signals(phase_stepping_curves, n_periods=1, flat=None):
    """Get the average a_0, the phase phi and the amplitude 
    |a_1| from the phase stepping curves.

    Input:
    phase_stepping_curves is a numpy array with the phase stepping curves
    along the last axis (axis=-1).

    n_periods is the number of periods used in the phase stepping

    flat contains a0, phi and a1 from the flat image.
    The parameters for the flat can be computed with this same function, by
    simply providing flat=None (which is the default).

    returns a0, phi and a1 in a tuple, after division (subtraction for phi)
    by the flat parameters if a flat was provided.

    """

    transformed = np.fft.rfft(phase_stepping_curves)
    a0 = np.abs(transformed[..., 0]) 
    a1 = np.abs(transformed[..., n_periods]) 
    phi1 = np.angle(transformed[..., n_periods])
    if flat:
        a0_flat, phi_flat, a1_flat = flat
        a0 /= a0_flat
        a1 /= a1_flat / a0
        phi1 -= phi_flat
        #unwrap the phase values
        phi1 = np.mod(phi1 + np.pi, 2 * np.pi) - np.pi
    return a0, phi1, a1

