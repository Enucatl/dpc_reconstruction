"""
Functions for reconstructing the DPC images from the raw phase steps.

"""

import os
import logging
import numpy as np
import tensorflow as tf

angle_module = tf.load_op_library(os.path.join("src", "arg.so"))
log = logging.getLogger(__name__)


def visibility(data):
    return 2 * data[:, :, 2] / data[:, :, 0]


def get_signals(phase_stepping_curves, n_periods=1):
    """Get the average a_0, the phase phi and the amplitude
    |a_1| from the phase stepping curves.

    Input:
    phase_stepping_curves is a tensorflow.Tensor with the phase stepping curves
    along the third axis, (x, y) pixels along the first two axes.

    n_periods is the number of periods used in the phase stepping.

    returns a0, phi and a1 along the last axis.
    """

    transformed = tf.py_func(
        np.fft.rfft,
        [phase_stepping_curves],
        [tf.complex128]
    )[0]
    a0 = tf.abs(transformed[:, :, 0])
    a1 = tf.abs(transformed[:, :, n_periods])
    phi1 = angle_module.arg(transformed[:, :, n_periods])
    return tf.pack([a0, phi1, a1], axis=-1)


def compare_sample_to_flat(sample, flat):
    a0_flat = flat[:, :, 0]
    phi_flat = flat[:, :, 1]
    a1_flat = flat[:, :, 2]
    result0 = sample[:, :, 0] / flat[:, :, 0]
    result1 = tf.mod(
        sample[:, :, 1] - flat[:, :, 1] + np.pi,
        2 * np.pi
    ) - np.pi
    result2 = sample[:, :, 2] / flat[:, :, 2] / result0
    return tf.pack([result0, result1, result2], axis=-1)
