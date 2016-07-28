#!/usr/bin/env python
# encoding: utf-8
"""Calculate the visibility."""

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


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--flats_every", default=1, type=int)
@click.option("--steps", type=int)
@click.option("--group", default="raw_images")
@click.option("-v", "--verbose", count=True)
def main(
        files,
        flats_every,
        steps,
        group,
        verbose):
    logging.config.dictConfig(
        logger_config.get_dict(verbose)
    )
    datasets = np.squeeze(np.stack(
        [hdf5.read_group(filename, group)
            for filename in files]
    ))
    datasets = np.swapaxes(datasets, 0, 2)
    log.debug("input datasets with shape %s", datasets.shape)
    output_name = hdf5.output_name(files)
    with tf.Session() as sess:
        tensor = tf.placeholder(
            tf.float32, shape=datasets.shape
        )
        signals = phase_stepping.get_signals(tensor)
        visibility = phase_stepping.visibility(signals)
        visibility_np = sess.run(
            visibility,
            feed_dict={
                tensor: datasets
            })
        log.debug("visibility dataset with shape %s", visibility_np.shape)
        with h5py.File(output_name) as output_file:
            group = output_file.require_group("postprocessing")
            try:
                group.create_dataset("visibility", data=visibility_np)
            except RuntimeError:
                del group["visibility"]
                log.info("overwriting visibility dataset")
                group.create_dataset("visibility", data=visibility_np)
            log.info("saved data to %s", output_name)
