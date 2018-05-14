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
@click.option("--group", default="raw_images")
@click.option("--overwrite", is_flag=True)
@click.option("--crop", type=int, nargs=4)
@click.option("--drop_last", is_flag=True)
@click.option("--phase_steps", type=int, default=0)
@click.option("-v", "--verbose", count=True)
def main(
        files,
        group,
        overwrite,
        crop,
        drop_last,
        phase_steps,
        verbose):
    logging.config.dictConfig(
        logger_config.get_dict(verbose)
    )
    datasets = np.squeeze(np.stack(
        [hdf5.read_group(filename, group, drop_last)[
            crop[0]:crop[1], crop[2]:crop[3], ...]
         for filename in files]
    ))
    if phase_steps:
        log.debug(datasets.shape)
        datasets = np.stack(np.split(
            datasets,
            datasets.shape[-1] // phase_steps,
            axis=-1))
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
                log.info("saved data to %s", output_name)
            except RuntimeError:
                if overwrite:
                    del group["visibility"]
                    log.info("overwriting visibility dataset")
                    group.create_dataset("visibility", data=visibility_np)
                    log.info("data overwritten to %s", output_name)
