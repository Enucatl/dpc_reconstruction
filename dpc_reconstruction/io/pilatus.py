"""Components for the shadobox detector."""

from __future__ import division, print_function

import logging
import numpy as np
import os

import pypes.component

log = logging.getLogger(__name__)


class PilatusToNumpy(pypes.component.Component):
    """
    mandatory input packet attributes:
        - data: Binary content of the image file

    optional input packet attributes:
        - none:

    parameters:
        - roi: cut the image down to a roi

    output packet attributes:
        - data: hdf5 data set

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)

        self.set_parameter("roi", [0, 0, 486, 618])
        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)


    def run(self):
        # Define our components entry point
        while True:

            # for each packet waiting on our input port
            roi = self.get_parameter("roi")
            for packet in self.receive_all('in'):
                try:
                    raw_data = packet.get('data')
                    file_name = packet.get("file_name")
                    packet.set("raw_file_name", file_name)
                    packet.set("file_name",
                       os.path.dirname(file_name) + ".hdf5")
                    data = np.fromstring(
                        raw_data,
                        dtype='int32'
                        ).reshape((roi[2] - roi[0], roi[3] - roi[1]))
                    # check order of header entries to correctly rearrange
                    # array
                    log.debug('{0} read dataset with shape {1}'.format(
                        self.__class__.__name__, data.shape))
                    packet.set('data', data)
                except:
                    log.error('Component Failed: %s', self.__class__.__name__,
                              exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
