"""
Input a filename as a string, it opens the file (default binary mode) and
builds a packet with a 'data' attribute. The data are a stream with the
filename as the first line followed by the file contents.

This structure keeps compatibility with the HTTP protocol easy. If a paster
server is running, this component is equivalent to a post request, for
example:

    raw_image = file_name + "\n" + open(file_name, 'rb')
            headers = {'content-encoding': 'gzip'}
            stringio = StringIO.StringIO()
            gzip_file = gzip.GzipFile(fileobj=stringio, mode='w')
            gzip_file.write(os.path.abspath(file_name))
            gzip_file.write("\n")
            gzip_file.write(raw_image.read())
            gzip_file.close()
            requests.post(server,
                    data=stringio.getvalue(),
                    headers=headers)

"""

from __future__ import division, print_function

import logging
import traceback
import h5py
import os

import pypes.component 
import pypesvds.lib.packet

log = logging.getLogger(__name__)

class FileReader(pypes.component.Component):

    """Read a file from the disk."""

    __metatype__ = "ADAPTER"

    def __init__(self):
        pypes.component.Component.__init__(self)
        # remove the output port since this is a publisher
        self.set_parameter("mode", "rb")
        self.set_parameter("remove_source", False)
        log.debug('pypes.component.Component Initialized: {0}'.format(
            self.__class__.__name__))
        
    def run(self):
        while True:
            file_name = self.receive("in")
            mode = self.get_parameter("mode")
            packet = pypesvds.lib.packet.Packet()
            try:
                full_path = os.path.abspath(file_name)
                if not os.path.exists(full_path):
                    raise OSError("file {0} not found!".format(
                        full_path))
                data = full_path + "\n" + open(full_path, mode).read()
                if self.get_parameter("remove_source"):
                    os.remove(full_path)
                    log.debug("{0} removed file {1}".format(
                        self.__class__.__name__, full_path))
                log.debug('{0} read file {1}'.format(
                    self.__class__.__name__, full_path))
                packet.set('data', data)
                self.send('out', packet)
            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__,
                        exc_info=True)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()
