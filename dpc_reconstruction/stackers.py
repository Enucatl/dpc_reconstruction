"""Stack or split hdf5 datasets so that they can easier manipulated.

"""

import logging

import pypes.component

log = logging.getLogger(__name__)

class DatasetStacker(pypes.component.Component):
    # stacks all the 2d dataset into a single 3d dataset with numpy.dstack
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
                data = np.dstack([dataset for dataset in packet.get('data')])
                packet.set('data', data)
                log.debug('{0} dataset shape {1}'.format(
                    self.__class__.__name__, dataset.shape))
            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__,
                        exc_info=True)

            # send the packet to the next component
            self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
