"""Separate the flats from the data and merge them again after the
analysis."""

from __future__ import division, print_function

import logging
import numpy as np

import pypes.component

log = logging.getLogger(__name__)


class SplitFlatSample(pypes.component.Component):
    """
    Send the flat data to the out2 port and the sample data to the out port.

    mandatory input packet attributes:
        - flat: flat data
        - sample: sample data

    optional input packet attributes:
        - None

    parameters:
        - group: hdf5 group with the raw images

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
        self.set_parameter("group", "/")

        # log successful initialization message
        log.debug('Component Initialized: %s',
                  self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # for each packet waiting on our input port
            packet = self.receive("in")
            group = self.get_parameter("group")
            try:
                for file_name in packet.get('sample'):
                    new_packet = pypes.packet.Packet()
                    new_packet.set("file_name", file_name)
                    new_packet.set("data", group)
                    log.debug("%s sending out sample file %s group %s",
                              self.__class__.__name__,
                              file_name,
                              group)
                    self.send('out', new_packet)
                for file_name in packet.get('flat'):
                    new_packet = pypes.packet.Packet()
                    new_packet.set("file_name", file_name)
                    new_packet.set("data", group)
                    log.debug("%s sending out flat file %s group %s",
                              self.__class__.__name__,
                              file_name,
                              group)
                    self.send('out2', new_packet)
            except:
                log.error('Component Failed: %s', self.__class__.__name__,
                          exc_info=True)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()


class MergeFlatSample(pypes.component.Component):
    """
    Combine the flat field data with the sample data to get the final DPC
    signal reconstruction.

    mandatory input packet attributes:
        in  - data: the curve parameters with the sample
        in2 - data: the curve parameters without the sample (flats)

    optional input packet attributes:
        - None

    parameters:
        - None

    output packet attributes:
        - data: the sample combined with the flat after division/subtraction

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)

        self.add_input('in2', 'input for the flat packet')

        # log successful initialization message
        log.debug('Component Initialized: %s',
                  self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # for each packet waiting on our input port
            flat_packet = self.receive('in2')
            sample_packet = self.receive('in')
            if not flat_packet or not sample_packet:
                self.yield_ctrl()
                continue
            else:
                try:
                    flat = flat_packet.get('data')
                    sample = sample_packet.get('data')
                    a0_flat = flat[..., 0, np.newaxis]
                    phi_flat = flat[..., 1, np.newaxis]
                    a1_flat = flat[..., 2, np.newaxis]
                    sample[..., 0] /= a0_flat
                    sample[..., 1] -= phi_flat
                    sample[..., 2] = sample[..., 2] / a1_flat / sample[..., 0]
                    # unwrap the phase values
                    sample[..., 1] = np.mod(
                        sample[..., 1] + np.pi, 2 * np.pi) - np.pi
                    sample_packet.set('data', sample)
                    visibility_map = np.tile(
                        2 * a1_flat / a0_flat,
                        (1, 1, sample.shape[2]))
                    flat_curves = flat_packet.get("phase stepping curves")
                    median_flat = np.median(flat_curves, axis=2)
                    flat_median_curve = np.tile(
                        np.expand_dims(median_flat, 2),
                        (1, 1, sample.shape[2], 1))
                    log.debug("tiled flat shape %s", flat_median_curve.shape)
                    sample_packet.set('visibility', visibility_map)
                    sample_packet.set('flat median phase stepping curves',
                                      flat_median_curve)
                    sample_packet.set(
                        'parameters',
                        np.tile(np.expand_dims(flat, 2),
                                (1, 1, sample.shape[2], 1)))
                    log.debug('''%s: merged flat and data and unwrapped the
                    phase values. Created dataset with shape %s''',
                              self.__class__.__name__, sample.shape)
                    log.debug(
                        'shapes sample %s, visibility %s, parameters %s',
                        sample.shape, visibility_map.shape, a0_flat.shape)
                    log.debug(
                        'phase stepping curves shape %s',
                        sample_packet.get("phase stepping curves").shape)
                except:
                    log.error('Component Failed: %s', self.__class__.__name__,
                              exc_info=True)

                # send the packet to the next component
                self.send('out', sample_packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
