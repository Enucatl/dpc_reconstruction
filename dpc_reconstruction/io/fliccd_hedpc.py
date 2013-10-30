"""
Read the RAW images saved by the CCDFLI camera and merge them into a single
HDF5 file.
"""

from __future__ import division, print_function

import numpy as np

from pypes.component import Component
from pypesvds.lib.packet import Packet

#number of lines in a CCD FLI header
_HEADER_LINES = 16
_RAW_IMAGES_NAME = "raw_images"

class FliRawHeaderSplitter(Component):

    """Split the stream of binary data coming from the FLI CCD raw format
    into three outputs: the filename (string), the header (binary) and the
    image data (binary)."""

    __metatype__ = "ADAPTER"

    def __init__(self, file_objects):
        super(FliRawHeaderSplitter, self).__init__()
        self.add_output("header", "lines with metadata from the camera")
        self._file_objects = file_objects
        

    def run(self):
        while True:
            self.receive("in")
            for file_object in self._file_objects:
                image_packet = Packet()
                header_packet = Packet()
                image_packet.set("file_name", file_object.name)
                lines = file_object.readlines()
                header_packet.set("data", lines[:_HEADER_LINES])
                #first byte of the last line is useless
                image_packet.set("data", lines[-1][1:])
                self.send("header", header_packet)
                self.send("out", image_packet)
            self.yield_ctrl()

class FliRawHeaderAnalyzer(Component):

    """Analyze the header and get the metadata for the picture."""

    __metatype__ = "TRANSFORMER"

    def __init__(self):
        super(FliRawHeaderAnalyzer, self).__init__()
        
    def run(self):
        while True:
            packets = self.receive_all('in')
            for packet in packets:
                header = packet.get("data")
                exposure_time = float(header[4].split()[-1])
                min_y, min_x, max_y, max_x = [
                        int(x) for x in header[-2].split()[2:]]
                packet.delete("data") #header is not useful anymore
                packet.set("min_y", min_y)
                packet.set("max_y", max_y)
                packet.set("min_x", min_x)
                packet.set("max_x", max_x)
                packet.set("exposure_time", exposure_time)
                self.send("out", packet)
            self.yield_ctrl()

class FliRaw2Numpy(Component):

    """Get the header information merged with the binary image, and pass the
    latter in numpy format."""

    __metatype__ = "TRANSFORMER"

    def __init__(self):
        super(FliRaw2Numpy, self).__init__()

    def run(self):
        while True:
            packets = self.receive_all('in')
            for packet in packets:
                header = packet.get("data")
                max_x = packet.get("max_x")
                min_x = packet.get("min_x")
                min_y = packet.get("min_y")
                max_y = packet.get("max_y")
                image = np.reshape(
                        np.frombuffer(packet.get("data"), dtype=np.uint16),
                        (max_y - min_y, max_x - min_x))
                packet.delete("data") #remove binary data
                packet.set("image", image)
                self.send("out", packet)
                print("2numpy", packet.get("file_name"))
            self.yield_ctrl()

class Printer(Component):
    __metatype__ = 'PUBLISHER'

    def __init__(self):
        Component.__init__(self)

    def run(self):
        while True:
            for data in self.receive_all('in'):
                image = data.get("image")
                print(image)
                print(image.shape)
            self.yield_ctrl()
