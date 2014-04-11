"""
Functions for reconstructing the DPC images from the raw phase steps.

"""

from __future__ import division, print_function

import logging
import numpy as np

import pypes.component

log = logging.getLogger(__name__)


def get_signals(phase_stepping_curves, n_periods=1):
    """Get the average a_0, the phase phi and the amplitude
    |a_1| from the phase stepping curves.

    Input:
    phase_stepping_curves is a numpy array with the phase stepping curves
    along the last axis (axis=-1).

    n_periods is the number of periods used in the phase stepping

    returns a0, phi and a1 along the last axis
    """

    transformed = np.fft.rfft(phase_stepping_curves)
    a0 = np.abs(transformed[..., 0])
    a1 = np.abs(transformed[..., n_periods])
    phi1 = np.angle(transformed[..., n_periods])
    shape = phase_stepping_curves.shape[:-1] + (3,)
    output = np.zeros(shape)
    output[..., 0] = a0
    output[..., 1] = phi1
    output[..., 2] = a1
    return output


class FourierAnalyzer(pypes.component.Component):
    """
    mandatory input packet attributes:
        - data: numpy array with the phase stepping curves along the last
          axis. Note that the "last" phase stepping point, corresponding to
          an angle of 2pi must NOT be included.

    optional input packet attributes:
        - None

    parameters:
        - n_periods: [default: 1] the number of periods
        used in the phase stepping

    output packet attributes:
        - data: a numpy array with the last axis of length 3:
            0 = absorption
            1 = phase
            2 = dark field
    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)

        self.set_parameter("n_periods", 1)

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # for each packet waiting on our input port
            n_periods = self.get_parameter("n_periods")

            for packet in self.receive_all('in'):
                try:
                    data = packet.get("data")
                    signals = get_signals(data, n_periods=n_periods)
                    packet.set("data", signals)
                    packet.set("phase stepping curves", data)
                    log.debug('{0} created a dataset with shape {1}'.format(
                        self.__class__.__name__, signals.shape))
                except:
                    log.error('Component Failed: %s', self.__class__.__name__,
                              exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
