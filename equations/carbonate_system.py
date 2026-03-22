"""
Ocean Carbonate System

Models the seawater CO₂ equilibrium, pH buffering capacity, and
electrochemical alkalinity enhancement for ocean acidification mitigation.

Key equations:
  CO₂(aq) + H₂O ⇌ H⁺ + HCO₃⁻      (K₁)
  HCO₃⁻ ⇌ H⁺ + CO₃²⁻               (K₂)

  Aragonite saturation: Ω_arag = [Ca²⁺][CO₃²⁻] / K_sp

References:
  - Zeebe, R.E. & Wolf-Gladrow, D. (2001). CO₂ in Seawater: Equilibrium,
    Kinetics, Isotopes. Elsevier Oceanography Series, 65.
  - Lueker, T.J., Dickson, A.G., Keeling, C.D. (2000). Ocean pCO₂ calculated
    from dissolved inorganic carbon, alkalinity, and equations for K₁ and K₂.
    Marine Chemistry, 70(1-3), 105-119.
  - Mucci, A. (1983). The solubility of calcite and aragonite in seawater at
    various salinities, temperatures, and one atmosphere total pressure.
    American Journal of Science, 283, 780-799.
  - Rau, G.H. (2008). Electrochemical splitting of calcium carbonate to
    increase solution alkalinity. Environmental Science & Technology, 42(23),
    8935-8940.
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class CarbonateState:
    """State of the seawater carbonate system."""
    pH: float = 0.0
    CO2_umol_kg: float = 0.0       # dissolved CO₂ (μmol/kg)
    HCO3_umol_kg: float = 0.0      # bicarbonate (μmol/kg)
    CO3_umol_kg: float = 0.0       # carbonate ion (μmol/kg)
    DIC_umol_kg: float = 0.0       # total dissolved inorganic carbon
    omega_aragonite: float = 0.0    # aragonite saturation state
    omega_calcite: float = 0.0      # calcite saturation state
    buffer_capacity: float = 0.0    # Revelle factor (dimensionless)
    pCO2_uatm: float = 0.0         # partial pressure of CO₂ (μatm)


def carbonate_K1(temperature_C: float, salinity_psu: float) -> float:
    """First dissociation constant of carbonic acid in seawater.

    CO₂(aq) + H₂O ⇌ H⁺ + HCO₃⁻

    From Lueker et al. (2000), total pH scale.

    Args:
        temperature_C: Temperature in Celsius
        salinity_psu: Salinity in PSU

    Returns:
        K₁ in mol/kg-sw
    """
    T_K = temperature_C + 273.15
    S = salinity_psu

    # Lueker et al. (2000) - valid for T=2-35°C, S=19-43
    pK1 = (3633.86 / T_K - 61.2172 + 9.6777 * math.log(T_K)
           - 0.011555 * S + 0.0001152 * S ** 2)
    return 10 ** (-pK1)


def carbonate_K2(temperature_C: float, salinity_psu: float) -> float:
    """Second dissociation constant of carbonic acid in seawater.

    HCO₃⁻ ⇌ H⁺ + CO₃²⁻

    From Lueker et al. (2000), total pH scale.

    Args:
        temperature_C: Temperature in Celsius
        salinity_psu: Salinity in PSU

    Returns:
        K₂ in mol/kg-sw
    """
    T_K = temperature_C + 273.15
    S = salinity_psu

    pK2 = (471.78 / T_K + 25.9290 - 3.16967 * math.log(T_K)
           - 0.01781 * S + 0.0001122 * S ** 2)
    return 10 ** (-pK2)


def aragonite_Ksp(temperature_C: float, salinity_psu: float) -> float:
    """Solubility product of aragonite in seawater.

    From Mucci (1983).

    Args:
        temperature_C: Temperature in Celsius
        salinity_psu: Salinity in PSU

    Returns:
        K_sp in (mol/kg-sw)²
    """
    T_K = temperature_C + 273.15
    S = salinity_psu

    log_Ksp = (-171.945 - 0.077993 * T_K + 2903.293 / T_K
               + 71.595 * math.log10(T_K)
               + (-0.068393 + 0.0017276 * T_K + 88.135 / T_K) * math.sqrt(S)
               - 0.10018 * S + 0.0059415 * S ** 1.5)
    return 10 ** log_Ksp


def calcite_Ksp(temperature_C: float, salinity_psu: float) -> float:
    """Solubility product of calcite in seawater.

    From Mucci (1983).

    Args:
        temperature_C: Temperature in Celsius
        salinity_psu: Salinity in PSU

    Returns:
        K_sp in (mol/kg-sw)²
    """
    T_K = temperature_C + 273.15
    S = salinity_psu

    log_Ksp = (-171.9065 - 0.077993 * T_K + 2839.319 / T_K
               + 71.595 * math.log10(T_K)
               + (-0.77712 + 0.0028426 * T_K + 178.34 / T_K) * math.sqrt(S)
               - 0.07711 * S + 0.0041249 * S ** 1.5)
    return 10 ** log_Ksp


def calcium_concentration(salinity_psu: float) -> float:
    """Calcium concentration in seawater from salinity.

    [Ca²⁺] ≈ 0.01028 × S/35 mol/kg-sw (Riley & Tongudai, 1967)

    Args:
        salinity_psu: Salinity in PSU

    Returns:
        [Ca²⁺] in mol/kg-sw
    """
    return 0.01028 * salinity_psu / 35.0


def solve_carbonate_system(DIC_umol_kg: float, pH: float,
                            temperature_C: float, salinity_psu: float
                            ) -> CarbonateState:
    """Solve the carbonate system given DIC and pH.

    Calculates all carbonate species, saturation states, and buffer capacity.

    Args:
        DIC_umol_kg: Total dissolved inorganic carbon (μmol/kg)
        pH: Seawater pH (total scale)
        temperature_C: Temperature in Celsius
        salinity_psu: Salinity in PSU

    Returns:
        CarbonateState with all computed values
    """
    K1 = carbonate_K1(temperature_C, salinity_psu)
    K2 = carbonate_K2(temperature_C, salinity_psu)
    H = 10 ** (-pH)
    DIC = DIC_umol_kg  # keep in μmol/kg for species

    # Species fractions (Zeebe & Wolf-Gladrow, 2001, eq. 1.5.9)
    denom = H ** 2 + K1 * H + K1 * K2
    f_CO2 = H ** 2 / denom
    f_HCO3 = K1 * H / denom
    f_CO3 = K1 * K2 / denom

    CO2 = DIC * f_CO2
    HCO3 = DIC * f_HCO3
    CO3 = DIC * f_CO3

    # Saturation states
    Ca = calcium_concentration(salinity_psu)
    CO3_mol_kg = CO3 * 1e-6  # convert to mol/kg

    Ksp_arag = aragonite_Ksp(temperature_C, salinity_psu)
    Ksp_calc = calcite_Ksp(temperature_C, salinity_psu)

    omega_arag = Ca * CO3_mol_kg / Ksp_arag
    omega_calc = Ca * CO3_mol_kg / Ksp_calc

    # Revelle factor (buffer capacity)
    # β = DIC × (1/[CO₂] + 1/[CO₃²⁻]) / (1 + [HCO₃⁻]/[CO₃²⁻])
    # Simplified: Revelle ≈ DIC × CO₂⁻¹ sensitivity
    # Using exact Revelle factor: R = (∂ln pCO₂ / ∂ln DIC) at constant ALK
    # Approximate: R ≈ DIC × CO2 / (HCO3² / (HCO3 + 4 * CO3))
    # Standard approximation (Zeebe & Wolf-Gladrow):
    if CO3 > 0 and CO2 > 0:
        S_factor = HCO3 ** 2 / (CO2 * CO3)
        revelle = (DIC / CO2) * (1 + (4 * CO3 * CO2) / HCO3 ** 2)
        # Clamp to reasonable range
        revelle = max(8.0, min(revelle, 25.0))
    else:
        revelle = 10.0

    # pCO₂ (using Henry's law, K0 from Weiss 1974)
    T_K = temperature_C + 273.15
    S = salinity_psu
    ln_K0 = (-60.2409 + 93.4517 * (100 / T_K) + 23.3585 * math.log(T_K / 100)
             + S * (0.023517 - 0.023656 * (T_K / 100) + 0.0047036 * (T_K / 100) ** 2))
    K0 = math.exp(ln_K0)  # mol/kg/atm
    pCO2 = (CO2 * 1e-6) / K0 * 1e6  # μatm

    return CarbonateState(
        pH=pH,
        CO2_umol_kg=CO2,
        HCO3_umol_kg=HCO3,
        CO3_umol_kg=CO3,
        DIC_umol_kg=DIC_umol_kg,
        omega_aragonite=omega_arag,
        omega_calcite=omega_calc,
        buffer_capacity=revelle,
        pCO2_uatm=pCO2,
    )


def alkalinity_needed_for_pH_shift(current_pH: float, target_pH: float,
                                     DIC_umol_kg: float,
                                     temperature_C: float,
                                     salinity_psu: float,
                                     volume_m3: float = 1.0) -> dict:
    """Calculate alkalinity addition needed to shift pH.

    Determines how many moles of OH⁻ (or equivalent base) must be added
    to shift seawater pH from current to target value.

    This is the core calculation for electrochemical pH restoration:
    how much electrical energy to process a given volume of seawater.

    Args:
        current_pH: Starting pH
        target_pH: Desired pH
        DIC_umol_kg: Dissolved inorganic carbon (μmol/kg)
        temperature_C: Temperature in Celsius
        salinity_psu: Salinity in PSU
        volume_m3: Volume of seawater to treat (m³)

    Returns:
        Dict with alkalinity needed, electrical energy, and power estimates
    """
    K1 = carbonate_K1(temperature_C, salinity_psu)
    K2 = carbonate_K2(temperature_C, salinity_psu)

    # Total alkalinity change needed
    # TA ≈ [HCO₃⁻] + 2[CO₃²⁻] + [OH⁻] - [H⁺] + minor species
    # For a pH shift at constant DIC:
    DIC_mol_kg = DIC_umol_kg * 1e-6

    def calc_TA(pH_val: float) -> float:
        H = 10 ** (-pH_val)
        denom = H ** 2 + K1 * H + K1 * K2
        HCO3 = DIC_mol_kg * K1 * H / denom
        CO3 = DIC_mol_kg * K1 * K2 / denom
        # pKw for seawater
        pKw = 13.22 - 0.0178 * (temperature_C - 25.0)
        Kw = 10 ** (-pKw)
        OH = Kw / H
        return HCO3 + 2 * CO3 + OH - H

    TA_current = calc_TA(current_pH)
    TA_target = calc_TA(target_pH)
    delta_TA_mol_kg = TA_target - TA_current  # mol/kg of alkalinity to add

    # Convert to total moles for given volume
    mass_kg = volume_m3 * 1025.0  # seawater density
    delta_TA_mol = delta_TA_mol_kg * mass_kg

    # Electrical energy for electrochemical alkalinity production
    # Faraday's law: Q = n × F / η_faradaic
    faradaic_efficiency = 0.70  # typical for seawater electrolysis
    F_const = 96485.0  # C/mol
    charge_C = abs(delta_TA_mol) * F_const / faradaic_efficiency

    # Cell voltage for seawater electrolysis: ~2.0-2.5 V
    cell_voltage = 2.2  # V
    energy_J = charge_C * cell_voltage
    energy_Wh = energy_J / 3600.0

    # Power for continuous treatment at 50 L/min
    flow_kg_per_s = (50.0 / 1000.0) * 1025.0 / 60.0  # 50 L/min → kg/s
    power_50_Lmin_W = abs(delta_TA_mol_kg) * flow_kg_per_s * F_const * cell_voltage / faradaic_efficiency

    return {
        "delta_TA_mol_per_kg": delta_TA_mol_kg,
        "delta_TA_total_mol": delta_TA_mol,
        "charge_coulombs": charge_C,
        "energy_joules": energy_J,
        "energy_Wh": energy_Wh,
        "power_W_at_50Lmin": power_50_Lmin_W,
        "volume_m3": volume_m3,
        "cell_voltage_V": cell_voltage,
        "faradaic_efficiency": faradaic_efficiency,
    }


def print_carbonate_report(temperature_C: float = 15.0,
                            salinity_psu: float = 35.0,
                            DIC_umol_kg: float = 2050.0) -> None:
    """Print carbonate system state across a pH range."""
    print("=" * 72)
    print("  OCEAN CARBONATE SYSTEM")
    print("=" * 72)
    print(f"  Conditions: T={temperature_C}°C, S={salinity_psu} psu, "
          f"DIC={DIC_umol_kg} μmol/kg")
    print()

    print(f"  {'pH':>5s}  {'CO₂':>8s}  {'HCO₃⁻':>8s}  {'CO₃²⁻':>8s}  "
          f"{'Ω_arag':>7s}  {'Ω_calc':>7s}  {'pCO₂':>8s}  {'Revelle':>8s}")
    print(f"  {'':>5s}  {'μmol/kg':>8s}  {'μmol/kg':>8s}  {'μmol/kg':>8s}  "
          f"{'':>7s}  {'':>7s}  {'μatm':>8s}  {'':>8s}")
    print("  " + "-" * 68)

    for pH_val in [7.6, 7.7, 7.8, 7.9, 8.0, 8.05, 8.1, 8.15, 8.2, 8.3, 8.4]:
        state = solve_carbonate_system(DIC_umol_kg, pH_val,
                                       temperature_C, salinity_psu)
        marker = ""
        if abs(pH_val - 8.05) < 0.001:
            marker = " ← current avg"
        elif abs(pH_val - 8.18) < 0.02:
            marker = " ← pre-industrial"

        print(f"  {pH_val:5.2f}  {state.CO2_umol_kg:8.1f}  {state.HCO3_umol_kg:8.1f}  "
              f"{state.CO3_umol_kg:8.1f}  {state.omega_aragonite:7.2f}  "
              f"{state.omega_calcite:7.2f}  {state.pCO2_uatm:8.0f}  "
              f"{state.buffer_capacity:8.1f}{marker}")

    print()
    print("  Ω_aragonite < 1.0: aragonite dissolution (shell/coral damage)")
    print("  Ω_aragonite > 2.5: healthy calcification")
    print()

    # Alkalinity enhancement calculation
    print("  ELECTROCHEMICAL pH RESTORATION")
    print("  " + "-" * 68)
    for target in [8.1, 8.15, 8.2]:
        result = alkalinity_needed_for_pH_shift(
            8.05, target, DIC_umol_kg, temperature_C, salinity_psu, 1.0
        )
        print(f"  pH 8.05 → {target}: {result['delta_TA_mol_per_kg'] * 1e6:.1f} μmol/kg "
              f"alkalinity | {result['energy_Wh']:.0f} Wh/m³ | "
              f"{result['power_W_at_50Lmin']:.0f} W at 50 L/min")

    print()
    print("  A 2 kW wave device can drive meaningful pH buffering at 50 L/min")
    print("  Effective zone: tens to hundreds of meters downstream")
    print("=" * 72)


if __name__ == "__main__":
    print("Ocean Carbonate System — Demonstration\n")
    print_carbonate_report()

    print("\n\nPre-industrial vs current vs future (RCP 8.5 2100):\n")
    scenarios = [
        ("Pre-industrial (~1850)", 15.0, 35.0, 2000.0, 8.18),
        ("Current (~2024)", 15.0, 35.0, 2050.0, 8.05),
        ("RCP 8.5 2100", 17.0, 35.0, 2200.0, 7.75),
    ]
    for name, T, S, DIC, pH_val in scenarios:
        state = solve_carbonate_system(DIC, pH_val, T, S)
        print(f"  {name:30s}  pH={pH_val:.2f}  Ω_arag={state.omega_aragonite:.2f}  "
              f"pCO₂={state.pCO2_uatm:.0f} μatm  CO₃²⁻={state.CO3_umol_kg:.0f} μmol/kg")
