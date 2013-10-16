"""Average the images, e.g. from multiple flats.

"""

import numpy as np

def average(list_of_images, axis=2):
    """Use the median to average all the images along the second axis.
    The median is more robust than the mean against outliers.

    """
    return [np.median(image, axis=axis) for image in list_of_images]
