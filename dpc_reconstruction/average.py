"""Average the images, e.g. from multiple flats.

"""
from __future__ import division, print_function

import numpy as np
import logging

import pypes.component

log = logging.getLogger(__name__)

class Average(pypes.component.Component):
    """
    mandatory input packet attributes:
        - data: the n-dimensional data to average

    optional input packet attributes:
        - None

    parameters:
        - axis: [default: 2] axis along which to perform the averaging

    output packet attributes:
        - data: the (n-1)-dimensional dataset, averaged along one axis

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)
        
        # Setup any user parameters required by this component 
        # 2nd arg is the default value, 3rd arg is optional list of choices
        self.set_parameter('axis', 2)

        # log successful initialization message
        log.debug('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:
            axis = self.get_parameter('axis')             

            # for each packet waiting on our input port
            for packet in self.receive_all('in'):
                try:
                    data = packet.get('data')
                    averaged = average(data, axis=axis)
                    packet.set('data', averaged)
                    log.debug('{0} dataset created with shape {1}'.format(
                        self.__class__.__name__, averaged.shape))
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__,
                            exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

def average(dataset, axis=-1):
    """Use the median to average all the images along the axis=axis
    (defaults to last).
    The median is more robust than the mean with respect to outliers.

    """
    return np.median(dataset, axis=axis)
