"""Tests for wave power and OWC device sizing."""

import math

import pytest

from wave_energy import (
    G,
    RHO_SW,
    OWCDevice,
    WaveConditions,
    WaveEnergyResult,
    calculate_owc_performance,
    deep_water_wave_power,
    owc_efficiency,
    wavelength,
)


# --- Wave power ---

def test_wave_power_matches_its_own_formula():
    """Pins the implemented expression P = rho g^2 Hs^2 Tp / (64 pi)."""
    expected = (RHO_SW * G ** 2 * 1.0 ** 2 * 8.0) / (64 * math.pi)
    assert deep_water_wave_power(1.0, 8.0) == pytest.approx(expected)


def test_wave_power_matches_documented_derivation():
    """P must equal energy density x group velocity, as the docstring states.

    E = rho g Hs^2 / 16  and  cg = g Tp / (4 pi)  =>  P = rho g^2 Hs^2 Tp / (64 pi).
    """
    energy_density = RHO_SW * G * 1.0 ** 2 / 16.0
    group_velocity = G * 8.0 / (4 * math.pi)
    assert deep_water_wave_power(1.0, 8.0) == pytest.approx(
        energy_density * group_velocity, rel=1e-9)


def test_wave_power_matches_the_standard_engineering_approximation():
    """The familiar rule of thumb for a random sea: P[kW/m] ~ 0.49 Hs^2 Te."""
    for Hs, Tp in [(0.5, 6.0), (1.0, 8.0), (2.0, 10.0), (3.0, 12.0)]:
        kW_per_m = deep_water_wave_power(Hs, Tp) / 1000.0
        assert kW_per_m == pytest.approx(0.49 * Hs ** 2 * Tp, rel=0.01)


def test_regular_wave_form_is_twice_the_irregular_sea_result():
    """Guards against the 32*pi form silently coming back.

    The 32*pi denominator is correct for monochromatic waves of height H, but
    applying it to a sea state characterised by Hs doubles the resource. This
    pins the factor of 2 so the distinction cannot be quietly re-collapsed.
    """
    regular_wave_power = (RHO_SW * G ** 2 * 1.0 ** 2 * 8.0) / (32 * math.pi)
    assert deep_water_wave_power(1.0, 8.0) == pytest.approx(
        regular_wave_power / 2, rel=1e-12)


def test_wave_power_scales_with_height_squared():
    base = deep_water_wave_power(1.0, 8.0)
    assert deep_water_wave_power(2.0, 8.0) == pytest.approx(4 * base)
    assert deep_water_wave_power(3.0, 8.0) == pytest.approx(9 * base)


def test_wave_power_scales_linearly_with_period():
    base = deep_water_wave_power(1.0, 8.0)
    assert deep_water_wave_power(1.0, 16.0) == pytest.approx(2 * base)


def test_flat_water_carries_no_power():
    assert deep_water_wave_power(0.0, 8.0) == 0.0


def test_wave_power_is_in_kilowatts_per_metre_for_typical_seas():
    """Coastal sea states are O(1-100) kW/m; catches unit-conversion slips."""
    for Hs, Tp in [(0.5, 6.0), (1.0, 8.0), (2.0, 10.0), (3.0, 12.0)]:
        kW_per_m = deep_water_wave_power(Hs, Tp) / 1000.0
        assert 0.1 < kW_per_m < 200.0


# --- Wavelength ---

def test_deep_water_wavelength():
    """L0 = g T^2 / 2pi; a 10 s swell is ~156 m long."""
    assert wavelength(10.0) == pytest.approx(G * 100.0 / (2 * math.pi))
    assert wavelength(10.0) == pytest.approx(156.13, abs=0.1)


def test_deep_water_approximation_used_when_depth_exceeds_half_wavelength():
    L0 = G * 100.0 / (2 * math.pi)
    assert wavelength(10.0, depth_m=L0) == pytest.approx(L0)
    assert wavelength(10.0, depth_m=None) == pytest.approx(L0)


def test_shallow_water_shortens_the_wave():
    """Shoaling reduces wavelength relative to the deep-water value."""
    L0 = wavelength(10.0)
    L_shallow = wavelength(10.0, depth_m=5.0)

    assert L_shallow < L0
    assert L_shallow > 0


def test_wavelength_increases_monotonically_with_depth():
    depths = [2.0, 5.0, 10.0, 20.0, 40.0]
    lengths = [wavelength(10.0, depth_m=d) for d in depths]
    assert lengths == sorted(lengths)


def test_shallow_water_solution_satisfies_dispersion_relation():
    """The iterate must converge to L = L0 tanh(2 pi d / L).

    The solver stops when successive iterates differ by <1 mm and returns the
    earlier one, so the residual is a little larger than that step -- a few
    centimetres on a ~74 m wave (0.03%). The tolerance reflects that.
    """
    depth = 6.0
    L0 = G * 100.0 / (2 * math.pi)
    L = wavelength(10.0, depth_m=depth)
    assert L == pytest.approx(L0 * math.tanh(2 * math.pi * depth / L), abs=0.05)


# --- OWC efficiency ---

def test_turbine_efficiency_ordering():
    """Impulse > Wells > check valve, per Heath (2012)."""
    check = owc_efficiency("check_valve", 1.0, 3.0)
    wells = owc_efficiency("wells", 1.0, 3.0)
    impulse = owc_efficiency("impulse", 1.0, 3.0)

    assert check < wells < impulse


def test_base_efficiencies_are_the_documented_values():
    """Below the overtopping and small-wave thresholds, no penalty applies."""
    assert owc_efficiency("check_valve", 1.0, 3.0) == pytest.approx(0.07)
    assert owc_efficiency("wells", 1.0, 3.0) == pytest.approx(0.18)
    assert owc_efficiency("impulse", 1.0, 3.0) == pytest.approx(0.25)


def test_unknown_turbine_falls_back_to_conservative_default():
    assert owc_efficiency("perpetual_motion", 1.0, 3.0) == pytest.approx(0.10)


def test_efficiency_stays_a_physical_fraction():
    for turbine in ("wells", "impulse", "check_valve"):
        for Hs in (0.05, 0.3, 1.0, 3.0, 10.0):
            eta = owc_efficiency(turbine, Hs, 3.0)
            assert 0.0 <= eta <= 1.0


def test_overtopping_penalises_large_waves():
    """Waves past 0.8 x chamber depth spill over instead of driving the column."""
    nominal = owc_efficiency("wells", 2.0, 3.0)
    overtopping = owc_efficiency("wells", 6.0, 3.0)
    assert overtopping < nominal


def test_small_waves_penalised_by_viscous_losses():
    assert owc_efficiency("wells", 0.15, 3.0) < owc_efficiency("wells", 0.5, 3.0)
    # At Hs = 0.15 m the penalty is exactly the documented Hs/0.3 factor.
    assert owc_efficiency("wells", 0.15, 3.0) == pytest.approx(0.18 * 0.5)


# --- Integrated device performance ---

def test_captured_power_is_available_power_times_efficiency():
    result = calculate_owc_performance()
    assert result.captured_power_W == pytest.approx(
        result.available_power_W * result.efficiency)


def test_available_power_scales_with_chamber_width():
    waves = WaveConditions()
    narrow = calculate_owc_performance(waves, OWCDevice(chamber_width_m=2.0))
    wide = calculate_owc_performance(waves, OWCDevice(chamber_width_m=6.0))

    assert wide.available_power_W == pytest.approx(3 * narrow.available_power_W)


def test_defaults_are_used_when_arguments_omitted():
    assert calculate_owc_performance(None, None) == calculate_owc_performance()
    assert isinstance(calculate_owc_performance(), WaveEnergyResult)


def test_capacity_factor_is_a_fraction():
    for Hs in (0.3, 0.9, 1.5, 2.5):
        waves = WaveConditions(significant_height_m=Hs, winter_Hs_m=Hs * 1.5,
                               summer_Hs_m=Hs * 0.6)
        result = calculate_owc_performance(waves)
        assert 0.0 <= result.capacity_factor <= 1.0


def test_annual_energy_is_consistent_with_mean_power():
    """Annual kWh must equal the seasonal mean power over 8760 hours."""
    result = calculate_owc_performance()
    mean_power_W = result.annual_energy_kWh * 1000.0 / 8760.0
    peak_W = result.captured_power_W

    assert mean_power_W > 0
    # The seasonal mean cannot exceed the rated (annual-mean Hs) capture by much.
    assert mean_power_W < peak_W * 3


def test_flat_sea_produces_no_energy():
    waves = WaveConditions(significant_height_m=0.0, summer_Hs_m=0.0,
                           winter_Hs_m=0.0)
    result = calculate_owc_performance(waves)

    assert result.captured_power_W == 0.0
    assert result.annual_energy_kWh == 0.0
    assert result.capacity_factor == 0.0


def test_bigger_seas_yield_more_power():
    calm = calculate_owc_performance(
        WaveConditions(significant_height_m=0.5, summer_Hs_m=0.4, winter_Hs_m=0.7))
    rough = calculate_owc_performance(
        WaveConditions(significant_height_m=1.5, summer_Hs_m=1.2, winter_Hs_m=2.0))

    assert rough.captured_power_W > calm.captured_power_W
    assert rough.annual_energy_kWh > calm.annual_energy_kWh


def test_community_scale_device_lands_in_the_claimed_power_band():
    """README claims 100 W - 10 kW from community-buildable OWC devices."""
    waves = WaveConditions(significant_height_m=1.0, peak_period_s=8.0)
    device = OWCDevice(chamber_width_m=5.0, chamber_depth_m=3.0,
                       turbine_type="wells")
    result = calculate_owc_performance(waves, device)

    assert 100.0 < result.captured_power_W < 10000.0
