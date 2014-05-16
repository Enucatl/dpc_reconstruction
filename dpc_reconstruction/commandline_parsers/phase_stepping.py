"""Parser for programs that do phase stepping"""

from dpc_reconstruction.commandline_parsers.basic import BasicParser


class PhaseSteppingParser(BasicParser):

    def __init__(self, *args, **kwargs):
        BasicParser.__init__(self, *args, **kwargs)
        self.add_argument('--steps', '-s',
                          nargs='?', default=1, type=int,
                          help='''number of phase steps''')
