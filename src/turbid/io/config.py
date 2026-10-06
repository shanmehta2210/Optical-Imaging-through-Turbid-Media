"""Load and check YAML simulation configs.

Lengths are millimetres, optical coefficients are mm^-1, and the detector
acceptance angle is radians. ``g`` is dimensionless.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Mapping

import yaml

_REQUIRED_BLOCKS = ("tank", "medium", "source", "rod", "detector", "simulation")


def load_config(path: Path | str) -> dict[str, Any]:
    """Read a YAML config and check its units and required keys.

    Parameters
    ----------
    path :
        Path to a YAML file such as ``configs/example.yaml``.

    Returns
    -------
    dict
        The parsed mapping. It has these blocks:

        ``tank``
            ``length_mm``, ``width_mm``, ``height_mm`` in millimetres;
            ``n_medium``, ``n_outside`` dimensionless.
        ``medium``
            ``mu_a``, ``mu_s`` in mm^-1, and at least one of ``g`` or
            ``mu_s_prime`` (mm^-1). Both may be set when they agree.
        ``source``
            ``type`` is ``pencil`` or ``wide``. ``x_mm`` and ``y_mm`` are
            the launch point or the centre of the wide rectangle.
            A wide source also has ``x_half_width_mm`` and
            ``y_half_height_mm``.
        ``rod``
            ``enabled``, ``radius_mm``, ``x_mm``, ``z_mm``. The cylinder
            is infinite along ``y``.
        ``detector``
            ``acceptance_half_angle_rad`` in radians, lateral binning
            (``lateral_x_min_mm``, ``lateral_x_max_mm``, ``lateral_n_bins``),
            and radial binning (``radial_rho_max_mm``, ``radial_n_bins``).
        ``simulation``
            ``n_photons``, ``n_batches``, ``seed``, ``weight_threshold``,
            ``roulette_survival``.

    Raises
    ------
    ValueError
        A required key is missing, a length or coefficient is out of range,
        or ``g`` disagrees with ``mu_s_prime``.
    """
    path = Path(path)
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"{path} did not contain a mapping")
    validate_config(loaded)
    return loaded


def resolved_g(medium: Mapping[str, Any]) -> float:
    """Return the anisotropy stored in a medium block.

    Parameters
    ----------
    medium :
        The ``medium`` mapping. ``mu_s`` and ``mu_s_prime`` are mm^-1.
        ``g`` is dimensionless.

    Returns
    -------
    float
        ``g`` in ``(-1, 1)``. A block that sets ``mu_s_prime`` and omits
        ``g`` returns ``1 - mu_s_prime / mu_s``. A non-scattering block
        (``mu_s = 0``) with neither value returns ``0``.

    Raises
    ------
    ValueError
        ``g`` is outside ``(-1, 1)``, ``mu_s_prime`` is inconsistent with
        ``g``, or a scattering medium specifies neither.
    """
    mu_s = float(medium["mu_s"])
    if mu_s < 0.0:
        raise ValueError("mu_s must be >= 0 mm^-1")
    g_value = medium.get("g")
    prime_value = medium.get("mu_s_prime")
    has_g = g_value is not None
    has_prime = prime_value is not None
    if has_prime and float(prime_value) < 0.0:
        raise ValueError("mu_s_prime must be >= 0 mm^-1")

    if mu_s == 0.0:
        if has_prime and float(prime_value) != 0.0:
            raise ValueError("mu_s_prime must be 0 when mu_s is 0")
        if has_g:
            g = float(g_value)
            _check_g(g)
            return g
        return 0.0

    g_from_prime: float | None = None
    if has_prime:
        g_from_prime = 1.0 - float(prime_value) / mu_s
        _check_g(g_from_prime)
    if has_g:
        g = float(g_value)
        _check_g(g)
        if g_from_prime is not None and abs(g - g_from_prime) > 1e-5:
            raise ValueError(
                f"g ({g}) disagrees with mu_s_prime, which implies g = {g_from_prime}"
            )
        return g
    if g_from_prime is not None:
        return g_from_prime
    raise ValueError("medium needs g or mu_s_prime when mu_s > 0")


def resolved_mu_s_prime(medium: Mapping[str, Any]) -> float:
    """Return ``μ_s′`` in mm^-1, computing it from ``g`` when it is absent.

    Parameters
    ----------
    medium :
        The ``medium`` mapping.

    Returns
    -------
    float
        ``μ_s′ = μ_s (1 − g)``, in mm^-1. A stored ``mu_s_prime`` is returned
        after :func:`resolved_g` has checked it against ``g``.
    """
    g = resolved_g(medium)
    if medium.get("mu_s_prime") is not None:
        return float(medium["mu_s_prime"])
    return float(medium["mu_s"]) * (1.0 - g)


def validate_config(config: Mapping[str, Any]) -> None:
    """Raise ``ValueError`` when a config is missing keys or has bad units.

    Parameters
    ----------
    config :
        A mapping with the blocks described on :func:`load_config`.
    """
    missing = [name for name in _REQUIRED_BLOCKS if name not in config]
    if missing:
        raise ValueError(f"Config is missing {', '.join(missing)}")

    tank = config["tank"]
    _require(tank, ("length_mm", "width_mm", "height_mm", "n_medium", "n_outside"), "tank")
    for key in ("length_mm", "width_mm", "height_mm"):
        if float(tank[key]) <= 0.0:
            raise ValueError(f"tank.{key} must be positive")
    if float(tank["n_medium"]) <= 0.0 or float(tank["n_outside"]) <= 0.0:
        raise ValueError("refractive indices must be positive")

    medium = config["medium"]
    _require(medium, ("mu_a", "mu_s"), "medium")
    if float(medium["mu_a"]) < 0.0:
        raise ValueError("mu_a must be >= 0 mm^-1")
    resolved_g(medium)

    source = config["source"]
    _require(source, ("type", "x_mm", "y_mm"), "source")
    if source["type"] not in ("pencil", "wide"):
        raise ValueError("source.type must be 'pencil' or 'wide'")
    float(source["x_mm"])
    float(source["y_mm"])
    if source["type"] == "wide":
        _require(source, ("x_half_width_mm", "y_half_height_mm"), "source")
        if float(source["x_half_width_mm"]) <= 0.0 or float(source["y_half_height_mm"]) <= 0.0:
            raise ValueError("wide-beam half-widths must be positive")

    rod = config["rod"]
    _require(rod, ("enabled", "radius_mm", "x_mm", "z_mm"), "rod")
    if float(rod["radius_mm"]) <= 0.0:
        raise ValueError("rod.radius_mm must be positive")
    if not isinstance(rod["enabled"], bool):
        raise ValueError("rod.enabled must be a boolean")

    detector = config["detector"]
    _require(
        detector,
        (
            "acceptance_half_angle_rad",
            "lateral_x_min_mm",
            "lateral_x_max_mm",
            "lateral_n_bins",
            "radial_rho_max_mm",
            "radial_n_bins",
        ),
        "detector",
    )
    half_angle = float(detector["acceptance_half_angle_rad"])
    if not 0.0 < half_angle < math.pi / 2.0:
        raise ValueError("acceptance_half_angle_rad must lie in (0, π/2)")
    if float(detector["lateral_x_min_mm"]) >= float(detector["lateral_x_max_mm"]):
        raise ValueError("lateral x bins need x_min < x_max")
    if int(detector["lateral_n_bins"]) < 1 or int(detector["radial_n_bins"]) < 1:
        raise ValueError("bin counts must be positive")
    if float(detector["radial_rho_max_mm"]) <= 0.0:
        raise ValueError("radial_rho_max_mm must be positive")

    simulation = config["simulation"]
    _require(
        simulation,
        ("n_photons", "n_batches", "seed", "weight_threshold", "roulette_survival"),
        "simulation",
    )
    n_photons = int(simulation["n_photons"])
    n_batches = int(simulation["n_batches"])
    if n_photons < 1 or n_batches < 1:
        raise ValueError("n_photons and n_batches must be positive")
    if n_photons % n_batches != 0:
        raise ValueError("n_photons must be divisible by n_batches")
    if float(simulation["weight_threshold"]) <= 0.0:
        raise ValueError("weight_threshold must be positive")
    survival = float(simulation["roulette_survival"])
    if not 0.0 < survival <= 1.0:
        raise ValueError("roulette_survival must lie in (0, 1]")


def _check_g(g: float) -> None:
    if not -1.0 < g < 1.0:
        raise ValueError(f"g must lie in (-1, 1); got {g}")


def _require(block: Mapping[str, Any], keys: tuple[str, ...], block_name: str) -> None:
    missing = [key for key in keys if key not in block]
    if missing:
        raise ValueError(f"{block_name} is missing {', '.join(missing)}")
