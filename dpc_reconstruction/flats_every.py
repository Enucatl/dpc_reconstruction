"""
If the scan has many flats, separate the various chunks and analyse then one
by one.

"""
from __future__ import division, print_function

import logging

import pypes.component
import pypesvds.lib.packet

log = logging.getLogger(__name__)


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    http://stackoverflow.com/a/312464
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


class SplitFlatSampleEvery(pypes.component.Component):
    """
    mandatory input packet attributes:
    - None (only receives a trigger but the data is set up on
      initialization)

    optional input packet attributes:
    - None

    parameters:
    - flats_every: every how many files is a flat scan taken?
    - n_flats: n consecutive flats to average
    - files: list with all the files

    output packet attributes:
    - many output ports: each group of files (with one flat) is sent to an
      output.
    - for each output port: (matches the SplitFlatSample interface)
        - sample: list with the files for the sample
        - flat: list with the files for the flats

    """

    # defines the type of component we're creating.
    __metatype__ = 'ADAPTER'

    def __init__(self, flats_every,
                 n_flats, files):
        # initialize parent class
        pypes.component.Component.__init__(self)

        self.set_parameter("flats_every", flats_every)
        self.set_parameter("n_flats", n_flats)
        self.set_parameter("files", files)

        n = len(files) // (flats_every + n_flats)

        # Optionally add/remove component ports
        self.remove_output('out')
        for i in range(n):
            self.add_output('out{0}'.format(i))

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # receives only a trigger
            _ = self.receive('in')
            try:
                files = self.get_parameter("files")
                flats_every = self.get_parameter("flats_every")
                n_flats = self.get_parameter("n_flats")
                n = flats_every + n_flats
                for i, chunk in enumerate(chunks, files, n):
                    sample = chunk[:flats_every]
                    flat = chunks[flats_every:flats_every + n_flats]
                    packet = pypesvds.lib.packet.Packet()
                    packet.set("sample", sample)
                    packet.set("flat", flat)
                    port = "out{0}".format(i)
                    self.send(port, packet)
            except:
                log.error('Component Failed: %s',
                          self.__class__.__name__, exc_info=True)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()


class MergeFlatsEvery(pypes.component.Component):
    """
    mandatory input packet attributes:
    - att1:

    optional input packet attributes:
    - opt:

    parameters:
    - par1: [default: blah]

    output packet attributes:
    - output attribute:

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)

        # Optionally add/remove component ports
        # self.remove_output('out')
        # self.add_input('in2', 'A description of what this port is used for')

        # Setup any user parameters required by this component
        # 2nd arg is the default value, 3rd arg is optional list of choices
        #self.set_parameter('MyParam', 'opt1', ['opt1', 'opt2', 'opt3'])

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # myparam = self.get_parameter('MyParam')

            # for each packet waiting on our input port
            for packet in self.receive_all('in'):
                try:
                    # perform your custom logic here
                    pass
                except:
                    log.error('Component Failed: %s',
                              self.__class__.__name__, exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
