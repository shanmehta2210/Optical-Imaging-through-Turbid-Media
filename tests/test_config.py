"""Config loading and the anisotropy algebra."""

from __future__ import annotations

from pathlib import Path

import pytest

from turbid.io.config import load_config, resolved_g, resolved_mu_s_prime

_EXAMPLE = Path(__file__).resolve().parents[1] / "configs" / "example.yaml"


def test_example_config_resolves_anisotropy() -> None:
    config = load_config(_EXAMPLE)
    assert resolved_g(config["medium"]) == pytest.approx(0.9)
    assert resolved_mu_s_prime(config["medium"]) == pytest.approx(0.05)


def test_mu_s_prime_alone_sets_g() -> None:
    medium = {"mu_a": 0.0, "mu_s": 2.0, "mu_s_prime": 0.2}
    assert resolved_g(medium) == pytest.approx(0.9)
    assert resolved_mu_s_prime(medium) == pytest.approx(0.2)


def test_inconsistent_g_and_mu_s_prime_are_rejected() -> None:
    medium = {"mu_a": 0.0, "mu_s": 0.5, "mu_s_prime": 0.05, "g": 0.5}
    with pytest.raises(ValueError, match="disagrees"):
        resolved_g(medium)


def test_scattering_medium_needs_g_or_mu_s_prime() -> None:
    with pytest.raises(ValueError, match="g or mu_s_prime"):
        resolved_g({"mu_a": 0.0, "mu_s": 0.4})
