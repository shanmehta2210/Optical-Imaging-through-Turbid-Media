"""Henyey–Greenstein sampling and direction updates.

Angles that these functions return are in radians. Cosines are dimensionless.
The scattering parameters do not carry a length unit.
"""

from __future__ import annotations

import numpy as np

def henyey_greenstein_cos_theta(g: float, xi: float) -> float:
    """Sample ``cos θ`` from the Henyey–Greenstein phase function.

    Parameters
    ----------
    g :
        Anisotropy, dimensionless, with ``-1 < g < 1``. ``g = 0`` is
        isotropic and must be handled on its own: the general formula
        divides by ``g``.
    xi :
        Uniform random number on (0, 1).

    Returns
    -------
    float
        Cosine of the polar scattering angle, dimensionless, in [-1, 1].

    Notes
    -----
    For ``g ≠ 0`` and ``ξ`` uniform on (0, 1),

    .. math::

        \\cos\\theta = \\frac{1}{2g}\\left[
        1 + g^2 - \\left(\\frac{1 - g^2}{1 - g + 2 g \\xi}\\right)^2
        \\right].

    For ``g = 0``, use ``cos θ = 2ξ − 1``. The sample mean of ``cos θ``
    must equal ``g``.
    """
    raise NotImplementedError("henyey_greenstein_cos_theta is not implemented")


def sample_azimuth(xi: float) -> float:
    """Sample an azimuthal scattering angle.

    Parameters
    ----------
    xi :
        Uniform random number on [0, 1).

    Returns
    -------
    float
        ``φ`` in radians, uniform on ``[0, 2π)``.
    """
    raise NotImplementedError("sample_azimuth is not implemented")


def scatter_direction(
    direction: np.ndarray,
    cos_theta: float,
    phi_rad: float,
) -> np.ndarray:
    """Rotate a unit direction by a polar deflection and an azimuth.

    Parameters
    ----------
    direction :
        Incoming unit vector, shape (3,), dimensionless direction cosines
        ``(ux, uy, uz)``.
    cos_theta :
        Cosine of the polar scattering angle, dimensionless.
    phi_rad :
        Azimuthal angle in radians.

    Returns
    -------
    numpy.ndarray
        Outgoing unit vector, shape (3,). The sample mean of the ``z``
        component, for a beam that starts along ``+z``, equals ``g`` after
        one scattering.

    Notes
    -----
    Use the same rotation as the ``Spin`` routine in MCML (Wang, Jacques,
    and Zheng, 1995), including the separate branch for a direction that
    is already parallel to ``z``.
    """
    raise NotImplementedError("scatter_direction is not implemented")
