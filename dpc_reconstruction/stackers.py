"""Stack or split hdf5 datasets so that they can easier manipulated.

"""

from __future__ import division, print_function

import logging
import numpy as np

import pypes.component

log = logging.getLogger(__name__)

class Stacker(pypes.component.Component):
    """
    mandatory input packet attributes:
        - data: list of h5py.Dataset or numpy arrays

    optional input packet attributes:
        - None

    parameters:
        - None

    output packet attributes:
        - data: a numpy array with the input datasets stacked along the last
          axis.
    """
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
            packet = self.receive('in')
            try:
                datasets = [dataset for dataset in packet.get('data')]
                log.debug('{0} datasets[0] found with shape {1}'.format(
                    self.__class__.__name__, datasets[0].shape))
                data = np.dstack(datasets)
                packet.set('data', data)
                #add info from first dataset
                for key, value in datasets[0].attrs.iteritems():
                    packet.set(key, value)
                log.debug('{0} dataset created with shape {1}'.format(
                    self.__class__.__name__, data.shape))
            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__,
                        exc_info=True)

            # send the packet to the next component
            self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
