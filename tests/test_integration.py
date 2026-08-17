"""End-to-end tests for the integrated site assessment and the CLI.

These check that the three physics modules compose correctly and that the
numbers surfaced in the report are internally consistent with the parts they
came from.
"""

import math
import os
import subprocess
import sys

import pytest

from ocean_restoration_simulation import (
    LA_JOLLA,
    RIVER_MOUTH,
    TROPICAL_REEF,
    IntegratedResult,
    SiteConfig,
    format_assessment,
    run_integrated_assessment,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESETS = [LA_JOLLA, RIVER_MOUTH, TROPICAL_REEF]


# --- Assessment mechanics ---

def test_default_assessment_runs():
    result = run_integrated_assessment()
    assert isinstance(result, IntegratedResult)
    assert result.wave_power_W > 0


def test_assessment_defaults_match_explicit_default_config():
    assert run_integrated_assessment(None) == run_integrated_assessment(SiteConfig())


@pytest.mark.parametrize("config", PRESETS, ids=lambda c: c.name)
def test_preset_sites_produce_finite_results(config):
    """Every numeric field must be a finite real number, not NaN or inf."""
    result = run_integrated_assessment(config)

    for field_name, value in vars(result).items():
        if isinstance(value, float):
            assert math.isfinite(value), f"{field_name} is not finite: {value}"


@pytest.mark.parametrize("config", PRESETS, ids=lambda c: c.name)
def test_preset_sites_report_nonnegative_physical_quantities(config):
    result = run_integrated_assessment(config)

    assert result.wave_power_W >= 0
    assert result.annual_energy_kWh >= 0
    assert result.fe2_half_life_min > 0
    assert result.passive_dissolution_ug_hr >= 0
    assert result.effective_plume_length_m >= 0
    assert result.omega_aragonite_current > 0


# --- Energy budget bookkeeping ---

@pytest.mark.parametrize("config", PRESETS, ids=lambda c: c.name)
def test_total_power_sums_wave_and_salinity_contributions(config):
    result = run_integrated_assessment(config)
    expected = result.wave_power_W + result.salinity_power_mW / 1000.0
    assert result.total_power_W == pytest.approx(expected)


@pytest.mark.parametrize("config", PRESETS, ids=lambda c: c.name)
def test_power_surplus_is_total_minus_demand(config):
    result = run_integrated_assessment(config)
    assert result.power_surplus_W == pytest.approx(
        result.total_power_W - result.alkalinity_power_W)


def test_salinity_gradient_only_contributes_at_a_river_mouth():
    """The estuary preset has a real gradient; open-ocean sites do not."""
    estuary = run_integrated_assessment(RIVER_MOUTH)
    ocean = run_integrated_assessment(LA_JOLLA)

    assert estuary.salinity_power_mW > 0
    assert ocean.salinity_power_mW == 0.0


def test_salinity_gradient_power_stays_negligible():
    """CLAUDE.md is explicit that this yields milliwatts, not watts."""
    estuary = run_integrated_assessment(RIVER_MOUTH)
    assert estuary.salinity_power_mW < 1000.0  # under 1 W
    assert estuary.salinity_power_mW / 1000.0 < 0.01 * estuary.wave_power_W


def test_no_gradient_when_low_salinity_equals_ocean_salinity():
    config = SiteConfig(salinity_psu=35.0, salinity_low_psu=35.0)
    assert run_integrated_assessment(config).salinity_power_mW == 0.0


# --- Carbonate coupling ---

@pytest.mark.parametrize("config", PRESETS, ids=lambda c: c.name)
def test_raising_target_pH_raises_aragonite_saturation(config):
    result = run_integrated_assessment(config)
    if config.target_pH > config.pH:
        assert result.omega_aragonite_restored > result.omega_aragonite_current


def test_warmer_site_has_higher_saturation_state():
    """The tropical reef sits at higher Omega than the temperate site."""
    reef = run_integrated_assessment(TROPICAL_REEF)
    la_jolla = run_integrated_assessment(LA_JOLLA)
    assert reef.omega_aragonite_current > la_jolla.omega_aragonite_current


def test_pH_shift_recorded_when_restoration_is_modelled():
    result = run_integrated_assessment(LA_JOLLA)
    assert result.pH_shift_possible == pytest.approx(
        LA_JOLLA.target_pH - LA_JOLLA.pH)


# --- Iron coupling ---

def test_plume_shrinks_downstream():
    result = run_integrated_assessment(LA_JOLLA)
    assert result.fe2_at_500m_nM <= result.fe2_at_100m_nM


def test_disabling_iron_release_empties_the_plume():
    result = run_integrated_assessment(RIVER_MOUTH)  # iron_release_ug_hr = 0
    assert result.fe2_at_100m_nM == 0.0
    assert result.fe2_at_500m_nM == 0.0
    assert result.effective_plume_length_m == 0.0


def test_larger_release_extends_the_effective_plume():
    small = run_integrated_assessment(SiteConfig(iron_release_ug_hr=100.0))
    large = run_integrated_assessment(SiteConfig(iron_release_ug_hr=100000.0))
    assert large.effective_plume_length_m > small.effective_plume_length_m


# --- Feasibility messaging ---

@pytest.mark.parametrize("config", PRESETS, ids=lambda c: c.name)
def test_warnings_and_recommendations_are_strings(config):
    result = run_integrated_assessment(config)

    assert isinstance(result.warnings, list)
    assert isinstance(result.recommendations, list)
    assert all(isinstance(w, str) and w for w in result.warnings)
    assert all(isinstance(r, str) and r for r in result.recommendations)


def test_warning_lists_are_not_shared_between_results():
    """Guards the dataclass default_factory against mutable-default aliasing."""
    a = run_integrated_assessment(LA_JOLLA)
    b = run_integrated_assessment(TROPICAL_REEF)

    assert a.warnings is not b.warnings
    a.warnings.append("sentinel")
    assert "sentinel" not in b.warnings


def test_underpowered_site_is_warned_about():
    """A tiny device in a flat sea cannot run anything active."""
    config = SiteConfig(
        wave_height_m=0.1, summer_Hs_m=0.05, winter_Hs_m=0.15,
        owc_width_m=0.5, turbine_type="check_valve",
    )
    result = run_integrated_assessment(config)

    assert result.total_power_W < 10
    assert any("low power" in w.lower() for w in result.warnings)


def test_power_deficit_is_warned_about():
    config = SiteConfig(
        wave_height_m=0.2, summer_Hs_m=0.15, winter_Hs_m=0.3,
        owc_width_m=1.0, turbine_type="check_valve",
        pH=8.0, target_pH=8.3,
    )
    result = run_integrated_assessment(config)

    if result.alkalinity_power_W > result.total_power_W:
        assert any("deficit" in w.lower() for w in result.warnings)


def test_site_above_target_pH_gets_iron_focused_recommendation():
    config = SiteConfig(pH=8.25, target_pH=8.15)
    result = run_integrated_assessment(config)
    assert any("already above target" in r for r in result.recommendations)


# --- Report formatting ---

@pytest.mark.parametrize("config", PRESETS, ids=lambda c: c.name)
def test_report_includes_site_name_and_all_sections(config):
    report = format_assessment(run_integrated_assessment(config), config)

    assert config.name in report
    for section in ("SITE CONDITIONS", "ENERGY BUDGET", "pH RESTORATION",
                    "IRON CHEMISTRY"):
        assert section in report


def test_report_lists_every_warning_and_recommendation():
    result = run_integrated_assessment(LA_JOLLA)
    report = format_assessment(result, LA_JOLLA)

    for message in result.warnings + result.recommendations:
        assert message in report


def test_report_omits_empty_sections():
    """A site with no warnings should not print an empty WARNINGS header."""
    result = run_integrated_assessment(LA_JOLLA)
    result.warnings = []
    result.recommendations = []
    report = format_assessment(result, LA_JOLLA)

    assert "WARNINGS" not in report
    assert "RECOMMENDATIONS" not in report


def test_report_uses_defaults_when_config_omitted():
    report = format_assessment(run_integrated_assessment())
    assert isinstance(report, str)
    assert "INTEGRATED OCEAN RESTORATION ASSESSMENT" in report


# --- Executable entry points ---

def _run(*args):
    """Run a repo script in a subprocess and return the completed process.

    The reports contain Greek letters and subscripts, so the child's encoding
    is pinned to UTF-8 rather than inherited from the locale -- otherwise a
    runner with LANG=C fails on the first micro sign.
    """
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8",
        env=env, timeout=120,
    )


@pytest.mark.parametrize("module", [
    "equations/wave_energy.py",
    "equations/iron_chemistry.py",
    "equations/carbonate_system.py",
    "equations/ocean_restoration_simulation.py",
])
def test_module_demo_runs_cleanly(module):
    """Each module's __main__ demonstration must exit 0 and print something."""
    proc = _run(module)

    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip()


@pytest.mark.parametrize("preset", ["la-jolla", "river-mouth", "tropical-reef"])
def test_calculator_presets(preset):
    proc = _run("community-tools/deployment_calculator.py", "--preset", preset)

    assert proc.returncode == 0, proc.stderr
    assert "INTEGRATED OCEAN RESTORATION ASSESSMENT" in proc.stdout


def test_calculator_accepts_custom_parameters():
    proc = _run(
        "community-tools/deployment_calculator.py",
        "--name", "Test Bay", "--wave-height", "1.2", "--wave-period", "10",
        "--pH", "8.0", "--turbine", "impulse", "--owc-width", "4",
    )

    assert proc.returncode == 0, proc.stderr
    assert "Test Bay" in proc.stdout


def test_calculator_no_iron_flag_disables_the_plume():
    proc = _run("community-tools/deployment_calculator.py", "--no-iron")

    assert proc.returncode == 0, proc.stderr
    assert "Target release:     0 μg/hr" in proc.stdout


def test_calculator_rejects_unknown_preset():
    proc = _run("community-tools/deployment_calculator.py", "--preset", "atlantis")
    assert proc.returncode != 0


def test_calculator_help():
    proc = _run("community-tools/deployment_calculator.py", "--help")

    assert proc.returncode == 0
    assert "--wave-height" in proc.stdout
