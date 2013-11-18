"""Common to all programs."""
import argparse

commandline_parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

commandline_parser.add_argument('--overwrite', '-o',
        action='store_true',
        help='overwrite hdf5 files if they already exist.')
commandline_parser.add_argument('--verbose', '-v',
        action='store_true',
        help='print all the debug information.')
commandline_parser.add_argument('--jobs', '-j',
        nargs='?', default=1, type=int,
        help='specifies the number of jobs running simultaneously.')
commandline_parser.add_argument('--batch', '-b', 
        action='store_true',
        help='batch mode (no drawing or user interaction)')
