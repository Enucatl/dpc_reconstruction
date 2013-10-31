"""
Output from numpy to hdf5 datasets

"""

from __future__ import division, print_function

import logging
import traceback
import h5py
import os

import pypes.component 

log = logging.getLogger(__name__)

class Hdf5Writer(pypes.component.Component):

    """Output an image to HDF5, with all of its metadata."""

    __metatype__ = "PUBLISHER"

    def __init__(self):
        pypes.component.Component.__init__(self)
        self.set_parameter("overwrite", False)
        
    def run(self):
        while True:
            overwrite = self.get_parameter("overwrite")
            packets = self.receive_all("in")
            for packet in packets:
                try:
                    file_name = packet.get("file_name")
                    folder_name, tail_name = os.path.split(file_name)
                    output_name = folder_name + ".hdf5"
                    output_file = h5py.File(output_name)
                    packetset_name = os.path.splitext(tail_name)[0]
                    if packetset_name in output_file and overwrite:
                        del output_file[packetset_name]
                    elif packetset_name in output_file and not overwrite:
                        output_file.close()
                        self.yield_ctrl()
                        continue
                    output_file[packetset_name] = packet.get("image")
                    packet.delete("image")
                    for key, value in packet.get_attributes().iteritems():
                        output_file[packetset_name].attrs[key] = value
                    output_file.close()
                except Exception as e:
                    log.error('pypes.component.Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    log.error(traceback.print_exc())

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
