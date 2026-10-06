"""Radial and lateral profiles from camera frames.

Image arrays are linear camera counts. Profile coordinates are millimetres.
Pixel size is millimetres per pixel. Raw files are only read, never written.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import NDArray


def load_image(path: Path) -> NDArray[np.float64]:
    """Read one frame as a float array in linear counts.

    Parameters
    ----------
    path :
        Image path. TIFF via ``tifffile``, camera raw via ``rawpy``, and
        other still formats via ``imageio``. Apply no gamma and do not
        subtract a dark frame here.

    Returns
    -------
    numpy.ndarray
        Two-dimensional ``float64`` array, shape ``(ny, nx)``, in counts.
    """
    raise NotImplementedError("load_image is not implemented")


def subtract_dark(
    image: NDArray[np.float64],
    dark: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Subtract a dark frame taken at the same exposure.

    Parameters
    ----------
    image :
        Linear counts, shape ``(ny, nx)``.
    dark :
        Dark frame, same shape and exposure, in counts.

    Returns
    -------
    numpy.ndarray
        ``image - dark``, in counts. Negative pixels are left negative so a
        later average is not biased by clipping.
    """
    raise NotImplementedError("subtract_dark is not implemented")


def radial_profile(
    image: NDArray[np.float64],
    origin_x_px: float,
    origin_y_px: float,
    pixel_size_mm: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Azimuthal average of an exit-face image about the beam centre.

    Parameters
    ----------
    image :
        Linear counts, shape ``(ny, nx)``, dark already subtracted.
    origin_x_px, origin_y_px :
        Beam centre in pixel coordinates. ``x`` is the column index.
    pixel_size_mm :
        Millimetres per pixel at the exit face.

    Returns
    -------
    tuple of numpy.ndarray
        ``ρ`` bin centres in millimetres, and the mean counts in each bin.
    """
    raise NotImplementedError("radial_profile is not implemented")


def lateral_profile(
    image: NDArray[np.float64],
    pixel_size_mm: float,
    axis: str = "x",
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Average an image along ``y`` (or ``x``) into a 1D exit profile.

    Parameters
    ----------
    image :
        Linear counts, shape ``(ny, nx)``. The rod stands along ``y``, so
        the default average is over rows.
    pixel_size_mm :
        Millimetres per pixel.
    axis :
        ``"x"`` averages over ``y`` and returns a profile versus ``x``.
        ``"y"`` does the opposite.

    Returns
    -------
    tuple of numpy.ndarray
        Position of each pixel in millimetres, relative to the image centre,
        and the mean counts at that position.
    """
    raise NotImplementedError("lateral_profile is not implemented")


def lateral_profile_from_image(
    image: NDArray[np.float64],
    pixel_size_mm: float,
    dark: NDArray[np.float64] | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Dark-subtract, then return the lateral profile versus ``x``.

    Parameters
    ----------
    image :
        Linear counts, shape ``(ny, nx)``.
    pixel_size_mm :
        Millimetres per pixel.
    dark :
        Optional dark frame in counts. When it is omitted the image is used
        as given.

    Returns
    -------
    tuple of numpy.ndarray
        ``x`` in millimetres and mean counts.
    """
    raise NotImplementedError("lateral_profile_from_image is not implemented")
