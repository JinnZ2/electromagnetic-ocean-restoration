"""
Ocean Restoration Simulation — Integrated Site Assessment

Combines wave energy capture, iron chemistry, and carbonate system models
to assess a complete ocean restoration deployment.

This is the main entry point for running integrated simulations. It imports
from the individual physics modules:
  - wave_energy.py: Wave power and OWC device sizing
  - iron_chemistry.py: Fe²⁺/Fe³⁺ kinetics and plume modeling
  - carbonate_system.py: pH buffering and alkalinity enhancement

Usage:
    python equations/ocean_restoration_simulation.py

WARNING: This is a planning tool. Real deployments require site-specific
oceanographic data, environmental impact assessment, and regulatory approval.
"""

import math
import sys
import os
from dataclasses import dataclass, field
from typing import Optional

# Add parent directory to path for imports when run directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wave_energy import (
    WaveConditions, OWCDevice, deep_water_wave_power,
    owc_efficiency, calculate_owc_performance,
)
from iron_chemistry import (
    SeawaterConditions, fe2_half_life, fe3_solubility,
    iron_dissolution_rate, simulate_iron_plume,
)
from carbonate_system import (
    solve_carbonate_system, alkalinity_needed_for_pH_shift,
)

# Physical constants
R = 8.314          # Gas constant (J/mol·K)
F_CONST = 96485.0  # Faraday constant (C/mol)
RHO_SW = 1025.0    # Seawater density (kg/m³)


@dataclass
class SiteConfig:
    """Complete site configuration for integrated simulation."""
    # Location
    name: str = "Generic Coastal Site"

    # Wave conditions
    wave_height_m: float = 1.0
    wave_period_s: float = 8.0
    summer_Hs_m: float = 0.6
    winter_Hs_m: float = 1.5

    # Seawater
    temperature_C: float = 15.0
    salinity_psu: float = 35.0
    pH: float = 8.05
    DIC_umol_kg: float = 2050.0
    dissolved_O2_umol_kg: float = 250.0

    # Salinity gradient (only meaningful at river mouths)
    salinity_low_psu: float = 35.0   # same as ocean = no gradient

    # Device
    owc_width_m: float = 5.0
    owc_depth_m: float = 3.0
    turbine_type: str = "wells"

    # Iron release
    iron_release_ug_hr: float = 500.0  # μg/hr as dissolved Fe
    iron_mineral: str = "iron_filings"
    iron_surface_area_cm2: float = 5000.0  # for passive dissolution

    # Current
    current_speed_m_s: float = 0.3

    # pH restoration target
    target_pH: float = 8.15
    flow_rate_L_min: float = 50.0


@dataclass
class IntegratedResult:
    """Complete assessment results."""
    # Energy
    wave_power_W: float = 0.0
    salinity_power_mW: float = 0.0
    total_power_W: float = 0.0
    annual_energy_kWh: float = 0.0

    # pH restoration
    alkalinity_power_W: float = 0.0
    pH_shift_possible: float = 0.0
    power_surplus_W: float = 0.0

    # Iron
    fe2_half_life_min: float = 0.0
    passive_dissolution_ug_hr: float = 0.0
    fe2_at_100m_nM: float = 0.0
    fe2_at_500m_nM: float = 0.0
    effective_plume_length_m: float = 0.0

    # Carbonate system
    omega_aragonite_current: float = 0.0
    omega_aragonite_restored: float = 0.0
    pCO2_current_uatm: float = 0.0

    # Feasibility
    warnings: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)


def run_integrated_assessment(config: Optional[SiteConfig] = None
                                ) -> IntegratedResult:
    """Run complete integrated site assessment.

    Chains together wave energy, iron chemistry, and carbonate system
    models to evaluate a restoration deployment.

    Args:
        config: Site configuration. Uses defaults if None.

    Returns:
        IntegratedResult with complete assessment.
    """
    if config is None:
        config = SiteConfig()

    result = IntegratedResult()

    # --- 1. WAVE ENERGY ---
    waves = WaveConditions(
        significant_height_m=config.wave_height_m,
        peak_period_s=config.wave_period_s,
        summer_Hs_m=config.summer_Hs_m,
        winter_Hs_m=config.winter_Hs_m,
    )
    device = OWCDevice(
        chamber_width_m=config.owc_width_m,
        chamber_depth_m=config.owc_depth_m,
        turbine_type=config.turbine_type,
    )
    wave_result = calculate_owc_performance(waves, device)
    result.wave_power_W = wave_result.captured_power_W
    result.annual_energy_kWh = wave_result.annual_energy_kWh

    # --- 2. SALINITY GRADIENT (usually negligible) ---
    if config.salinity_low_psu < config.salinity_psu - 1.0:
        T_K = config.temperature_C + 273.15
        delta_V = (R * T_K / F_CONST) * math.log(config.salinity_psu / config.salinity_low_psu)
        # Small RED cell: ~5 mA, 30% efficiency
        result.salinity_power_mW = delta_V * 0.005 * 0.30 * 1000
    else:
        result.salinity_power_mW = 0.0

    result.total_power_W = result.wave_power_W + result.salinity_power_mW / 1000

    # --- 3. IRON CHEMISTRY ---
    sw_conditions = SeawaterConditions(
        temperature_C=config.temperature_C,
        salinity_psu=config.salinity_psu,
        pH=config.pH,
        dissolved_O2_umol_kg=config.dissolved_O2_umol_kg,
    )

    result.fe2_half_life_min = fe2_half_life(
        config.temperature_C, config.salinity_psu,
        config.pH, config.dissolved_O2_umol_kg
    ) / 60.0

    result.passive_dissolution_ug_hr = iron_dissolution_rate(
        config.iron_surface_area_cm2, config.pH,
        config.temperature_C, config.iron_mineral
    )

    # Iron plume
    plume = simulate_iron_plume(
        config.iron_release_ug_hr, config.current_speed_m_s,
        sw_conditions, max_distance_m=1000.0, steps=100
    )

    # Extract key plume values
    for dist, fe2, total in plume:
        if abs(dist - 100) < 15:
            result.fe2_at_100m_nM = fe2
        if abs(dist - 500) < 15:
            result.fe2_at_500m_nM = fe2

    # Effective plume length (where Fe²⁺ > 1.8 nM = 0.1 μg/L)
    threshold_nM = 1.8  # 0.1 μg/L
    result.effective_plume_length_m = 0.0
    for dist, fe2, total in plume:
        if fe2 >= threshold_nM:
            result.effective_plume_length_m = dist

    # --- 4. CARBONATE SYSTEM ---
    current_state = solve_carbonate_system(
        config.DIC_umol_kg, config.pH,
        config.temperature_C, config.salinity_psu
    )
    result.omega_aragonite_current = current_state.omega_aragonite
    result.pCO2_current_uatm = current_state.pCO2_uatm

    restored_state = solve_carbonate_system(
        config.DIC_umol_kg, config.target_pH,
        config.temperature_C, config.salinity_psu
    )
    result.omega_aragonite_restored = restored_state.omega_aragonite

    # --- 5. pH RESTORATION ENERGY BUDGET ---
    alk_result = alkalinity_needed_for_pH_shift(
        config.pH, config.target_pH,
        config.DIC_umol_kg, config.temperature_C,
        config.salinity_psu, volume_m3=1.0
    )
    result.alkalinity_power_W = alk_result["power_W_at_50Lmin"]
    if result.alkalinity_power_W > 0:
        result.pH_shift_possible = config.target_pH - config.pH
    result.power_surplus_W = result.total_power_W - result.alkalinity_power_W

    # --- 6. FEASIBILITY ASSESSMENT ---
    if result.total_power_W < 10:
        result.warnings.append(
            f"Very low power ({result.total_power_W:.1f} W). "
            "Only passive monitoring is feasible."
        )

    if result.alkalinity_power_W > result.total_power_W:
        deficit = result.alkalinity_power_W - result.total_power_W
        result.warnings.append(
            f"pH restoration requires {result.alkalinity_power_W:.0f} W but only "
            f"{result.total_power_W:.0f} W available (deficit: {deficit:.0f} W). "
            "Reduce flow rate or increase device size."
        )

    if result.fe2_half_life_min < 5:
        result.warnings.append(
            f"Fe²⁺ half-life is {result.fe2_half_life_min:.1f} min — iron oxidizes "
            "very fast. Use slow continuous release, not batch dosing."
        )

    if result.effective_plume_length_m < 50:
        result.warnings.append(
            f"Effective iron plume only {result.effective_plume_length_m:.0f} m long. "
            "Consider chelated iron or multiple release points."
        )

    if config.pH > 8.15:
        result.recommendations.append(
            "Site pH is already above target. Focus on iron delivery, "
            "not pH buffering."
        )

    if result.power_surplus_W > 100:
        result.recommendations.append(
            f"Power surplus of {result.power_surplus_W:.0f} W available for "
            "sensors, data logging, and telemetry."
        )

    if result.passive_dissolution_ug_hr < config.iron_release_ug_hr * 0.1:
        result.recommendations.append(
            f"Passive dissolution ({result.passive_dissolution_ug_hr:.1f} μg/hr) is much "
            f"less than target release ({config.iron_release_ug_hr:.0f} μg/hr). "
            "Use electrolytic dissolution powered by wave energy."
        )

    return result


def format_assessment(result: IntegratedResult,
                       config: Optional[SiteConfig] = None) -> str:
    """Format integrated assessment as readable report."""
    if config is None:
        config = SiteConfig()

    lines = [
        "=" * 70,
        f"  INTEGRATED OCEAN RESTORATION ASSESSMENT: {config.name}",
        "=" * 70,
        "",
        "  SITE CONDITIONS",
        "  " + "-" * 66,
        f"    Waves:    Hs={config.wave_height_m:.1f} m, Tp={config.wave_period_s:.0f} s "
        f"(seasonal: {config.summer_Hs_m:.1f}–{config.winter_Hs_m:.1f} m)",
        f"    Water:    T={config.temperature_C:.1f}°C, S={config.salinity_psu:.1f} psu, "
        f"pH={config.pH:.2f}",
        f"    Current:  {config.current_speed_m_s:.1f} m/s",
        f"    DIC:      {config.DIC_umol_kg:.0f} μmol/kg",
        "",
        "  ENERGY BUDGET",
        "  " + "-" * 66,
        f"    Wave energy ({config.owc_width_m:.0f}m {config.turbine_type} OWC):  "
        f"{result.wave_power_W:.0f} W",
    ]

    if result.salinity_power_mW > 0.01:
        lines.append(
            f"    Salinity gradient:  {result.salinity_power_mW:.3f} mW  (negligible)")

    lines.extend([
        f"    Total available:    {result.total_power_W:.0f} W",
        f"    Annual energy:      {result.annual_energy_kWh:.0f} kWh/year",
        "",
        "  pH RESTORATION",
        "  " + "-" * 66,
        f"    Current:  pH={config.pH:.2f}, Ω_arag={result.omega_aragonite_current:.2f}, "
        f"pCO₂={result.pCO2_current_uatm:.0f} μatm",
        f"    Target:   pH={config.target_pH:.2f}, Ω_arag={result.omega_aragonite_restored:.2f}",
        f"    Power needed ({config.flow_rate_L_min:.0f} L/min):  "
        f"{result.alkalinity_power_W:.0f} W",
        f"    Power surplus:      {result.power_surplus_W:.0f} W",
        "",
        "  IRON CHEMISTRY",
        "  " + "-" * 66,
        f"    Fe²⁺ half-life:    {result.fe2_half_life_min:.1f} min",
        f"    Passive dissolution: {result.passive_dissolution_ug_hr:.1f} μg/hr "
        f"({config.iron_mineral}, {config.iron_surface_area_cm2:.0f} cm²)",
        f"    Target release:     {config.iron_release_ug_hr:.0f} μg/hr",
        f"    Fe²⁺ at 100m:      {result.fe2_at_100m_nM:.1f} nM "
        f"({result.fe2_at_100m_nM * 0.055845:.3f} μg/L)",
        f"    Fe²⁺ at 500m:      {result.fe2_at_500m_nM:.1f} nM "
        f"({result.fe2_at_500m_nM * 0.055845:.3f} μg/L)",
        f"    Effective plume:    {result.effective_plume_length_m:.0f} m "
        "(Fe²⁺ > 0.1 μg/L)",
        "",
    ])

    if result.warnings:
        lines.append("  WARNINGS")
        lines.append("  " + "-" * 66)
        for w in result.warnings:
            lines.append(f"    ⚠ {w}")
        lines.append("")

    if result.recommendations:
        lines.append("  RECOMMENDATIONS")
        lines.append("  " + "-" * 66)
        for r in result.recommendations:
            lines.append(f"    → {r}")
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


# --- Predefined site configurations ---

LA_JOLLA = SiteConfig(
    name="La Jolla Marine Sanctuary",
    wave_height_m=0.9,
    wave_period_s=10.0,
    summer_Hs_m=0.6,
    winter_Hs_m=1.3,
    temperature_C=17.0,
    salinity_psu=33.5,
    pH=8.05,
    DIC_umol_kg=2020.0,
    current_speed_m_s=0.25,
    owc_width_m=5.0,
    turbine_type="wells",
    iron_release_ug_hr=300.0,
    target_pH=8.15,
)

RIVER_MOUTH = SiteConfig(
    name="River Mouth (Generic Estuary)",
    wave_height_m=0.7,
    wave_period_s=7.0,
    summer_Hs_m=0.4,
    winter_Hs_m=1.0,
    temperature_C=14.0,
    salinity_psu=30.0,
    salinity_low_psu=5.0,
    pH=7.95,
    DIC_umol_kg=2100.0,
    current_speed_m_s=0.5,
    owc_width_m=3.0,
    turbine_type="check_valve",
    iron_release_ug_hr=0.0,  # No iron at river mouths (excess already)
    target_pH=8.10,
)

TROPICAL_REEF = SiteConfig(
    name="Tropical Coral Reef",
    wave_height_m=0.6,
    wave_period_s=6.0,
    summer_Hs_m=0.5,
    winter_Hs_m=0.8,
    temperature_C=27.0,
    salinity_psu=35.0,
    pH=8.02,
    DIC_umol_kg=1950.0,
    current_speed_m_s=0.15,
    owc_width_m=3.0,
    turbine_type="check_valve",
    iron_release_ug_hr=100.0,
    target_pH=8.15,
)


if __name__ == "__main__":
    sites = [LA_JOLLA, RIVER_MOUTH, TROPICAL_REEF]

    for site_config in sites:
        result = run_integrated_assessment(site_config)
        print(format_assessment(result, site_config))
        print()
