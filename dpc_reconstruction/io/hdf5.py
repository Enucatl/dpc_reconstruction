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
        # remove the output port since this is a publisher
        self.remove_output('out')
        self.set_parameter("overwrite", False)
        log.debug('pypes.component.Component Initialized: {0}'.format(
            self.__class__.__name__))
        
    def run(self):
        while True:
            overwrite = self.get_parameter("overwrite")
            packet = self.receive("in")
            try:
                file_name = packet.get("file_name")
                folder_name, tail_name = os.path.split(file_name)
                output_name = folder_name + ".hdf5"
                output_file = h5py.File(output_name)
                dataset_name = os.path.splitext(tail_name)[0]
                if dataset_name in output_file and overwrite:
                    del output_file[dataset_name]
                elif dataset_name in output_file and not overwrite:
                    log.debug("{0}: dataset {1} exists, not overwriting".format(
                        self.__class__.__name__, dataset_name))
                    output_file.close()
                    self.yield_ctrl()
                    continue
                output_file[dataset_name] = packet.get("image")
                packet.delete("image")
                log.debug("{0}: written dataset {1} in file {2}".format(
                    self.__class__.__name__, dataset_name, output_name))
                for key, value in packet.get_attributes().iteritems():
                    output_file[dataset_name].attrs[key] = value
                output_file.close()
            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__,
                        exc_info=True)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()
