import logging
import tensorflow as tf

log = logging.getLogger(__name__)


def visibility(data):
    return 2 * data[:, :, 2] / data[:, :, 0]
