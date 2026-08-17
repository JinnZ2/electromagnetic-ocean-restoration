"""Tests for the ocean carbonate system model.

The equilibrium constants here are checked against the published values in
the papers the module cites, so a regression in the fitted coefficients
shows up immediately rather than silently shifting every downstream pH and
saturation-state number.
"""

import math

import pytest

from carbonate_system import (
    CarbonateState,
    alkalinity_needed_for_pH_shift,
    aragonite_Ksp,
    calcite_Ksp,
    calcium_concentration,
    carbonate_K1,
    carbonate_K2,
    solve_carbonate_system,
)


# --- Equilibrium constants: known values from the cited literature ---

def test_pK1_matches_lueker_2000():
    """Lueker et al. (2000) give pK1 = 5.8472 at T=25 degC, S=35 (total scale)."""
    pK1 = -math.log10(carbonate_K1(25.0, 35.0))
    assert pK1 == pytest.approx(5.8472, abs=0.001)


def test_pK2_matches_lueker_2000():
    """Lueker et al. (2000) give pK2 = 8.9660 at T=25 degC, S=35 (total scale)."""
    pK2 = -math.log10(carbonate_K2(25.0, 35.0))
    assert pK2 == pytest.approx(8.9660, abs=0.001)


def test_K1_greater_than_K2():
    """The first dissociation is always stronger than the second."""
    for T in (5.0, 15.0, 25.0, 30.0):
        assert carbonate_K1(T, 35.0) > carbonate_K2(T, 35.0)


def test_dissociation_constants_increase_with_temperature():
    """Warmer seawater dissociates carbonic acid more readily."""
    assert carbonate_K1(25.0, 35.0) > carbonate_K1(5.0, 35.0)
    assert carbonate_K2(25.0, 35.0) > carbonate_K2(5.0, 35.0)


def test_aragonite_Ksp_matches_mucci_1983():
    """Mucci (1983): K_sp(aragonite) = 6.48e-7 at T=25 degC, S=35."""
    assert aragonite_Ksp(25.0, 35.0) == pytest.approx(6.48e-7, rel=0.01)


def test_calcite_Ksp_matches_mucci_1983():
    """Mucci (1983): K_sp(calcite) = 4.27e-7 at T=25 degC, S=35."""
    assert calcite_Ksp(25.0, 35.0) == pytest.approx(4.27e-7, rel=0.01)


def test_aragonite_more_soluble_than_calcite():
    """Aragonite is the metastable polymorph, so it dissolves more readily."""
    for T in (5.0, 15.0, 25.0):
        assert aragonite_Ksp(T, 35.0) > calcite_Ksp(T, 35.0)


def test_calcium_concentration_reference_and_scaling():
    """Riley & Tongudai (1967): [Ca2+] = 0.01028 mol/kg at S=35, linear in S."""
    assert calcium_concentration(35.0) == pytest.approx(0.01028, rel=1e-6)
    assert calcium_concentration(17.5) == pytest.approx(0.01028 / 2, rel=1e-6)
    assert calcium_concentration(0.0) == 0.0


# --- Speciation ---

def test_species_sum_to_DIC():
    """Mass balance: CO2 + HCO3- + CO32- must equal total DIC exactly."""
    for pH in (7.6, 8.05, 8.4):
        state = solve_carbonate_system(2050.0, pH, 15.0, 35.0)
        total = state.CO2_umol_kg + state.HCO3_umol_kg + state.CO3_umol_kg
        assert total == pytest.approx(state.DIC_umol_kg, rel=1e-9)


def test_bicarbonate_dominates_at_seawater_pH():
    """At pH ~8, >85% of DIC is bicarbonate."""
    state = solve_carbonate_system(2050.0, 8.05, 15.0, 35.0)
    assert state.HCO3_umol_kg / state.DIC_umol_kg > 0.85


def test_speciation_shifts_with_pH():
    """Raising pH converts CO2 to carbonate; lowering it does the reverse."""
    low = solve_carbonate_system(2050.0, 7.7, 15.0, 35.0)
    high = solve_carbonate_system(2050.0, 8.3, 15.0, 35.0)

    assert high.CO3_umol_kg > low.CO3_umol_kg
    assert high.CO2_umol_kg < low.CO2_umol_kg
    assert high.pCO2_uatm < low.pCO2_uatm


def test_saturation_states_track_carbonate_ion():
    """Omega is linear in [CO32-], so it rises with pH at fixed DIC."""
    low = solve_carbonate_system(2050.0, 7.7, 15.0, 35.0)
    high = solve_carbonate_system(2050.0, 8.3, 15.0, 35.0)

    assert high.omega_aragonite > low.omega_aragonite
    assert high.omega_calcite > low.omega_calcite


def test_calcite_saturation_exceeds_aragonite():
    """Same [CO32-] over a smaller K_sp gives the larger saturation state."""
    state = solve_carbonate_system(2050.0, 8.05, 15.0, 35.0)
    assert state.omega_calcite > state.omega_aragonite


def test_present_day_surface_ocean_is_realistic():
    """Modern surface water: Omega_arag ~2-4, pCO2 within a few hundred uatm."""
    state = solve_carbonate_system(2050.0, 8.05, 15.0, 35.0)

    assert 2.0 < state.omega_aragonite < 4.0
    assert 300.0 < state.pCO2_uatm < 500.0
    assert isinstance(state, CarbonateState)


def test_acidified_future_undersaturates_aragonite_less_than_calcite():
    """RCP 8.5-style conditions push Omega down but keep the polymorph order."""
    state = solve_carbonate_system(2200.0, 7.75, 17.0, 35.0)
    assert state.omega_aragonite < state.omega_calcite
    assert state.omega_aragonite < 2.0


def test_revelle_factor_stays_in_documented_range():
    """The implementation clamps the buffer factor to 8-25."""
    for pH in (7.0, 7.6, 8.05, 8.5, 9.0):
        state = solve_carbonate_system(2050.0, pH, 15.0, 35.0)
        assert 8.0 <= state.buffer_capacity <= 25.0


def test_species_scale_linearly_with_DIC():
    """At fixed pH the speciation fractions are constant."""
    a = solve_carbonate_system(1000.0, 8.05, 15.0, 35.0)
    b = solve_carbonate_system(2000.0, 8.05, 15.0, 35.0)

    assert b.CO2_umol_kg == pytest.approx(2 * a.CO2_umol_kg, rel=1e-9)
    assert b.HCO3_umol_kg == pytest.approx(2 * a.HCO3_umol_kg, rel=1e-9)
    assert b.CO3_umol_kg == pytest.approx(2 * a.CO3_umol_kg, rel=1e-9)


# --- Alkalinity enhancement / energy budget ---

def test_raising_pH_requires_positive_alkalinity():
    result = alkalinity_needed_for_pH_shift(8.05, 8.15, 2050.0, 15.0, 35.0)
    assert result["delta_TA_mol_per_kg"] > 0
    assert result["energy_Wh"] > 0
    assert result["power_W_at_50Lmin"] > 0


def test_lowering_pH_requires_negative_alkalinity():
    result = alkalinity_needed_for_pH_shift(8.15, 8.05, 2050.0, 15.0, 35.0)
    assert result["delta_TA_mol_per_kg"] < 0


def test_no_pH_shift_needs_no_alkalinity():
    result = alkalinity_needed_for_pH_shift(8.05, 8.05, 2050.0, 15.0, 35.0)
    assert result["delta_TA_mol_per_kg"] == pytest.approx(0.0, abs=1e-15)
    assert result["energy_Wh"] == pytest.approx(0.0, abs=1e-9)


def test_alkalinity_demand_grows_with_pH_shift():
    small = alkalinity_needed_for_pH_shift(8.05, 8.10, 2050.0, 15.0, 35.0)
    large = alkalinity_needed_for_pH_shift(8.05, 8.20, 2050.0, 15.0, 35.0)
    assert large["delta_TA_mol_per_kg"] > small["delta_TA_mol_per_kg"]
    assert large["power_W_at_50Lmin"] > small["power_W_at_50Lmin"]


def test_energy_scales_linearly_with_volume():
    """Doubling the treated volume doubles the charge and energy."""
    one = alkalinity_needed_for_pH_shift(8.05, 8.15, 2050.0, 15.0, 35.0, 1.0)
    ten = alkalinity_needed_for_pH_shift(8.05, 8.15, 2050.0, 15.0, 35.0, 10.0)

    assert ten["delta_TA_total_mol"] == pytest.approx(
        10 * one["delta_TA_total_mol"], rel=1e-9)
    assert ten["energy_Wh"] == pytest.approx(10 * one["energy_Wh"], rel=1e-9)


def test_power_is_independent_of_treated_volume():
    """Continuous-flow power depends on flow rate, not on the batch volume."""
    one = alkalinity_needed_for_pH_shift(8.05, 8.15, 2050.0, 15.0, 35.0, 1.0)
    ten = alkalinity_needed_for_pH_shift(8.05, 8.15, 2050.0, 15.0, 35.0, 10.0)
    assert one["power_W_at_50Lmin"] == pytest.approx(ten["power_W_at_50Lmin"])


def test_faradaic_energy_matches_charge_and_voltage():
    """Energy must be exactly Q x V -- guards the unit conversions."""
    result = alkalinity_needed_for_pH_shift(8.05, 8.15, 2050.0, 15.0, 35.0)
    expected_J = result["charge_coulombs"] * result["cell_voltage_V"]

    assert result["energy_joules"] == pytest.approx(expected_J, rel=1e-12)
    assert result["energy_Wh"] == pytest.approx(expected_J / 3600.0, rel=1e-12)


def test_charge_follows_faradays_law():
    """Q = n x F / eta_faradaic for a one-electron-equivalent base."""
    result = alkalinity_needed_for_pH_shift(8.05, 8.15, 2050.0, 15.0, 35.0)
    expected_C = (abs(result["delta_TA_total_mol"]) * 96485.0
                  / result["faradaic_efficiency"])
    assert result["charge_coulombs"] == pytest.approx(expected_C, rel=1e-12)


def test_electrolysis_parameters_are_physically_plausible():
    result = alkalinity_needed_for_pH_shift(8.05, 8.15, 2050.0, 15.0, 35.0)
    assert 1.5 < result["cell_voltage_V"] < 3.0
    assert 0.0 < result["faradaic_efficiency"] <= 1.0


def test_pH_buffering_is_within_community_scale_power():
    """A 0.1-unit shift at 50 L/min must stay in the wave-device range.

    This is the claim the README makes; if a constant drifts and this jumps
    to kilowatts, the project's central feasibility argument has broken.
    """
    result = alkalinity_needed_for_pH_shift(8.05, 8.15, 2050.0, 15.0, 35.0)
    assert 10.0 < result["power_W_at_50Lmin"] < 5000.0
