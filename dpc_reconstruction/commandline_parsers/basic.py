"""Common to all programs."""
import argparse


class BasicParser(argparse.ArgumentParser):

    """Common to all programs."""

    def __init__(self, *args, **kwargs):
        kwargs['formatter_class'] = argparse.ArgumentDefaultsHelpFormatter
        argparse.ArgumentParser.__init__(self, *args, **kwargs)
        self.add_argument('--overwrite', '-o',
                          action='store_true',
                          help='overwrite hdf5 files if they already exist.')
        self.add_argument('--verbose', '-v',
                          action='store_true',
                          help='print all the debug information.')
        self.add_argument('--jobs', '-j',
                          nargs='?', default=1, type=int,
                          help='''specifies the number of jobs
                          running simultaneously.''')
        self.add_argument('--batch', '-b',
                          action='store_true',
                          help='batch mode (no drawing or user interaction)')
