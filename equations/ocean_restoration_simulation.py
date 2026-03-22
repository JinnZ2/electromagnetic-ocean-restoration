"""
Ocean Electromagnetic Restoration Simulation

Models three physically validated energy harvesting mechanisms for coastal
electromagnetic restoration systems, with realistic parameter ranges.

Energy sources modeled:
  1. Salinity gradient (reverse electrodialysis) — Nernst equation
  2. Ocean current electromagnetic induction — Faraday's law
  3. Wave energy — linear wave theory

Iron dispersal is modeled as a simple advection-diffusion process.

WARNING: This is a simplified planning tool. Real deployments require
site-specific oceanographic data and environmental impact assessment.
Do NOT deploy iron into marine environments without regulatory approval.
"""

import math
from dataclasses import dataclass, field
from typing import Optional

# Physical constants
R = 8.314          # Gas constant (J/mol·K)
F = 96485.0        # Faraday constant (C/mol)
RHO_SW = 1025.0    # Seawater density (kg/m³)
G = 9.81           # Gravitational acceleration (m/s²)
MU_0 = 4e-7 * math.pi  # Vacuum permeability (H/m)


@dataclass
class SiteConditions:
    """Oceanographic conditions at a deployment site."""
    # Salinity gradient
    salinity_high: float = 35.0    # psu (ocean side)
    salinity_low: float = 5.0     # psu (river mouth)
    temperature_K: float = 288.0  # Water temperature (K), ~15°C

    # Ocean current
    current_velocity: float = 0.5  # m/s
    magnetic_field: float = 50e-6  # Earth's field strength (T), typical mid-latitude
    electrode_separation: float = 1.0  # m
    current_field_angle_deg: float = 90.0  # Angle between current and B field

    # Wave conditions
    wave_height: float = 1.0      # Significant wave height (m)
    wave_period: float = 8.0      # Wave period (s)
    wave_crest_length: float = 10.0  # Capture width (m)

    # Iron dispersal
    iron_release_rate_kg_per_hr: float = 0.001  # kg/hr of iron filings
    diffusion_coefficient: float = 1e-9  # m²/s (molecular diffusion of Fe in seawater)
    current_speed_for_advection: float = 0.3  # m/s

    # System efficiencies
    salinity_efficiency: float = 0.30   # Typical RED membrane efficiency
    induction_efficiency: float = 0.10  # Small-scale electromagnetic harvesting
    wave_efficiency: float = 0.15       # Small-scale wave energy capture
    piezo_d33: float = 500e-12          # Piezoelectric coefficient (C/N), PZT ceramic
    piezo_force: float = 100.0          # Wave force on element (N)


@dataclass
class SimulationResult:
    """Results from a single simulation timestep or steady-state calculation."""
    # Power from each source (watts)
    salinity_power_W: float = 0.0
    induction_power_W: float = 0.0
    wave_power_W: float = 0.0
    total_power_W: float = 0.0

    # Voltages
    salinity_voltage_V: float = 0.0
    induction_voltage_V: float = 0.0
    piezo_voltage_V: float = 0.0

    # Iron dispersal
    iron_concentration_at_1km_ug_L: float = 0.0
    iron_plume_radius_m: float = 0.0

    # Feasibility flags
    warnings: list = field(default_factory=list)


def salinity_gradient_voltage(c_high: float, c_low: float, temp_K: float,
                               ion_charge: int = 1) -> float:
    """Nernst equation for salinity gradient potential.

    ΔV = (RT / nF) × ln(C₁ / C₂)

    Args:
        c_high: Higher salinity concentration (psu or proportional)
        c_low: Lower salinity concentration (psu or proportional)
        temp_K: Temperature in Kelvin
        ion_charge: Ion charge number (1 for Na⁺/Cl⁻)

    Returns:
        Voltage in volts (open-circuit, single ion pair)
    """
    if c_low <= 0 or c_high <= 0:
        return 0.0
    return (R * temp_K) / (ion_charge * F) * math.log(c_high / c_low)


def ocean_current_induction_voltage(B: float, v: float, L: float,
                                      theta_deg: float) -> float:
    """Faraday's law: EMF from conductive seawater moving through magnetic field.

    V = B × v × L × sin(θ)

    Args:
        B: Magnetic field strength (Tesla)
        v: Current velocity (m/s)
        L: Electrode separation (m)
        theta_deg: Angle between current direction and field (degrees)

    Returns:
        Induced voltage in volts
    """
    theta_rad = math.radians(theta_deg)
    return B * v * L * math.sin(theta_rad)


def wave_power_per_meter(wave_height: float, wave_period: float) -> float:
    """Deep-water wave power per meter of wave crest.

    P = (ρ × g² × H² × T) / (32π)  [W/m]

    This is the standard linear wave theory result for power transport.

    Args:
        wave_height: Significant wave height (m)
        wave_period: Wave period (s)

    Returns:
        Power in watts per meter of wave crest
    """
    return (RHO_SW * G**2 * wave_height**2 * wave_period) / (32 * math.pi)


def iron_concentration_downstream(release_rate_kg_s: float,
                                   current_speed: float,
                                   diffusion_coeff: float,
                                   distance_m: float) -> float:
    """Steady-state iron concentration downstream using simplified advection-diffusion.

    Models a continuous point source in a uniform current. Returns centerline
    concentration at a given distance downstream.

    C(x) = Q / (2π × D × x / v)  [simplified 2D steady-state]

    Converted to μg/L for comparison with ecological targets (0.1-1.0 μg/L).

    Args:
        release_rate_kg_s: Iron release rate (kg/s)
        current_speed: Advection velocity (m/s)
        diffusion_coeff: Turbulent + molecular diffusion coefficient (m²/s)
        distance_m: Distance downstream (m)

    Returns:
        Concentration in μg/L (micrograms per liter)
    """
    if distance_m <= 0 or current_speed <= 0:
        return 0.0

    # Use turbulent diffusion which dominates in ocean (~0.01-1 m²/s)
    D_turb = max(diffusion_coeff, 0.01)  # Minimum turbulent diffusion

    # 2D Gaussian plume centerline concentration (kg/m³)
    sigma = math.sqrt(2 * D_turb * distance_m / current_speed)
    if sigma <= 0:
        return 0.0
    conc_kg_m3 = release_rate_kg_s / (current_speed * math.pi * sigma**2)

    # Convert kg/m³ → μg/L (1 kg/m³ = 1e9 μg/L)
    return conc_kg_m3 * 1e9


def run_simulation(site: Optional[SiteConditions] = None) -> SimulationResult:
    """Run steady-state energy and iron dispersal simulation for a site.

    Args:
        site: Site conditions. Uses defaults (moderate coastal site) if None.

    Returns:
        SimulationResult with power estimates, voltages, and iron dispersal.
    """
    if site is None:
        site = SiteConditions()

    result = SimulationResult()

    # --- Energy Source 1: Salinity Gradient ---
    result.salinity_voltage_V = salinity_gradient_voltage(
        site.salinity_high, site.salinity_low, site.temperature_K
    )
    # Realistic current from small RED cell: ~1-10 mA
    estimated_current_A = 0.005
    result.salinity_power_W = (
        result.salinity_voltage_V * estimated_current_A * site.salinity_efficiency
    )

    # --- Energy Source 2: Ocean Current Induction ---
    result.induction_voltage_V = ocean_current_induction_voltage(
        site.magnetic_field, site.current_velocity,
        site.electrode_separation, site.current_field_angle_deg
    )
    # Realistic load current for small electrodes in seawater
    induction_current_A = 0.001
    result.induction_power_W = (
        result.induction_voltage_V * induction_current_A * site.induction_efficiency
    )

    # --- Energy Source 3: Wave Energy ---
    power_per_m = wave_power_per_meter(site.wave_height, site.wave_period)
    result.wave_power_W = power_per_m * site.wave_crest_length * site.wave_efficiency

    # --- Total Power (additive, NOT multiplicative) ---
    result.total_power_W = (
        result.salinity_power_W +
        result.induction_power_W +
        result.wave_power_W
    )

    # --- Piezoelectric Voltage (supplementary) ---
    result.piezo_voltage_V = site.piezo_d33 * site.piezo_force

    # --- Iron Dispersal ---
    release_rate_kg_s = site.iron_release_rate_kg_per_hr / 3600.0
    result.iron_concentration_at_1km_ug_L = iron_concentration_downstream(
        release_rate_kg_s, site.current_speed_for_advection,
        site.diffusion_coefficient, 1000.0
    )
    # Plume radius at 1km downstream (2-sigma)
    D_turb = max(site.diffusion_coefficient, 0.01)
    result.iron_plume_radius_m = 2 * math.sqrt(
        2 * D_turb * 1000.0 / site.current_speed_for_advection
    )

    # --- Feasibility Warnings ---
    if result.total_power_W < 0.001:
        result.warnings.append(
            "Total power < 1 mW. Insufficient for active systems; "
            "consider passive iron release only."
        )
    if result.induction_voltage_V < 1e-6:
        result.warnings.append(
            f"Induction voltage extremely low ({result.induction_voltage_V:.2e} V). "
            "Ocean current EM harvesting is not practical at this scale."
        )
    target_low, target_high = 0.1, 1.0
    conc = result.iron_concentration_at_1km_ug_L
    if conc > target_high:
        result.warnings.append(
            f"Iron concentration at 1 km ({conc:.2f} μg/L) exceeds target range. "
            "Reduce release rate to avoid ecological harm."
        )
    elif conc < target_low and release_rate_kg_s > 0:
        result.warnings.append(
            f"Iron concentration at 1 km ({conc:.4f} μg/L) below effective range. "
            "Consider higher release rate or closer deployment."
        )

    return result


def format_report(result: SimulationResult, site: Optional[SiteConditions] = None) -> str:
    """Format simulation results as a readable report."""
    if site is None:
        site = SiteConditions()

    lines = [
        "=" * 60,
        "  OCEAN ELECTROMAGNETIC RESTORATION — SITE ASSESSMENT",
        "=" * 60,
        "",
        "ENERGY SOURCES (realistic steady-state estimates)",
        "-" * 50,
        f"  Salinity gradient (RED):  {result.salinity_voltage_V * 1000:.1f} mV  →  "
        f"{result.salinity_power_W * 1000:.3f} mW",
        f"  Ocean current induction:  {result.induction_voltage_V * 1e6:.1f} μV  →  "
        f"{result.induction_power_W * 1e6:.3f} μW",
        f"  Wave energy capture:      {result.wave_power_W:.1f} W",
        f"  Piezoelectric (supplement): {result.piezo_voltage_V * 1e6:.1f} μV",
        "",
        f"  TOTAL HARVESTABLE POWER:  {result.total_power_W:.2f} W",
        "",
        "IRON DISPERSAL",
        "-" * 50,
        f"  Release rate:             {site.iron_release_rate_kg_per_hr * 1000:.1f} g/hr",
        f"  Concentration at 1 km:    {result.iron_concentration_at_1km_ug_L:.4f} μg/L",
        f"  Target range:             0.1 – 1.0 μg/L",
        f"  Plume radius at 1 km:     {result.iron_plume_radius_m:.0f} m",
        "",
    ]

    if result.warnings:
        lines.append("WARNINGS")
        lines.append("-" * 50)
        for w in result.warnings:
            lines.append(f"  ⚠ {w}")
        lines.append("")

    lines.append("NOTE: Wave energy dominates by orders of magnitude over")
    lines.append("salinity and induction sources at community scale. The")
    lines.append("'multiplicative coupling' described in project documentation")
    lines.append("overstates energy from EM induction and salinity gradients.")
    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


if __name__ == "__main__":
    print("Running simulation with default coastal site conditions...\n")

    site = SiteConditions()
    result = run_simulation(site)
    print(format_report(result, site))

    # Example: La Jolla conditions
    print("\n\nLa Jolla Marine Sanctuary scenario:\n")
    la_jolla = SiteConditions(
        salinity_high=33.5,
        salinity_low=30.0,     # Modest gradient (no major river)
        temperature_K=290.0,   # ~17°C
        current_velocity=0.3,  # Moderate California Current
        magnetic_field=48e-6,  # Mid-latitude Pacific
        electrode_separation=2.0,
        wave_height=0.8,
        wave_period=10.0,
        wave_crest_length=5.0,
        iron_release_rate_kg_per_hr=0.0005,
        current_speed_for_advection=0.3,
    )
    result_lj = run_simulation(la_jolla)
    print(format_report(result_lj, la_jolla))
