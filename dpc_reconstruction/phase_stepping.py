"""
Functions for reconstructing the DPC images from the raw phase steps.

"""

import logging
import numpy as np
import tensorflow as tf

log = logging.getLogger(__name__)


def angle(c):
    y = tf.imag(c)
    x = tf.real(c)
    zeros = tf.zeros_like(x)
    cond1 = tf.greater(x, zeros)
    cond2 = tf.logical_and(tf.less(x, zeros), tf.greater_equal(y, zeros))
    cond3 = tf.logical_and(tf.less(x, zeros), tf.less(y, zeros))
    cond4 = tf.logical_and(tf.equal(x, zeros), tf.greater(y, zeros))
    cond5 = tf.logical_and(tf.equal(x, zeros), tf.less(y, zeros))
    zeros[tf.where(cond1)] = tf.atan(
        tf.truediv(
            y[tf.where(cond1)], x[tf.where(cond1)]
        )
    )
    zeros[tf.where(cond2)] = tf.atan(
        tf.truediv(
            y[tf.where(cond2)], x[tf.where(cond2)]
        )
    ) + np.pi
    zeros[tf.where(cond3)] = tf.atan(
        tf.truediv(
            y[tf.where(cond3)], x[tf.where(cond3)]
        )
    ) - np.pi
    zeros[tf.where(cond4)] = np.pi / 2
    zeros[tf.where(cond5)] = -np.pi / 2
    return zeros


def get_signals(phase_stepping_curves, n_periods=1):
    """Get the average a_0, the phase phi and the amplitude
    |a_1| from the phase stepping curves.

    Input:
    phase_stepping_curves is a tensorflow.Tensor with the phase stepping curves
    along the third axis, (x, y) pixels along the first two axes.

    n_periods is the number of periods used in the phase stepping.

    returns a0, phi and a1 along the last axis.
    """

    transformed = tf.batch_fft(tf.cast(phase_stepping_curves, tf.complex64))
    a0 = np.abs(transformed[:, :, 0])
    a1 = np.abs(transformed[:, :, n_periods])
    phi1 = angle(transformed[:, :, n_periods])
    return tf.concat(concat_dim=2, values=[a0, phi1, a1])
