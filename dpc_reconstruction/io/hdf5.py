"""
Output from numpy to hdf5 datasets

"""

from __future__ import division, print_function

import logging
import h5py
import os

import pypes.component
import pypesvds.lib.packet

log = logging.getLogger(__name__)

class Hdf5Writer(pypes.component.Component):
    """Output an image to HDF5, with all of its metadata.

    mandatory input packet attributes:
    - full_path: path of the original raw file, used to calculate the
    hdf5 path and the name of the dataset
    - data: containing the image as a numpy array

    optional input packet attributes:
    - any: will be added as attributes for the hdf5 Dataset

    parameters:
    - overwrite: [default: False] overwrite the dataset if it already
    exists in the hdf5 file
    - group: [default: /] h5 Group used to store the datasets

    output:
    - None, writes to disk

    """

    __metatype__ = "PUBLISHER"

    def __init__(self):
        pypes.component.Component.__init__(self)
        # remove the output port since this is a publisher
        self.remove_output('out')
        self.set_parameter("overwrite", False)  # overwrite existing datasets
        self.set_parameter("group", "/")  # group inside the hdf file
        log.debug('Component Initialized: {0}'.format(
            self.__class__.__name__))

    def run(self):
        while True:
            overwrite = self.get_parameter("overwrite")
            packet = self.receive("in")
            try:
                file_name = packet.get("full_path")
                folder_name, tail_name = os.path.split(file_name)
                output_file_name = folder_name + ".hdf5"
                output_file = h5py.File(output_file_name)
                output_group = output_file.require_group(
                    self.get_parameter("group"))
                dataset_name = os.path.splitext(tail_name)[0]
                if dataset_name in output_group and overwrite:
                    del output_group[dataset_name]
                elif dataset_name in output_group and not overwrite:
                    log.debug(
                        "{0}: dataset {1} exists, not overwriting".format(
                            self.__class__.__name__, dataset_name))
                    output_file.close()
                    self.yield_ctrl()
                    continue
                output_group[dataset_name] = packet.get("data")
                packet.delete("data")
                log.debug("%s: written dataset %s to file %s group %s",
                          self.__class__.__name__,
                          dataset_name,
                          output_file_name,
                          self.get_parameter("group"))
                for key, value in packet.get_attributes().iteritems():
                    log.debug("%s: adding attribute to dataset %s: %s=%s",
                              self.__class__.__name__,
                              dataset_name,
                              key, value)
                    output_group[dataset_name].attrs[key] = value
                if output_file:
                    output_file.close()
            except:
                log.error('Component Failed: %s',
                          self.__class__.__name__, exc_info=True)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()


class Hdf5Reader(pypes.component.Component):
    """
    Read all the datasets in a h5py.Group.
    The files are stored in self.files so that they are not prematurely
    garbage collected.

    mandatory input (not a packet):
    - file_name: path of the hdf5 file

    parameters:
    - group: [default: /] h5 Group to be read

    output packet attributes:
    - file_names: the list of the paths of the input files
    - data: the list of h5py.Datasets read from the file(s)

    """

    __metatype__ = 'ADAPTER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)

        #read all the datasets in this group
        self.set_parameter("group", "/")

        #store files so that they are not garbage collected
        self.files = []

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:
            # for each file name string waiting on our input port
            file_names = list(self.receive_all('in'))
            datasets = []
            group_name = self.get_parameter("group")
            packet = pypesvds.lib.packet.Packet()
            for file_name in file_names:
                try:
                    log.debug('{0} reading file {1}'.format(
                        self.__class__.__name__, file_name))
                    input_file = h5py.File(file_name)
                    input_group = input_file[group_name]
                    #save files so that they are not garbage collected
                    self.files.append(input_file)
                    datasets.extend([dataset
                                     for dataset in input_group.itervalues()
                                     if isinstance(dataset, h5py.Dataset)])
                    log.debug('{0} found {1} datasets'.format(
                        self.__class__.__name__, len(datasets)))
                except:
                    log.error('Component Failed: %s',
                              self.__class__.__name__, exc_info=True)
            packet.set("data", datasets)
            packet.set("file_names", file_names)
            # send the packet to the next component
            self.send('out', packet)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()

    def __del__(self):
        """close files when the reference count is 0."""
        for f in self.files:
            log.debug('{0} closing file {1}'.format(
                self.__class__.__name__, f.filename))
            if f:
                f.close()
            else:
                log.debug('{0} file {1} was already closed'.format(
                    self.__class__.__name__, f.filename))


def output_name(files, component_name):
    """
    Get the name of the output hdf5 file from a list of input files.

    """
    first_file_name, _ = os.path.splitext(os.path.basename(files[0]))
    last_file_name = os.path.splitext(os.path.basename(files[-1]))[0]
    dir_name = os.path.dirname(files[0])
    if len(files) > 1:
        output_file_name = os.path.join(
            dir_name, "{0}_{1}/{2}".format(
                first_file_name, last_file_name, component_name))
    else:
        output_file_name = os.path.join(
            dir_name, "{0}/{1}".format(first_file_name, component_name))
    return output_file_name
