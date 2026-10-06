"""Speckle contrast, the ``K²(T)`` fit, and a hydrodynamic radius.

Exposure times are milliseconds. The scattering vector ``q`` is mm^-1.
The diffusion coefficient is mm²/s. The radius returned to the rest of the
project is millimetres. Viscosity stays in pascal-seconds because that is
how the Stokes–Einstein relation is tabulated; the conversion lives in
:func:`hydrodynamic_radius_mm`.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class SpeckleFit:
    """Best-fit coherence factor and decorrelation time.

    Attributes
    ----------
    beta :
        Optical coherence factor, dimensionless.
    tau_c_ms :
        Field decorrelation time in milliseconds.
    beta_uncertainty, tau_c_uncertainty_ms :
        One-standard-deviation uncertainties, same units as the estimates.
    chi2_per_dof :
        ``χ²`` per degree of freedom of the ``K²`` fit, dimensionless.
    """

    def __init__(
        self,
        beta: float,
        tau_c_ms: float,
        beta_uncertainty: float,
        tau_c_uncertainty_ms: float,
        chi2_per_dof: float,
    ) -> None:
        self.beta = beta
        self.tau_c_ms = tau_c_ms
        self.beta_uncertainty = beta_uncertainty
        self.tau_c_uncertainty_ms = tau_c_uncertainty_ms
        self.chi2_per_dof = chi2_per_dof


def speckle_contrast(frames: NDArray[np.float64], window_px: int = 7) -> float:
    """Spatial speckle contrast averaged over windows and frames.

    Parameters
    ----------
    frames :
        Linear camera signal, shape ``(n_frames, ny, nx)``, after dark
        subtraction. Units are camera counts.
    window_px :
        Side length of the square window, in pixels. The plan uses 7.

    Returns
    -------
    float
        ``K = σ_I / ⟨I⟩``, dimensionless, averaged over windows and frames.

    Notes
    -----
    This function does not remove dark noise or shot noise. Subtract those
    from ``σ_I²`` with :func:`correct_speckle_variance` before forming ``K``.
    """
    raise NotImplementedError("speckle_contrast is not implemented")


def correct_speckle_variance(
    variance_counts2: float,
    mean_counts: float,
    dark_variance_counts2: float,
    gain_counts_per_electron: float,
) -> float:
    """Remove dark noise and shot noise from an intensity variance.

    Parameters
    ----------
    variance_counts2 :
        Raw ``σ_I²`` in counts squared.
    mean_counts :
        Mean signal in counts, dark already subtracted.
    dark_variance_counts2 :
        Variance of a dark frame at the same exposure, in counts squared.
    gain_counts_per_electron :
        Camera gain. Shot noise in counts squared is
        ``mean_counts * gain_counts_per_electron`` only when the gain is
        defined that way; document the camera's convention next to the
        implementation and keep the two consistent.

    Returns
    -------
    float
        Corrected ``σ_I²`` in counts squared, clipped at zero so a noise
        estimate cannot drive ``K`` imaginary.
    """
    raise NotImplementedError("correct_speckle_variance is not implemented")


def k_squared(
    exposure_ms: NDArray[np.float64],
    beta: float,
    tau_c_ms: float,
) -> NDArray[np.float64]:
    """Model speckle contrast for an exponentially decaying field correlation.

    Parameters
    ----------
    exposure_ms :
        Camera exposure times in milliseconds, shape ``(n,)``.
    beta :
        Coherence factor, dimensionless.
    tau_c_ms :
        Decorrelation time in milliseconds. Must be positive.

    Returns
    -------
    numpy.ndarray
        ``K²`` at each exposure, dimensionless, shape ``(n,)``.

    Notes
    -----
    With ``x = T / τ_c``,

    .. math::

        K^2(T) = \\beta \\, \\frac{e^{-2x} - 1 + 2x}{2 x^2}.

    The ``x → 0`` limit is ``β``. Use that limit for a zero exposure rather
    than evaluating the quotient.
    """
    raise NotImplementedError("k_squared is not implemented")


def fit_k_squared(
    exposure_ms: NDArray[np.float64],
    k_squared_measured: NDArray[np.float64],
    k_squared_sigma: NDArray[np.float64],
) -> SpeckleFit:
    """Fit ``β`` and ``τ_c`` to a measured ``K²`` versus exposure curve.

    Parameters
    ----------
    exposure_ms :
        Exposures in milliseconds.
    k_squared_measured :
        Measured ``K²``, dimensionless, same length as ``exposure_ms``.
    k_squared_sigma :
        One-standard-deviation uncertainty on each ``K²`` point.

    Returns
    -------
    SpeckleFit
        Estimates, uncertainties, and ``χ²`` per degree of freedom.
        Two parameters are fitted, so the degrees of freedom are
        ``len(exposure_ms) - 2``.
    """
    raise NotImplementedError("fit_k_squared is not implemented")


def scattering_vector_per_mm(
    n_medium: float,
    wavelength_mm: float,
    theta_rad: float,
) -> float:
    """Scattering vector magnitude for a dynamic-light-scattering angle.

    Parameters
    ----------
    n_medium :
        Refractive index of the sample, dimensionless.
    wavelength_mm :
        Vacuum wavelength in millimetres.
    theta_rad :
        Scattering angle in radians. The plan uses a side-wall view near
        ``π/2``, and ``q`` depends on the angle that was actually measured.

    Returns
    -------
    float
        ``q = (4 π n / λ) sin(θ/2)``, in mm^-1.
    """
    raise NotImplementedError("scattering_vector_per_mm is not implemented")


def brownian_diffusion_mm2_per_s(tau_c_ms: float, q_per_mm: float) -> float:
    """Brownian diffusion coefficient in the single-scattering regime.

    Parameters
    ----------
    tau_c_ms :
        Decorrelation time in milliseconds.
    q_per_mm :
        Scattering vector in mm^-1.

    Returns
    -------
    float
        ``D_B`` in mm²/s. With ``τ`` converted to seconds,
        ``D_B = 1 / (q² τ) = 1000 / (q² τ_c_ms)``.
    """
    raise NotImplementedError("brownian_diffusion_mm2_per_s is not implemented")


def hydrodynamic_radius_mm(
    diffusion_mm2_per_s: float,
    temperature_C: float,
    viscosity_Pa_s: float,
) -> float:
    """Stokes–Einstein radius.

    Parameters
    ----------
    diffusion_mm2_per_s :
        ``D_B`` in mm²/s.
    temperature_C :
        Sample temperature in degrees Celsius.
    viscosity_Pa_s :
        Dynamic viscosity of the solvent at ``temperature_C``, in pascal-seconds.
        Water near room temperature is about ``1e-3``. A glycerol mixture
        needs its own viscosity at the working temperature.

    Returns
    -------
    float
        Hydrodynamic radius in millimetres.

    Notes
    -----
    ``r = k_B T / (6 π η D)`` with ``T`` in kelvin and ``D`` in m²/s.
    Convert with ``D[m²/s] = D[mm²/s] × 1e-6`` and ``r[mm] = r[m] × 1e3``:

    ``r_mm = k_B (temperature_C + 273.15) / (6 π η D_mm2_per_s × 1e-6) × 1e3``.
    """
    raise NotImplementedError("hydrodynamic_radius_mm is not implemented")
