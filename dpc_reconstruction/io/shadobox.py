
from __future__ import division, print_function

import logging
import numpy as np

import pypes.component

log = logging.getLogger(__name__)

class ShadoboxToNumpy(pypes.component.Component):
    """
    mandatory input packet attributes:
        - data: Binary content of the image file

    optional input packet attributes:
        - none: 

    parameters:
        - none:

    output packet attributes:
        - data: hdf5 data set

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)
        
        # log successful initialization message
        log.debug('pypes.component.Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # for each packet waiting on our input port
            for packet in self.receive_all('in'):
                try:
                    raw_data = packet.get('data')
                    data_array = np.fromstring(raw_data,'uint16')
                    header = data_array[:2]
                    # cheack order of header entries to correctly rearrange
                    # array
                    data = np.reshape(data_array[2:], (header[0],
                                                       header[1]))
                    log.debug('{0} read dataset with shape {1}'.format(
                        self.__class__.__name__, data.shape))
                    packet.set('header', header)
                    packet.set('data', data)
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__,
                            exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
