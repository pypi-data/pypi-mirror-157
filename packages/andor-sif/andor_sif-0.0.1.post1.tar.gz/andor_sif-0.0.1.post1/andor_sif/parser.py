import numpy as np
import typing
import sif_reader as sif


def parse(file: str) -> typing.Tuple[np.ndarray, typing.OrderedDict]:
    """
    Parse a .sif file.

    :param file: Path to a `.sif` file.
    :returns tuple[numpy.ndarray, OrderedDict]: Tuple of (data, info) where
        `data` is an (channels x 2) array with the first element of each row
        being the wavelength bin and the second being the counts.
        `info` is an OrderedDict of information about the measurement.
    """
    data, info = sif.np_open(file)
    wavelengths = sif.utils.extract_calibration(info)

    # @todo: `data.flatten()` may not be compatible with
    #   multiple images or 2D images.
    df = np.column_stack((wavelengths, data.flatten()))
    return (df, info)
