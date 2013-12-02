"""Stack or split hdf5 datasets so that they can easier manipulated.

"""

from __future__ import division, print_function

import logging
import numpy as np

import pypes.component

from dpc_reconstruction.io.hdf5 import output_name 

log = logging.getLogger(__name__)

class Stacker(pypes.component.Component):
    """
    mandatory input packet attributes:
        - data: list of h5py.Dataset or numpy arrays

    optional input packet attributes:
        - None

    parameters:
        - None

    output packet attributes:
        - data: a numpy array with the input datasets stacked along the last
          axis.
    """
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)
        
        # log successful initialization message
        log.debug('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:
            # for each packet waiting on our input port
            packet = self.receive('in')
            try:
                datasets = [dataset for dataset in packet.get('data')]
                log.debug('{0} datasets[0] found with shape {1}'.format(
                    self.__class__.__name__, datasets[0].shape))
                data = np.dstack(datasets)
                packet.set('data', data)
                file_names = packet.get('file_names')
                packet.delete("file_names")
                output_file_name = output_name(
                    file_names, self.__class__.__name__)
                packet.set("full_path", output_file_name)
                #add info from first dataset
                for key, value in datasets[0].attrs.iteritems():
                    packet.set(key, value)
                log.debug('{0} dataset created with shape {1}'.format(
                    self.__class__.__name__, data.shape))
            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__,
                        exc_info=True)

            # send the packet to the next component
            self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

class PhaseStepsSplitter(pypes.component.Component):
    """
    Split a 3D array into chunks the size of "phase_steps"
    Raises an exception if phase_steps is not a divisor of array.shape[2].

    mandatory input packet attributes:
        - data: a 3d dataset

    optional input packet attributes:
        - None

    parameters:
        - phase_steps: [default: 1] number of phase steps

    output packet attributes:
        - data: a 4d dataset, with the phase steps along the last axis

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)
        
        # Setup any user parameters required by this component 
        # 2nd arg is the default value, 3rd arg is optional list of choices
        self.set_parameter('phase_steps', 1)

        # log successful initialization message
        log.debug('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            phase_steps = self.get_parameter('phase_steps')             

            # for each packet waiting on our input port
            for packet in self.receive_all('in'):
                try:
                    data = packet.get('data')
                    chunk_size = data.shape[2] // phase_steps
                    log.debug(
                        '{0} splitting data with shape {1} into {2} chunks'.format(
                        self.__class__.__name__, data.shape, chunk_size))
                    split_data = np.split(data, chunk_size, axis=2)
                    #add axis to each dataset
                    added_axis = [np.expand_dims(array, axis=2)
                                  for array in split_data]
                    concatenated = np.concatenate(added_axis, axis=2)
                    packet.set('data', concatenated)
                    log.debug('{0} dataset created with shape {1}'.format(
                        self.__class__.__name__, concatenated.shape))
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__,
                            exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
