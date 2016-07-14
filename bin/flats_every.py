#!/usr/bin/env python
# encoding: utf-8
"""Reconstruct the DPC signals with multiple flats taken every flats_every
files"""

from __future__ import division, print_function

import logging
import logging.config

import click
import tensorflow as tf
import numpy as np

import dpc_reconstruction
import dpc_reconstruction.io.hdf5_reader as hdf5_reader
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    http://stackoverflow.com/a/312464
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--flats_every", default=1, type=int)
@click.option("--n_flats", default=1, type=int)
@click.option("--steps", type=int)
@click.option("--group", default="raw_images")
@click.option("--overwrite", is_flag=True)
@click.option("-v", "--verbose", count=True)
def main(
        files,
        flats_every,
        n_flats,
        steps,
        group,
        overwrite,
        verbose,
        jobs=1
        ):
        n = flats_every + n_flats
        for i, chunk in enumerate(chunks(files, n)):
            sample_files = chunk[:flats_every]
            flat_files = chunk[flats_every:flats_every + n_flats]
            samples = np.stack([hdf5_reader.read_group(sample, group)
                                for sample in sample_files])
            flats = np.stack([hdf5_reader.read_group(sample, group)
                              for sample in flat_files])
            print(samples.shape, flats.shape)
