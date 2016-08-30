import h5py
import click
import numpy as np
import matplotlib.pyplot as plt


@click.command()
@click.argument("oldfile", type=click.Path(exists=True))
@click.argument("newfile", type=click.Path(exists=True))
def main(oldfile, newfile):
    old_dataset = np.squeeze(
        h5py.File(oldfile)["postprocessing/dpc_reconstruction"][...])
    # old_dataset = np.swapaxes(old_dataset, 0, 1)
    new_dataset = np.squeeze(
        h5py.File(newfile)["postprocessing/dpc_reconstruction"][...])
    print(old_dataset.shape)
    print(new_dataset.shape)
    # print(old_dataset)
    # print(new_dataset)
    f, (ax1, ax2) = plt.subplots(1, 2)
    im1 = ax1.imshow(old_dataset[..., 2], interpolation=None, aspect="auto")
    im2 = ax2.imshow(new_dataset[..., 2], interpolation=None, aspect="auto")
    limits = [0, 1]
    im1.set_clim(*limits)
    im2.set_clim(*limits)
    plt.ion()
    plt.show()
    input()
    assert np.allclose(old_dataset, new_dataset)

if __name__ == "__main__":
    main()
