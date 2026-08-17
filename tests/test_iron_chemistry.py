"""Tests for iron speciation, oxidation kinetics and plume transport."""

import math

import pytest

from iron_chemistry import (
    IronState,
    SeawaterConditions,
    fe2_half_life,
    fe2_oxidation_rate_constant,
    fe3_solubility,
    iron_dissolution_rate,
    simulate_iron_plume,
)


# --- Oxidation kinetics ---

def test_rate_constant_increases_with_temperature():
    """Arrhenius behaviour: the 1545/T term dominates."""
    cold = fe2_oxidation_rate_constant(5.0, 35.0, 8.1)
    warm = fe2_oxidation_rate_constant(25.0, 35.0, 8.1)
    assert warm > cold


def test_rate_constant_is_positive_and_finite():
    for T in (0.0, 15.0, 30.0):
        k = fe2_oxidation_rate_constant(T, 35.0, 8.1)
        assert k > 0
        assert math.isfinite(k)


def test_rate_constant_matches_millero_1987_expression():
    """log k = 21.56 - 1545/T - 3.29 sqrt(I) + 1.52 I, per minute."""
    T_K = 288.15
    I = 0.0199 * 35.0
    expected_per_min = 10 ** (21.56 - 1545.0 / T_K - 3.29 * math.sqrt(I) + 1.52 * I)
    assert fe2_oxidation_rate_constant(15.0, 35.0, 8.1) == pytest.approx(
        expected_per_min / 60.0, rel=1e-9)


def test_half_life_falls_fourfold_per_0_3_pH_units():
    """The rate law goes as [OH-]^2, so +0.3 pH is 10^0.6 ~ 4x faster."""
    slow = fe2_half_life(15.0, 35.0, 7.8)
    fast = fe2_half_life(15.0, 35.0, 8.1)
    assert slow / fast == pytest.approx(10 ** 0.6, rel=0.01)


def test_half_life_shortens_with_pH_and_temperature_and_oxygen():
    base = fe2_half_life(15.0, 35.0, 8.1, 250.0)

    assert fe2_half_life(15.0, 35.0, 8.4, 250.0) < base   # more alkaline
    assert fe2_half_life(25.0, 35.0, 8.1, 250.0) < base   # warmer
    assert fe2_half_life(15.0, 35.0, 8.1, 400.0) < base   # more oxygen


def test_half_life_is_inversely_proportional_to_oxygen():
    """Rate is first order in [O2], so doubling O2 halves the half-life."""
    a = fe2_half_life(15.0, 35.0, 8.1, 200.0)
    b = fe2_half_life(15.0, 35.0, 8.1, 400.0)
    assert a / b == pytest.approx(2.0, rel=1e-9)


def test_half_life_at_surface_ocean_conditions_matches_literature():
    """Millero et al. (1987) report minutes, not hours, at pH 8 and 25 degC."""
    minutes = fe2_half_life(25.0, 35.0, 8.0, 250.0) / 60.0
    assert 1.0 < minutes < 15.0


def test_anoxic_water_preserves_fe2_indefinitely():
    assert fe2_half_life(15.0, 35.0, 8.1, 0.0) == float("inf")


# --- Fe(III) solubility ---

def test_fe3_solubility_falls_as_pH_rises():
    """Hydrolysis to Fe(OH)3 is favoured in more alkaline water."""
    assert fe3_solubility(15.0, 35.0, 8.5) < fe3_solubility(15.0, 35.0, 7.5)


def test_fe3_solubility_at_pH8_matches_liu_millero_2002():
    """Liu & Millero (2002): ~0.07-0.6 nM for amorphous Fe(OH)3 at pH 8."""
    assert 0.07 <= fe3_solubility(25.0, 35.0, 8.0) <= 0.6


def test_fe3_solubility_is_clamped_to_physical_bounds():
    assert fe3_solubility(15.0, 35.0, 12.0) == pytest.approx(0.01)
    assert fe3_solubility(15.0, 35.0, 3.0) == pytest.approx(100.0)


def test_fe3_solubility_rises_slightly_with_temperature():
    assert fe3_solubility(30.0, 35.0, 8.0) > fe3_solubility(5.0, 35.0, 8.0)


def test_dissolved_fe3_is_far_below_bioavailable_targets():
    """The 0.1-1.0 ug/L target (1.8-17.9 nM) is unreachable via Fe(III)."""
    assert fe3_solubility(15.0, 35.0, 8.1) < 1.8


# --- Mineral dissolution ---

def test_dissolution_scales_linearly_with_surface_area():
    small = iron_dissolution_rate(100.0, 8.1, 15.0, "magnetite")
    large = iron_dissolution_rate(1000.0, 8.1, 15.0, "magnetite")
    assert large == pytest.approx(10 * small)


def test_zero_surface_area_dissolves_nothing():
    assert iron_dissolution_rate(0.0, 8.1, 15.0, "iron_filings") == 0.0


def test_metallic_iron_dissolves_fastest():
    """Iron filings >> olivine > magnetite."""
    magnetite = iron_dissolution_rate(1000.0, 8.1, 15.0, "magnetite")
    olivine = iron_dissolution_rate(1000.0, 8.1, 15.0, "olivine")
    filings = iron_dissolution_rate(1000.0, 8.1, 15.0, "iron_filings")

    assert magnetite < olivine < filings


def test_unknown_mineral_uses_intermediate_default():
    unknown = iron_dissolution_rate(1000.0, 8.1, 15.0, "unobtainium")
    magnetite = iron_dissolution_rate(1000.0, 8.1, 15.0, "magnetite")
    assert unknown == pytest.approx(10 * magnetite)


def test_dissolution_accelerates_with_temperature():
    """Ea ~50 kJ/mol gives roughly 2-3x per 10 degC."""
    cold = iron_dissolution_rate(1000.0, 8.1, 5.0, "olivine")
    warm = iron_dissolution_rate(1000.0, 8.1, 25.0, "olivine")

    assert warm > cold
    assert 3.0 < warm / cold < 12.0


def test_dissolution_accelerates_in_more_acidic_water():
    assert (iron_dissolution_rate(1000.0, 7.0, 15.0, "olivine")
            > iron_dissolution_rate(1000.0, 8.0, 15.0, "olivine"))


def test_no_pH_acceleration_at_or_above_pH8():
    """The pH factor is pinned to 1.0 for pH >= 8."""
    at_8 = iron_dissolution_rate(1000.0, 8.0, 15.0, "olivine")
    at_8_5 = iron_dissolution_rate(1000.0, 8.5, 15.0, "olivine")
    assert at_8 == pytest.approx(at_8_5)


# --- Plume transport ---

def test_plume_profile_has_expected_shape():
    profile = simulate_iron_plume(500.0, 0.3, max_distance_m=500.0, steps=50)

    assert len(profile) == 51
    assert all(len(row) == 3 for row in profile)
    # First sample is nudged off zero to avoid the 1/sqrt(x) singularity.
    assert profile[0][0] == pytest.approx(0.1)
    assert profile[-1][0] == pytest.approx(500.0)


def test_fe2_decays_monotonically_downstream():
    """Advection dilutes and oxidation destroys -- both fall with distance."""
    profile = simulate_iron_plume(500.0, 0.3, max_distance_m=500.0, steps=50)
    fe2 = [row[1] for row in profile]
    assert fe2 == sorted(fe2, reverse=True)


def test_plume_concentration_scales_with_release_rate():
    weak = simulate_iron_plume(100.0, 0.3, max_distance_m=200.0, steps=20)
    strong = simulate_iron_plume(500.0, 0.3, max_distance_m=200.0, steps=20)

    for (_, weak_fe2, _), (_, strong_fe2, _) in zip(weak, strong):
        assert strong_fe2 == pytest.approx(5 * weak_fe2, rel=1e-9)


def test_no_release_means_no_iron():
    profile = simulate_iron_plume(0.0, 0.3, max_distance_m=200.0, steps=20)
    assert all(fe2 == 0.0 for _, fe2, _ in profile)


def test_faster_current_carries_fe2_further():
    """Less transit time to a given distance means less oxidation en route."""
    slow = simulate_iron_plume(500.0, 0.1, max_distance_m=300.0, steps=30)
    fast = simulate_iron_plume(500.0, 0.5, max_distance_m=300.0, steps=30)

    # Compare the fraction surviving at the far end, not raw concentration
    # (faster flow also dilutes more).
    assert fast[-1][1] / fast[1][1] > slow[-1][1] / slow[1][1]


def test_alkaline_water_shortens_the_plume():
    acidic = SeawaterConditions(pH=7.8)
    alkaline = SeawaterConditions(pH=8.4)

    far_acidic = simulate_iron_plume(500.0, 0.3, acidic, 500.0, 50)[-1][1]
    far_alkaline = simulate_iron_plume(500.0, 0.3, alkaline, 500.0, 50)[-1][1]

    assert far_alkaline < far_acidic


def test_total_dissolved_iron_never_below_fe2():
    profile = simulate_iron_plume(500.0, 0.3, max_distance_m=500.0, steps=50)
    for _, fe2, total in profile:
        assert total >= fe2


def test_plume_uses_default_conditions_when_none_given():
    explicit = simulate_iron_plume(500.0, 0.3, SeawaterConditions(), 200.0, 20)
    implicit = simulate_iron_plume(500.0, 0.3, None, 200.0, 20)
    assert explicit == implicit


# --- IronState bookkeeping ---

def test_iron_state_totals():
    state = IronState(
        fe2_dissolved_nM=1.0,
        fe3_dissolved_nM=0.2,
        fe3_colloidal_nM=0.5,
        fe_particulate_nM=3.0,
        fe_ligand_nM=0.8,
    )

    assert state.total_dissolved_nM == pytest.approx(2.0)
    assert state.total_nM == pytest.approx(5.5)
    assert state.bioavailable_nM == pytest.approx(1.8)


def test_empty_iron_state_is_all_zero():
    state = IronState()
    assert state.total_nM == 0.0
    assert state.total_dissolved_nM == 0.0
    assert state.bioavailable_nM == 0.0


def test_bioavailable_excludes_precipitated_iron():
    """Particulate and colloidal Fe(III) are not accessible to phytoplankton."""
    state = IronState(fe_particulate_nM=100.0, fe3_colloidal_nM=50.0)
    assert state.bioavailable_nM == 0.0
