import logging
import numpy as np
import tensorflow as tf

log = logging.getLogger(__name__)


def compare_sample_to_flat(sample, flat):
    a0_flat = flat[:, :,  0]
    phi_flat = flat[:, :, 1]
    a1_flat = flat[:, :, 2]
    sample[:, :, 0] /= a0_flat
    sample[:, :, 1] -= phi_flat
    sample[:, :, 2] /= a1_flat / sample[:, :, 0]
    # unwrap the phase values
    sample[..., 1] = tf.mod(
        sample[..., 1] + np.pi, 2 * np.pi
    ) - np.pi
    return sample
