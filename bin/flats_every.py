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
import h5py

import dpc_reconstruction
import dpc_reconstruction.io.hdf5 as hdf5
import dpc_reconstruction.phase_stepping as phase_stepping
import dpc_reconstruction.logger_config as logger_config

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
        jobs=1):
    logging.config.dictConfig(
        logger_config.get_dict(verbose)
    )
    n = flats_every + n_flats
    samples = []
    flats = []
    for i, chunk in enumerate(chunks(files, n)):
        sample_files = chunk[:flats_every]
        flat_files = chunk[flats_every:flats_every + n_flats]
        chunk_samples = np.stack(
            [hdf5.read_group(sample, group)
             for sample in sample_files])
        chunk_flats = np.stack(
            [hdf5.read_group(sample, group)
             for sample in flat_files])
        if chunk_flats.shape[0] > 1:
            np.median(chunk_flats, axis=0, overwrite_input=True)
            if chunk_samples.shape[0] > 1:
                chunk_flats = np.tile(
                    chunk_flats, (chunk_samples.shape[0], 1, 1)
                )
        samples.append(chunk_samples)
        flats.append(chunk_flats)
    samples = np.concatenate(samples)
    flats = np.concatenate(flats)
    output_name = hdf5.output_name(files)
    with tf.Session() as sess:
        sample_tensor = tf.placeholder(
            tf.float32, shape=samples.shape)
        flat_tensor = tf.placeholder(
            tf.float32, shape=flats.shape)
        sample_signals = phase_stepping.get_signals(sample_tensor)
        flat_signals = phase_stepping.get_signals(flat_tensor)
        dpc_reconstruction = phase_stepping.compare_sample_to_flat(
            sample_signals,
            flat_signals
        )
        visibility = phase_stepping.visibility(flat_signals)
        dpc_np, flat_np, visibility_np = sess.run(
            [
                dpc_reconstruction,
                flat_signals,
                visibility,
            ],
            feed_dict={
                sample_tensor: samples,
                flat_tensor: flats,
            })
        log.debug("dpc_reconstruction dataset with shape %s", dpc_np.shape)
        log.debug("flat_parameters dataset with shape %s", flat_np.shape)
        log.debug("visibility dataset with shape %s", visibility_np.shape)
        log.debug("flat_phase_stepping_curves dataset with shape %s",
                  flats.shape)
        log.debug("phase_stepping_curves dataset with shape %s", flats.shape)
        log.debug("saving to %s", output_name)
        with h5py.File(output_name, "w-") as output_file:
            group = output_file.create_group("postprocessing")
            group.create_dataset("dpc_reconstruction", data=dpc_np)
            group.create_dataset("visibility", data=visibility_np)
            group.create_dataset("flat_phase_stepping_curves", data=flats)
            group.create_dataset("flat_parameters", data=flat_np)
            group.create_dataset("phase_stepping_curves", data=samples)
            log.info("saved data to %s", output_name)
