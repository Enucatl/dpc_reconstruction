"""
Read the RAW images saved by the CCD FLI camera in OFLG/U210
"""

from __future__ import division, print_function

import logging

import numpy as np
import pypes.component

#number of lines in a CCD FLI header
_HEADER_LINES = 16

log = logging.getLogger(__name__)


class FliRawReader(pypes.component.Component):

    """

    mandatory input packet attributes:
        - data: the binary contents of the file

    optional input packet attributes:
        - None

    parameters:
        - None

    output packet attributes:
        - data: raw binary string containing only the image data
          (dtype=uint16), without the header
        - header: string containing the header only
    """

    __metatype__ = "ADAPTER"

    def __init__(self):
        pypes.component.Component.__init__(self)

        # log successful initialization message
        log.debug('Component Initialized: {0}'.format(
            self.__class__.__name__))

    def run(self):
        while True:
            packet = self.receive("in")
            data = packet.get('data')
            if data is None:
                self.yield_ctrl()
                continue
            lines = data.splitlines()
            log.debug("{0} is reading {1} lines".format(
                self.__class__.__name__, len(lines)))
            try:
                packet.set("header", lines[:_HEADER_LINES])
                #first byte of the last line is useless
                packet.set("data", lines[-1][1:])
            except:
                log.error('Component Failed: %s', self.__class__.__name__,
                          exc_info=True)
            self.send("out", packet)
            self.yield_ctrl()


class FliRawHeaderAnalyzer(pypes.component.Component):

    """Analyze the header and get the metadata for the picture.

    mandatory input packet attributes:
        - header: string with the header of the raw file

    optional input packet attributes:
        - None

    parameters:
        - None

    output packet attributes:
        - min_y: ...
        - max_y: ...
        - min_x: ...
        - max_x: ROI limits (pixel numbers)
        - exposure_time: exposure time as saved by the camera

    """

    __metatype__ = "TRANSFORMER"

    def __init__(self):
        pypes.component.Component.__init__(self)
        # log successful initialization message
        log.debug('Component Initialized: {0}'.format(
            self.__class__.__name__))

    def run(self):
        while True:
            packets = self.receive_all('in')
            for packet in packets:
                try:
                    header = packet.get("header")
                    exposure_time = float(header[4].split()[-1])
                    min_y, min_x, max_y, max_x = [
                        int(x) for x in header[-2].split()[2:]]
                    packet.delete("header")  # header is not useful anymore
                    packet.set("min_y", min_y)
                    packet.set("max_y", max_y)
                    packet.set("min_x", min_x)
                    packet.set("max_x", max_x)
                    packet.set("exposure_time", exposure_time)
                    log.debug("{0} read header".format(
                        self.__class__.__name__))
                except:
                    log.error('Component Failed: %s', self.__class__.__name__,
                              exc_info=True)
                # send the document to the next component
                self.send("out", packet)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()


class FliRaw2Numpy(pypes.component.Component):

    """Get the header information and the binary raw image, and convert the
    latter to a numpy array.

    mandatory input packet attributes:
        - data: the image raw binary string
        - min_y: ...
        - max_y: ...
        - min_x: ...
        - max_x: ROI limits (pixel numbers)

    optional input packet attributes:
        - None

    parameters:
        - None

    output packet attributes:
        - data: the image as a 2D numpy array

    """

    __metatype__ = "TRANSFORMER"

    def __init__(self):
        pypes.component.Component.__init__(self)
        # log successful initialization message
        log.debug('Component Initialized: {0}'.format(
            self.__class__.__name__))

    def run(self):
        while True:
            packet = self.receive('in')
            try:
                max_x = packet.get("max_x")
                min_x = packet.get("min_x")
                min_y = packet.get("min_y")
                max_y = packet.get("max_y")
                image = np.reshape(
                    np.fromstring(packet.get("data"), dtype=np.uint16),
                    (max_y - min_y, max_x - min_x),
                    order='F')
                log.debug("{0}: image with shape {1}".format(
                    self.__class__.__name__, image.shape))
                packet.set("data", image)
            except:
                log.error('Component Failed: %s', self.__class__.__name__,
                          exc_info=True)
            # send the document to the next component
            self.send("out", packet)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()
