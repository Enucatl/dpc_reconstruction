from __future__ import division, print_function

import logging

import pypes.component

log = logging.getLogger(__name__)

class SplitFlats(pypes.component.Component):
    """
    Send the flat data to the out2 port and the sample data to the out port.

    mandatory input packet attributes:
        - flat: flat data
        - sample: sample data

    optional input packet attributes:
        - None

    parameters:
        - None

    output ports:
        out  - sample data
        out2 - flat data

    """

    # defines the type of component we're creating.
    __metatype__ = 'ADAPTER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)
        
        self.add_output('out2', 'output for the flat data')

        # log successful initialization message
        log.debug('pypes.component.Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # for each packet waiting on our input port
            for packet in self.receive_all('in'):
                try:
                    packet.send('out', packet.get('sample'))
                    packet.send('out2', packet.get('flat'))
                    pass
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__,
                            exc_info=True)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
