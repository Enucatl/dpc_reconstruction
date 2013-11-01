"""
Read the RAW images saved by the CCDFLI camera and merge them into a single
HDF5 file.
"""

from __future__ import division, print_function 

import logging
import traceback
from glob import glob
import os

import numpy as np
import pypes.component 
import pypesvds.lib.packet

#number of lines in a CCD FLI header
_HEADER_LINES = 16

log = logging.getLogger(__name__)

class FliRawReader(pypes.component.Component):

    """Split the stream of binary data coming from the FLI CCD raw format
    into three outputs: the filename (string), the header (binary) and the
    image data (binary)."""

    __metatype__ = "ADAPTER"

    def __init__(self):
        pypes.component.Component.__init__(self)

        # log successful initialization message
        log.info('pypes.component.Component Initialized: {0}'.format(
            self.__class__.__name__))
        
    def run(self):
        while True:
            data = self.receive("in")
            print(data.get_attributes().items())
            folder = data.get('data')
            if folder is None:
                self.yield_ctrl()
                continue
            input_files = sorted(glob(
                os.path.join(
                    os.path.expanduser(folder),
                    "*.raw")))
            log.info("{0} is reading {1}".format(
                self.__class__.__name__, folder))
            for input_file in input_files:
                try:
                    packet = pypesvds.lib.packet.Packet()
                    lines = open(input_file).readlines()
                    packet.set("file_name", input_file)
                    packet.set("header", lines[:_HEADER_LINES])
                    #first byte of the last line is useless
                    packet.set("image_data", lines[-1][1:])
                    log.info("read file {0}".format(input_file))
                except Exception as e:
                    log.error('pypes.component.Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    log.error(traceback.print_exc())
                self.send("out", packet)
            self.yield_ctrl()

class FliRawHeaderAnalyzer(pypes.component.Component):

    """Analyze the header and get the metadata for the picture."""

    __metatype__ = "TRANSFORMER"

    def __init__(self):
        pypes.component.Component.__init__(self)
        # log successful initialization message
        log.info('pypes.component.Component Initialized: {0}'.format(
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
                    packet.delete("header") #header is not useful anymore
                    packet.set("min_y", min_y)
                    packet.set("max_y", max_y)
                    packet.set("min_x", min_x)
                    packet.set("max_x", max_x)
                    packet.set("exposure_time", exposure_time)
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    log.error(traceback.print_exc())
                # send the document to the next component
                self.send("out", packet)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()

class FliRaw2Numpy(pypes.component.Component):

    """Get the header information merged with the binary image, and pass the
    latter in numpy format."""

    __metatype__ = "TRANSFORMER"

    def __init__(self):
        pypes.component.Component.__init__(self)
        # log successful initialization message
        log.info('pypes.component.Component Initialized: {0}'.format(
            self.__class__.__name__))

    def run(self):
        while True:
            packets = self.receive_all('in')
            for packet in packets:
                try:
                    max_x = packet.get("max_x")
                    min_x = packet.get("min_x")
                    min_y = packet.get("min_y")
                    max_y = packet.get("max_y")
                    image = np.reshape(
                            np.frombuffer(packet.get("image_data"), dtype=np.uint16),
                            (max_y - min_y, max_x - min_x))
                    packet.delete("image_data") #remove binary data
                    packet.set("image", image)
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    log.error(traceback.print_exc())
                # send the document to the next component
                self.send("out", packet)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()
