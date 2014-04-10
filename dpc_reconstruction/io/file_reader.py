"""Components to read binary files.

"""

from __future__ import division, print_function

import logging
import os

import pypes.component
import pypes.packet.packet

log = logging.getLogger(__name__)


class FileReader(pypes.component.Component):

    """Read a file from the disk and send as a packet.

    mandatory input:
        - the file name as a string

    optional input:
        - None

    parameters:
        - mode: (default: "rb") open mode for the file
        - remove_source: (default: False) remove the file after reading it

    output packet with two attributes:
        - full_path: absolute path of the file
        - data: raw contents of the file
    """

    __metatype__ = "ADAPTER"

    def __init__(self):
        pypes.component.Component.__init__(self)
        # remove the output port since this is a publisher
        self.set_parameter("mode", "rb")
        self.set_parameter("remove_source", False)
        log.debug('Component Initialized: {0}'.format(
            self.__class__.__name__))

    def run(self):
        while True:
            file_name = self.receive("in")
            mode = self.get_parameter("mode")
            packet = pypes.packet.packet.Packet()
            try:
                full_path = os.path.abspath(file_name)
                if not os.path.exists(full_path):
                    raise OSError("file {0} not found!".format(
                        full_path))
                data = open(full_path, mode).read()
                if self.get_parameter("remove_source"):
                    os.remove(full_path)
                    log.debug("{0} removed file {1}".format(
                        self.__class__.__name__, full_path))
                log.debug('{0} read file {1}'.format(
                    self.__class__.__name__, full_path))
                packet.set('data', data)
                packet.set('full_path', full_path)
                self.send('out', packet)
            except:
                log.error('Component Failed: %s', self.__class__.__name__,
                          exc_info=True)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()
