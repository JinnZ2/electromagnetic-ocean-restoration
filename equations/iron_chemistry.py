"""
Iron Chemistry in Seawater

Models iron speciation, oxidation kinetics, and precipitation relevant to
marine iron fertilization. Based on established geochemistry literature.

Key processes:
  1. Fe²⁺ oxidation by dissolved O₂ (Millero et al., 1987)
  2. Fe³⁺ hydrolysis and precipitation (Liu & Millero, 2002)
  3. Iron dissolution from minerals (olivine, magnetite)
  4. Ligand complexation effects on iron residence time

WARNING: Iron release into marine environments requires regulatory approval.
See London Protocol (2013 amendment) and local marine protection laws.

References:
  - Millero, F.J., Sotolongo, S., Izaguirre, M. (1987). The oxidation
    kinetics of Fe(II) in seawater. Geochimica et Cosmochimica Acta,
    51(4), 793-801.
  - Liu, X., Millero, F.J. (2002). The solubility of iron in seawater.
    Marine Chemistry, 77(1), 43-54.
  - Millero, F.J. (1998). Solubility of Fe(III) in seawater. Earth and
    Planetary Science Letters, 154(1-4), 323-329.
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class SeawaterConditions:
    """Seawater conditions affecting iron chemistry."""
    temperature_C: float = 15.0    # degrees Celsius
    salinity_psu: float = 35.0     # practical salinity units
    pH: float = 8.1                # seawater pH (total scale)
    dissolved_O2_umol_kg: float = 250.0  # typical surface ocean
    depth_m: float = 0.0           # meters below surface


@dataclass
class IronState:
    """Iron concentrations and speciation."""
    fe2_dissolved_nM: float = 0.0   # dissolved Fe²⁺ (nanomolar)
    fe3_dissolved_nM: float = 0.0   # dissolved Fe³⁺ (nanomolar)
    fe3_colloidal_nM: float = 0.0   # colloidal Fe(III) oxyhydroxides
    fe_particulate_nM: float = 0.0  # particulate (precipitated) iron
    fe_ligand_nM: float = 0.0       # organically complexed iron (bioavailable)

    @property
    def total_dissolved_nM(self) -> float:
        return self.fe2_dissolved_nM + self.fe3_dissolved_nM + self.fe_ligand_nM

    @property
    def total_nM(self) -> float:
        return (self.fe2_dissolved_nM + self.fe3_dissolved_nM +
                self.fe3_colloidal_nM + self.fe_particulate_nM +
                self.fe_ligand_nM)

    @property
    def bioavailable_nM(self) -> float:
        """Iron accessible to phytoplankton: dissolved Fe²⁺ + ligand-bound."""
        return self.fe2_dissolved_nM + self.fe_ligand_nM


def fe2_oxidation_rate_constant(temperature_C: float, salinity_psu: float,
                                  pH: float) -> float:
    """Fe²⁺ oxidation rate constant in seawater.

    Rate law: -d[Fe²⁺]/dt = k × [Fe²⁺] × [O₂] × [OH⁻]²

    The rate constant k depends on temperature and ionic strength.
    From Millero et al. (1987), the rate in seawater at S=35:

        log k = 21.56 - 1545/T - 3.29×I^0.5 + 1.52×I

    where T is in Kelvin and I is ionic strength.

    Args:
        temperature_C: Temperature in Celsius
        salinity_psu: Salinity in PSU
        pH: Seawater pH (total scale)

    Returns:
        Rate constant k in M⁻³ s⁻¹ (for the rate law above)
    """
    T_K = temperature_C + 273.15
    # Ionic strength from salinity (Millero, 1998)
    I = 0.0199 * salinity_psu  # approximate

    # Millero's formula gives k in M⁻³ min⁻¹; convert to M⁻³ s⁻¹
    log_k_per_min = 21.56 - 1545.0 / T_K - 3.29 * math.sqrt(I) + 1.52 * I
    return 10 ** log_k_per_min / 60.0


def fe2_half_life(temperature_C: float, salinity_psu: float, pH: float,
                   dissolved_O2_umol_kg: float = 250.0) -> float:
    """Calculate Fe²⁺ half-life in seawater.

    The oxidation rate is strongly pH-dependent (squared OH⁻ dependence).
    Doubling [OH⁻] (increasing pH by 0.3) increases rate 4×.

    Args:
        temperature_C: Temperature in Celsius
        salinity_psu: Salinity in PSU
        pH: Seawater pH
        dissolved_O2_umol_kg: Dissolved O₂ concentration

    Returns:
        Half-life in seconds
    """
    k = fe2_oxidation_rate_constant(temperature_C, salinity_psu, pH)
    T_K = temperature_C + 273.15

    # Convert O₂ from μmol/kg to mol/L (approximate for seawater density)
    O2_M = dissolved_O2_umol_kg * 1e-6 * 1.025  # kg/L seawater density

    # [OH⁻] from pH using pure water Kw (NBS scale), since Millero's
    # rate constant was calibrated on the NBS pH scale.
    # pKw(T) = 4470/T + 0.01706T - 6.0846 (Harned & Hamer, 1933)
    pKw = 4470.0 / T_K + 0.01706 * T_K - 6.0846
    OH_M = 10 ** (-(pKw - pH))

    # Pseudo-first-order rate constant: k' = k × [O₂] × [OH⁻]²
    k_pseudo = k * O2_M * OH_M ** 2

    if k_pseudo <= 0:
        return float('inf')

    return math.log(2) / k_pseudo


def fe3_solubility(temperature_C: float, salinity_psu: float,
                    pH: float) -> float:
    """Thermodynamic solubility of Fe(III) in seawater.

    Fe³⁺ forms insoluble oxyhydroxides:
        Fe³⁺ + 3OH⁻ → Fe(OH)₃(s)

    Solubility depends on pH, temperature, and the crystallinity of the
    precipitate. Amorphous Fe(OH)₃ is more soluble than goethite/hematite.

    From Liu & Millero (2002), the solubility of Fe(III) in seawater
    at pH 8 is approximately 0.07-0.6 nM for amorphous Fe(OH)₃.

    Args:
        temperature_C: Temperature in Celsius
        salinity_psu: Salinity in PSU
        pH: Seawater pH

    Returns:
        Solubility in nM (nanomolar)
    """
    # Simplified from Liu & Millero (2002) Figure 4
    # Solubility minimum near pH 8-9
    # Using amorphous Fe(OH)₃ (freshly precipitated, most relevant)
    log_sol_pH8 = -0.7  # ~0.2 nM at pH 8
    # pH sensitivity: approximately -3 × (pH - 8) on log scale for pH > 7
    log_sol = log_sol_pH8 - 2.5 * (pH - 8.0)

    # Temperature correction (~+0.02 per degree above 25°C)
    log_sol += 0.015 * (temperature_C - 25.0)

    solubility_nM = 10 ** log_sol
    # Clamp to physically reasonable range
    return max(0.01, min(solubility_nM, 100.0))


def iron_dissolution_rate(surface_area_cm2: float, pH: float,
                           temperature_C: float,
                           mineral: str = "magnetite") -> float:
    """Dissolution rate of iron minerals in seawater.

    Passive dissolution of iron from mineral surfaces. Key for designing
    wave-agitated iron release chambers.

    Args:
        surface_area_cm2: Exposed mineral surface area (cm²)
        pH: Seawater pH
        temperature_C: Temperature in Celsius
        mineral: One of "magnetite", "olivine", "iron_filings"

    Returns:
        Dissolution rate in μg/hr of dissolved iron
    """
    # Dissolution rates from literature (mol/cm²/s at 25°C, pH 8):
    rates_mol_cm2_s = {
        "magnetite": 1e-12,     # Cornell & Schwertmann (2003)
        "olivine": 5e-12,       # Hangx & Spiers (2009)
        "iron_filings": 1e-10,  # Metallic iron, much faster than minerals
    }

    base_rate = rates_mol_cm2_s.get(mineral, 1e-11)

    # Temperature dependence (Arrhenius, Ea ~ 50 kJ/mol for silicate dissolution)
    Ea = 50000.0  # J/mol
    R = 8.314
    T_ref = 298.15
    T = temperature_C + 273.15
    temp_factor = math.exp((Ea / R) * (1 / T_ref - 1 / T))

    # pH dependence (dissolution increases at lower pH)
    # Approximately 10× faster per pH unit decrease below pH 7
    pH_factor = 10 ** max(0, (7.0 - pH))  # Only accelerates below pH 7
    if pH < 8.0:
        pH_factor = max(1.0, 10 ** (0.5 * (8.0 - pH)))

    rate_mol_cm2_s = base_rate * temp_factor * pH_factor

    # Convert mol/cm²/s → μg/hr
    # Fe molar mass = 55.845 g/mol
    rate_ug_hr = rate_mol_cm2_s * surface_area_cm2 * 55.845e6 * 3600.0

    return rate_ug_hr


def simulate_iron_plume(release_rate_ug_hr: float, current_speed_m_s: float,
                         conditions: Optional[SeawaterConditions] = None,
                         max_distance_m: float = 1000.0,
                         steps: int = 50) -> list:
    """Simulate Fe²⁺ concentration along a downstream plume.

    Models the competition between advection (carrying iron downstream)
    and oxidation (converting Fe²⁺ to Fe³⁺ which precipitates).

    Returns concentration profile as list of (distance_m, fe2_nM, total_fe_nM).

    Args:
        release_rate_ug_hr: Iron release rate in μg/hr (as Fe²⁺)
        current_speed_m_s: Current velocity in m/s
        conditions: Seawater conditions (uses defaults if None)
        max_distance_m: Maximum distance to model (m)
        steps: Number of spatial steps

    Returns:
        List of (distance_m, fe2_dissolved_nM, total_dissolved_nM) tuples
    """
    if conditions is None:
        conditions = SeawaterConditions()

    half_life_s = fe2_half_life(
        conditions.temperature_C, conditions.salinity_psu,
        conditions.pH, conditions.dissolved_O2_umol_kg
    )

    # Initial Fe²⁺ concentration at release point
    # release_rate (μg/hr) into a cross-sectional area of current
    # Assume plume cross-section starts at 1 m² and grows with turbulent diffusion
    D_turb = 0.01  # m²/s (coastal turbulent diffusion)
    release_rate_kg_s = release_rate_ug_hr * 1e-9 / 3600.0  # μg/hr → kg/s
    Fe_molar_mass = 55.845e-3  # kg/mol

    results = []
    dx = max_distance_m / steps

    for i in range(steps + 1):
        x = i * dx
        if x == 0:
            x = 0.1  # avoid singularity

        # Travel time to this point
        travel_time_s = x / current_speed_m_s

        # Plume cross-section grows with distance (turbulent diffusion)
        sigma = math.sqrt(2 * D_turb * x / current_speed_m_s)
        plume_area_m2 = math.pi * sigma ** 2
        plume_area_m2 = max(plume_area_m2, 0.1)  # minimum 0.1 m²

        # Concentration without oxidation (kg/m³)
        conc_kg_m3 = release_rate_kg_s / (current_speed_m_s * plume_area_m2)

        # Convert to nanomolar
        conc_nM_total = (conc_kg_m3 / Fe_molar_mass) * 1e9

        # Fe²⁺ fraction remaining after oxidation
        fe2_fraction = math.exp(-math.log(2) * travel_time_s / half_life_s)
        fe2_nM = conc_nM_total * fe2_fraction

        # Dissolved Fe³⁺ is limited by solubility
        fe3_sol = fe3_solubility(conditions.temperature_C,
                                  conditions.salinity_psu, conditions.pH)
        total_dissolved_nM = fe2_nM + min(fe3_sol, conc_nM_total * (1 - fe2_fraction))

        results.append((x, fe2_nM, total_dissolved_nM))

    return results


def print_plume_profile(profile: list, conditions: Optional[SeawaterConditions] = None) -> None:
    """Print iron plume concentration profile."""
    if conditions is None:
        conditions = SeawaterConditions()

    half_life = fe2_half_life(
        conditions.temperature_C, conditions.salinity_psu,
        conditions.pH, conditions.dissolved_O2_umol_kg
    )

    print("=" * 65)
    print("  IRON PLUME CONCENTRATION PROFILE")
    print("=" * 65)
    print(f"  Conditions: T={conditions.temperature_C}°C, S={conditions.salinity_psu} psu, "
          f"pH={conditions.pH}")
    print(f"  Fe²⁺ half-life: {half_life:.0f} s ({half_life / 60:.1f} min)")
    print()
    print(f"  {'Distance (m)':>14s}  {'Fe²⁺ (nM)':>10s}  {'Total diss. (nM)':>16s}  "
          f"{'Fe²⁺ (μg/L)':>12s}")
    print("  " + "-" * 58)

    # Print every ~10 rows
    step = max(1, len(profile) // 20)
    for i, (dist, fe2, total) in enumerate(profile):
        if i % step == 0 or i == len(profile) - 1:
            fe2_ug_L = fe2 * 55.845e-3  # nM to μg/L
            print(f"  {dist:14.0f}  {fe2:10.2f}  {total:16.2f}  {fe2_ug_L:12.4f}")

    print()
    print("  Target range for phytoplankton: 0.1–1.0 μg/L (1.8–17.9 nM)")
    print("  Fe²⁺ = bioavailable form; Fe³⁺ precipitates rapidly")
    print("=" * 65)


if __name__ == "__main__":
    print("Iron Chemistry in Seawater — Demonstration\n")

    # 1. Half-life sensitivity to pH
    print("Fe²⁺ half-life vs pH (15°C, S=35, O₂=250 μmol/kg):")
    print(f"  {'pH':>6s}  {'Half-life':>12s}")
    print("  " + "-" * 22)
    for pH_val in [7.0, 7.5, 7.8, 8.0, 8.1, 8.2, 8.5]:
        hl = fe2_half_life(15.0, 35.0, pH_val)
        if hl > 3600:
            print(f"  {pH_val:6.1f}  {hl / 3600:9.1f} hr")
        elif hl > 60:
            print(f"  {pH_val:6.1f}  {hl / 60:9.1f} min")
        else:
            print(f"  {pH_val:6.1f}  {hl:9.1f} s")

    # 2. Fe³⁺ solubility
    print(f"\nFe(III) solubility (amorphous Fe(OH)₃, 15°C, S=35):")
    print(f"  {'pH':>6s}  {'Solubility (nM)':>16s}")
    print("  " + "-" * 26)
    for pH_val in [7.0, 7.5, 8.0, 8.1, 8.2, 8.5, 9.0]:
        sol = fe3_solubility(15.0, 35.0, pH_val)
        print(f"  {pH_val:6.1f}  {sol:16.3f}")

    # 3. Mineral dissolution rates
    print(f"\nIron dissolution rates (1000 cm² surface, pH 8.1, 15°C):")
    for mineral in ["magnetite", "olivine", "iron_filings"]:
        rate = iron_dissolution_rate(1000.0, 8.1, 15.0, mineral)
        print(f"  {mineral:15s}: {rate:.3f} μg/hr ({rate / 1000:.4f} mg/hr)")

    # 4. Plume profile
    print(f"\nIron plume from 500 μg/hr release at 0.3 m/s current:\n")
    conditions = SeawaterConditions(temperature_C=15.0, pH=8.1)
    profile = simulate_iron_plume(500.0, 0.3, conditions, max_distance_m=500.0)
    print_plume_profile(profile, conditions)
