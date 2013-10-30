"""
Output from numpy to hdf5 datasets

"""

from __future__ import division, print_function

import h5py
import os

from pypes.component import Component

class Hdf5Publisher(Component):

    """Output an image to HDF5, with all of its metadata."""

    __metatype__ = "PUBLISHER"

    def __init__(self, overwrite):
        super(Hdf5Publisher, self).__init__()
        self._overwrite = overwrite
        
    def run(self):
        while True:
            packets = self.receive_all("in")
            for packet in packets:
                file_name = packet.get("file_name")
                print("writing", file_name)
                folder_name, tail_name = os.path.split(file_name)
                output_name = folder_name + ".hdf5"
                output_file = h5py.File(output_name)
                packetset_name = os.path.splitext(tail_name)[0]
                if packetset_name in output_file and self._overwrite:
                    del output_file[packetset_name]
                elif packetset_name in output_file and not self._overwrite:
                    output_file.close()
                    self.yield_ctrl()
                    continue
                output_file[packetset_name] = packet.get("image")
                packet.delete("image")
                for key, value in packet.get_attributes().iteritems():
                    output_file[packetset_name].attrs[key] = value
                output_file.close()
            self.yield_ctrl()
