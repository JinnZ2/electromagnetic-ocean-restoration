"""
Wave Energy Capture

Models ocean wave power and community-scale wave energy converter sizing.
Focuses on oscillating water column (OWC) devices as the most practical
community-buildable option.

Key equations:
  Deep-water wave power: P = (ρ g² H² T) / (32π)  [W/m]
  OWC capture: P_cap = P × W × η_owc
  Annual energy: E = P_cap × capacity_factor × 8760  [Wh/year]

References:
  - Falnes, J. (2007). A review of wave-energy extraction.
    Marine Structures, 20(4), 185-201.
  - Heath, T.V. (2012). A review of oscillating water columns.
    Philosophical Transactions of the Royal Society A, 370, 235-245.
  - Barstow, S. et al. (2008). WorldWaves wave energy resource assessments
    from the deep ocean to the coast. Journal of Energy and Power
    Engineering, 2, 29-42.
"""

import math
from dataclasses import dataclass
from typing import Optional

# Physical constants
RHO_SW = 1025.0    # Seawater density (kg/m³)
G = 9.81           # Gravitational acceleration (m/s²)


@dataclass
class WaveConditions:
    """Wave climate at a deployment site."""
    significant_height_m: float = 1.0   # Hs (m)
    peak_period_s: float = 8.0          # Tp (s)
    # Seasonal variation
    summer_Hs_m: float = 0.6
    winter_Hs_m: float = 1.5
    summer_Tp_s: float = 7.0
    winter_Tp_s: float = 10.0


@dataclass
class OWCDevice:
    """Oscillating Water Column device parameters."""
    chamber_width_m: float = 5.0        # Width perpendicular to wave crests
    chamber_depth_m: float = 3.0        # Submerged depth
    chamber_length_m: float = 2.0       # Length in wave direction
    turbine_type: str = "wells"         # "wells", "impulse", or "check_valve"
    # Efficiency depends on turbine type
    # Wells: 15-25%, impulse: 20-35%, check_valve (simplest): 5-10%


@dataclass
class WaveEnergyResult:
    """Wave energy calculation results."""
    wave_power_per_meter_W: float = 0.0
    wavelength_m: float = 0.0
    available_power_W: float = 0.0
    captured_power_W: float = 0.0
    efficiency: float = 0.0
    annual_energy_kWh: float = 0.0
    capacity_factor: float = 0.0


def deep_water_wave_power(Hs: float, Tp: float) -> float:
    """Wave power per meter of wave crest in deep water.

    P = (ρ × g² × Hs² × Tp) / (32π)

    This is the time-averaged power transported by a sea state characterized
    by significant wave height Hs and peak period Tp.

    Derivation: from linear wave theory, energy density E = ρgHs²/16,
    group velocity cg = gTp/(4π), and P = E × cg.

    Args:
        Hs: Significant wave height (m)
        Tp: Peak wave period (s)

    Returns:
        Power in watts per meter of wave crest
    """
    return (RHO_SW * G ** 2 * Hs ** 2 * Tp) / (32 * math.pi)


def wavelength(period_s: float, depth_m: Optional[float] = None) -> float:
    """Wave wavelength from period.

    Deep water: L = g × T² / (2π)
    Shallow water: iterative solution of L = (gT²/2π) × tanh(2πd/L)

    Args:
        period_s: Wave period (s)
        depth_m: Water depth (m). If None, uses deep-water approximation.

    Returns:
        Wavelength in meters
    """
    L0 = G * period_s ** 2 / (2 * math.pi)  # deep-water wavelength

    if depth_m is None or depth_m > L0 / 2:
        return L0

    # Iterative solution for finite depth
    L = L0
    for _ in range(50):
        L_new = L0 * math.tanh(2 * math.pi * depth_m / L)
        if abs(L_new - L) < 0.001:
            break
        L = L_new
    return L


def owc_efficiency(turbine_type: str, wave_height: float,
                    chamber_depth: float) -> float:
    """Estimate OWC conversion efficiency.

    Efficiency depends on:
    - Turbine type (Wells, impulse, simple check valve)
    - Wave height relative to chamber depth (overtopping losses)
    - Resonance tuning (chamber dimensions vs wave period)

    Conservative estimates based on Heath (2012) review.

    Args:
        turbine_type: "wells", "impulse", or "check_valve"
        wave_height: Significant wave height (m)
        chamber_depth: Submerged depth of chamber (m)

    Returns:
        Conversion efficiency (0-1)
    """
    # Base efficiencies (time-averaged, including off-design conditions)
    base_eff = {
        "wells": 0.18,         # 15-25%, use 18% average
        "impulse": 0.25,       # 20-35%, use 25% average
        "check_valve": 0.07,   # 5-10%, simplest community build
    }

    eta = base_eff.get(turbine_type, 0.10)

    # Penalty for excessive wave height (overtopping)
    if wave_height > chamber_depth * 0.8:
        overtopping_factor = chamber_depth * 0.8 / wave_height
        eta *= overtopping_factor

    # Penalty for very small waves (viscous losses dominate)
    if wave_height < 0.3:
        eta *= wave_height / 0.3

    return eta


def calculate_owc_performance(waves: Optional[WaveConditions] = None,
                                device: Optional[OWCDevice] = None
                                ) -> WaveEnergyResult:
    """Calculate OWC wave energy converter performance.

    Args:
        waves: Wave conditions at site
        device: OWC device parameters

    Returns:
        WaveEnergyResult with power and energy estimates
    """
    if waves is None:
        waves = WaveConditions()
    if device is None:
        device = OWCDevice()

    result = WaveEnergyResult()

    # Wave power per meter
    result.wave_power_per_meter_W = deep_water_wave_power(
        waves.significant_height_m, waves.peak_period_s
    )
    result.wavelength_m = wavelength(waves.peak_period_s)

    # Available power over device width
    result.available_power_W = result.wave_power_per_meter_W * device.chamber_width_m

    # Efficiency
    result.efficiency = owc_efficiency(
        device.turbine_type, waves.significant_height_m, device.chamber_depth_m
    )
    result.captured_power_W = result.available_power_W * result.efficiency

    # Annual energy with seasonal variation and capacity factor
    # Calculate seasonal powers
    summer_P = deep_water_wave_power(waves.summer_Hs_m, waves.summer_Tp_s)
    winter_P = deep_water_wave_power(waves.winter_Hs_m, waves.winter_Tp_s)

    summer_eff = owc_efficiency(device.turbine_type, waves.summer_Hs_m,
                                 device.chamber_depth_m)
    winter_eff = owc_efficiency(device.turbine_type, waves.winter_Hs_m,
                                 device.chamber_depth_m)

    summer_cap = summer_P * device.chamber_width_m * summer_eff
    winter_cap = winter_P * device.chamber_width_m * winter_eff

    # 6 months each, simplified
    annual_avg_W = (summer_cap + winter_cap) / 2
    result.annual_energy_kWh = annual_avg_W * 8760 / 1000

    # Capacity factor: actual annual output / (peak seasonal × 8760)
    peak_seasonal_W = max(summer_cap, winter_cap, result.captured_power_W)
    if peak_seasonal_W > 0:
        result.capacity_factor = annual_avg_W / peak_seasonal_W
    else:
        result.capacity_factor = 0.0

    return result


def print_sizing_table() -> None:
    """Print device sizing table for various wave conditions."""
    print("=" * 78)
    print("  WAVE ENERGY DEVICE SIZING TABLE")
    print("=" * 78)
    print()
    print("  Wave power per meter of wave crest (deep water):")
    print(f"  {'Hs (m)':>8s}  {'Tp (s)':>8s}  {'P (W/m)':>10s}  {'P (kW/m)':>10s}  "
          f"{'λ (m)':>8s}")
    print("  " + "-" * 50)

    for Hs in [0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0]:
        for Tp in [6, 8, 10, 12]:
            P = deep_water_wave_power(Hs, Tp)
            L = wavelength(Tp)
            print(f"  {Hs:8.1f}  {Tp:8.0f}  {P:10.0f}  {P / 1000:10.2f}  {L:8.0f}")
        print()

    print()
    print("  OWC CAPTURED POWER (5m wide chamber, 3m deep)")
    print("  " + "-" * 70)
    print(f"  {'Hs':>4s}  {'Tp':>4s}  {'Check valve (7%)':>18s}  "
          f"{'Wells (18%)':>14s}  {'Impulse (25%)':>16s}")
    print(f"  {'(m)':>4s}  {'(s)':>4s}  {'(W)':>18s}  {'(W)':>14s}  {'(W)':>16s}")
    print("  " + "-" * 70)

    device_base = OWCDevice(chamber_width_m=5.0, chamber_depth_m=3.0)
    for Hs, Tp in [(0.5, 6), (0.8, 8), (1.0, 8), (1.0, 10),
                    (1.5, 10), (2.0, 12)]:
        waves = WaveConditions(significant_height_m=Hs, peak_period_s=Tp)
        results = []
        for turbine in ["check_valve", "wells", "impulse"]:
            device = OWCDevice(chamber_width_m=5.0, chamber_depth_m=3.0,
                               turbine_type=turbine)
            r = calculate_owc_performance(waves, device)
            results.append(r.captured_power_W)
        print(f"  {Hs:4.1f}  {Tp:4.0f}  {results[0]:18.0f}  {results[1]:14.0f}  "
              f"{results[2]:16.0f}")

    print()
    print("  Check valve: simplest build (concrete + rubber flaps)")
    print("  Wells turbine: requires machining, self-rectifying airflow")
    print("  Impulse turbine: highest efficiency, most complex")
    print("=" * 78)


def print_annual_estimate(waves: Optional[WaveConditions] = None,
                           device: Optional[OWCDevice] = None) -> None:
    """Print annual energy production estimate."""
    if waves is None:
        waves = WaveConditions()
    if device is None:
        device = OWCDevice()

    result = calculate_owc_performance(waves, device)

    print("=" * 60)
    print("  ANNUAL ENERGY PRODUCTION ESTIMATE")
    print("=" * 60)
    print(f"  Device: {device.chamber_width_m:.0f}m wide OWC, "
          f"{device.turbine_type} turbine")
    print(f"  Annual mean Hs: {waves.significant_height_m:.1f} m, "
          f"Tp: {waves.peak_period_s:.0f} s")
    print(f"  Seasonal range: Hs {waves.summer_Hs_m:.1f}–"
          f"{waves.winter_Hs_m:.1f} m")
    print()
    print(f"  Wave power density:  {result.wave_power_per_meter_W / 1000:.1f} kW/m")
    print(f"  Available (at width): {result.available_power_W / 1000:.1f} kW")
    print(f"  Conversion efficiency: {result.efficiency * 100:.0f}%")
    print(f"  Rated capture:       {result.captured_power_W / 1000:.2f} kW")
    print(f"  Capacity factor:     {result.capacity_factor:.0%}")
    print(f"  Annual energy:       {result.annual_energy_kWh:.0f} kWh/year")
    print()

    # Context: what this powers
    avg_W = result.annual_energy_kWh * 1000 / 8760
    print(f"  Average continuous power: {avg_W:.0f} W")
    print()
    print("  This powers:")
    if avg_W >= 500:
        print("    ✓ Electrochemical pH cell (50 L/min)")
    if avg_W >= 50:
        print("    ✓ Iron dosing pump + controller")
    if avg_W >= 20:
        print("    ✓ Full sensor suite (pH, DO, temp, salinity, chlorophyll)")
    if avg_W >= 5:
        print("    ✓ Data logger + cellular/LoRa telemetry")
    if avg_W < 5:
        print("    ✗ Insufficient for active systems")
        print("    → Use for passive monitoring only (battery + solar backup)")
    print("=" * 60)


if __name__ == "__main__":
    print("Wave Energy Capture — Demonstration\n")

    # 1. Sizing table
    print_sizing_table()

    # 2. Annual estimate for La Jolla
    print("\n\nLa Jolla site estimate:\n")
    la_jolla_waves = WaveConditions(
        significant_height_m=0.9,
        peak_period_s=10.0,
        summer_Hs_m=0.6,
        winter_Hs_m=1.3,
        summer_Tp_s=8.0,
        winter_Tp_s=12.0,
    )
    la_jolla_device = OWCDevice(
        chamber_width_m=5.0,
        chamber_depth_m=3.0,
        turbine_type="wells",
    )
    print_annual_estimate(la_jolla_waves, la_jolla_device)

    # 3. Budget build estimate
    print("\n\nBudget build (2m check-valve OWC, moderate waves):\n")
    budget_waves = WaveConditions(
        significant_height_m=0.8,
        peak_period_s=7.0,
        summer_Hs_m=0.5,
        winter_Hs_m=1.1,
        summer_Tp_s=6.0,
        winter_Tp_s=9.0,
    )
    budget_device = OWCDevice(
        chamber_width_m=2.0,
        chamber_depth_m=2.0,
        turbine_type="check_valve",
    )
    print_annual_estimate(budget_waves, budget_device)
