from __future__ import division, print_function

import logging

import pypes.component

import matplotlib.pyplot as plt

log = logging.getLogger(__name__)

class VisibilityPlotter(pypes.component.Component):
    """
    mandatory input packet attributes:
        - data: the visibility values for each pixel

    optional input packet attributes:
        - min_y: ...
        - max_y: ...
        - min_x: ...
        - max_x: ROI limits (pixel numbers)

    parameters:
        - None

    output packet attributes:
        No output (display on screen)

    """

    # defines the type of component we're creating.
    __metatype__ = 'PUBLISHER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)
        
        # Optionally add/remove component ports
        self.remove_output('out')

        # log successful initialization message
        log.debug('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # for each packet waiting on our input port
            packet = self.receive('in')
            try:
                visibility = packet.get("data")
                log.debug("{0}: got visibility data with shape {1}".format(
                    self.__class__.__name__, visibility.shape))
                image = plt.imshow(visibility, cmap=plt.cm.RdYlGn)
                plt.colorbar(image)
                plt.show()
            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__,
                        exc_info=True)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
