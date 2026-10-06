"""Mie anisotropy ``g`` as a function of particle radius.

Radius and wavelength are millimetres (632.8 nm is ``6.328e-4`` mm).
``g`` is dimensionless. Wrap ``miepython``; do not reimplement the Mie series.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def anisotropy_vs_radius(
    radius_mm: NDArray[np.float64],
    wavelength_mm: float,
    n_particle: complex,
    n_medium: float,
) -> NDArray[np.float64]:
    """Compute the Mie asymmetry parameter on a radius grid.

    Parameters
    ----------
    radius_mm :
        Sphere radii in millimetres, shape ``(n,)``.
    wavelength_mm :
        Vacuum wavelength in millimetres.
    n_particle :
        Particle refractive index relative to vacuum. A complex value is the
        absorbing case. Dimensionless.
    n_medium :
        Real refractive index of the surrounding water. Dimensionless.

    Returns
    -------
    numpy.ndarray
        ``g(r)``, dimensionless, shape ``(n,)``. The size parameter is
        ``x = 2 π n_medium radius_mm / wavelength_mm``.

    Notes
    -----
    This ``g`` is the intensity-weighted mean cosine from the Mie amplitudes,
    not a Henyey–Greenstein input. The Monte Carlo consumes it only after
    Part A has measured ``g``.
    """
    raise NotImplementedError("anisotropy_vs_radius is not implemented")


def effective_radius_mm(
    g_measured: float,
    g_uncertainty: float,
    radius_grid_mm: NDArray[np.float64],
    wavelength_mm: float,
    n_particle: complex,
    n_particle_uncertainty: float,
    n_medium: float,
) -> tuple[float, float, float]:
    """Invert a measured anisotropy for an effective sphere radius.

    Parameters
    ----------
    g_measured :
        Anisotropy from Part A, dimensionless.
    g_uncertainty :
        One-standard-deviation uncertainty on ``g_measured``.
    radius_grid_mm :
        Radii at which to evaluate ``g(r)``, in millimetres. The grid has
        to cover the expected casein and fat sizes.
    wavelength_mm :
        Vacuum wavelength in millimetres.
    n_particle :
        Particle refractive index, dimensionless.
    n_particle_uncertainty :
        Uncertainty on the real part of ``n_particle``, dimensionless.
    n_medium :
        Real refractive index of water, dimensionless.

    Returns
    -------
    tuple of float
        ``(radius_mm, low_mm, high_mm)``. The band is the range of radii
        whose Mie ``g`` stays inside the measured ``g`` band after the
        refractive index is shifted by ``± n_particle_uncertainty``. Milk
        is polydisperse, so the radius is an effective one, weighted toward
        the sizes that scatter most.
    """
    raise NotImplementedError("effective_radius_mm is not implemented")
