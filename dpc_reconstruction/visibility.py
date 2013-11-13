from __future__ import division, print_function

import logging
import os

import pypes.component

log = logging.getLogger(__name__)

class VisibilityCalculator(pypes.component.Component):
    """
    mandatory input packet attributes:
        - data: a dataset with the last axis of length 3:
            0 = absorption
            1 = phase
            2 = dark field
        - file_names: list of files that had the original datasets, used to
          calculate the output hdf5 file for the Hdf5Writer

    optional input packet attributes:
        - None

    parameters:
        - None

    output packet attributes:
        - data: a dataset with one less dimensions than the original, with
          the visibility calculated for each pixel

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
                    data = packet.get("data")
                    visibility = 2 * data[..., 2] / data[..., 0]
                    packet.set("data", visibility)
                    files = packet.get("file_names")
                    first_file_name, ext = os.path.splitext(os.path.basename(files[0]))
                    last_file_name = os.path.splitext(os.path.basename(files[-1]))[0]
                    dir_name = os.path.dirname(files[0])
                    if len(files) > 1:
                        output_file_name = os.path.join(
                                dir_name, "{0}_{1}/{2}".format(
                                    first_file_name, last_file_name,
                                    self.__class__.__name__))
                    else:
                        output_file_name = os.path.join(
                                dir_name, "{0}/{1}".format(
                                    first_file_name, 
                                    self.__class__.__name__))
                    packet.set("full_path", output_file_name)
                    log.debug('{0} created a dataset with shape {1}'.format(
                        self.__class__.__name__, visibility.shape))
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__,
                            exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
