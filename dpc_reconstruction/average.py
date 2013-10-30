"""Average the images, e.g. from multiple flats.

"""

import numpy as np

def average(dataset, axis=-1):
    """Use the median to average all the images along the last axis.
    The median is more robust than the mean against outliers.

    """
    return np.median(dataset, axis=axis)
