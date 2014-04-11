"""Stack or split hdf5 datasets so that they can easier manipulated.

"""

from __future__ import division, print_function

import logging
import numpy as np

import pypes.component
import pypes.packet
from pypes.plugins.hdf5 import output_name

log = logging.getLogger(__name__)


def flatten(l, ltypes=(list, tuple)):
    """Flatten nested list. From
    http://rightfootin.blogspot.ch/2006/09/more-on-python-flatten.html

    """
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)


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
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:
            # for each packet waiting on our input port
            packets = list(self.receive_all("in"))
            try:
                datasets = flatten([packet.get("data")
                                    for packet in packets])
                file_names = flatten([packet.get("file_name")
                                      for packet in packets])
                log.debug('{0} datasets found with shape {1}'.format(
                    self.__class__.__name__, datasets[0].shape))
                data = np.dstack(datasets)
                packet = pypes.packet.Packet()
                packet.set("data", data)
                output_file_name = output_name(
                    file_names, self.__class__.__name__)
                packet.set("full_path", output_file_name)

                #add info from first dataset
                for key, value in datasets[0].attrs.items():
                    packet.set(key, value)
                log.debug('{0} dataset created with shape {1}'.format(
                    self.__class__.__name__, data.shape))
            except:
                log.error('Component Failed: %s',
                          self.__class__.__name__, exc_info=True)

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
        log.debug('Component Initialized: %s', self.__class__.__name__)

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
                        '{0} split data with shape {1} into {2} chunks'.format(
                            self.__class__.__name__, data.shape, chunk_size))
                    split_data = np.split(data, chunk_size, axis=2)
                    #add axis to each dataset
                    added_axis = [np.expand_dims(array, axis=2)
                                  for array in split_data]
                    concatenated = np.concatenate(added_axis, axis=2)
                    packet.set('data', concatenated)
                    log.debug('{0} dataset created with shape {1}'.format(
                        self.__class__.__name__, concatenated.shape))
                except:
                    log.error('Component Failed: %s',
                              self.__class__.__name__, exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
