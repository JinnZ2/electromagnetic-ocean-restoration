# Electromagnetic Ocean Restoration

**Community-Deployable Systems for Marine Ecosystem Restoration**

## What This Project Does

This project provides open-source tools for coastal communities to build and deploy small-scale ocean restoration systems that combine:

1. **Wave energy capture** — harvest mechanical energy from ocean waves to power restoration equipment
2. **Controlled iron release** — deliver bioavailable iron to iron-limited marine ecosystems
3. **Electrochemical pH buffering** — use harvested energy to drive alkalinity enhancement

These three mechanisms are well-studied individually. This project integrates them into community-deployable packages and provides the physics, chemistry, and engineering models to plan deployments.

## Honest Energy Budget

Not all energy sources are equal. Here is what the physics actually gives you at community scale:

| Energy Source | Voltage / Power | Practical? | Notes |
|---|---|---|---|
| **Wave energy** (1m wave, 8s period, 10m capture) | ~39 kW available, ~7 kW captured | **Yes** | Dominant source. Well-proven technology. |
| **Salinity gradient** (river mouth, small RED cell) | ~50 mV, ~0.07 mW | Marginal | Needs large membrane area to be useful. Research-scale. |
| **Ocean current EM induction** | ~25 μV, ~0.003 μW | **No** | Earth's field is ~50 μT. Yields microwatts. Not practical. |
| **Piezoelectric** | ~0.05 μV per element | **No** | Supplementary sensor power only. |
| **Solar/CME coupling** | N/A at surface | **No** | Affects ionosphere, not coastal devices. |

**Bottom line**: Wave energy is the only viable power source at community scale. The other mechanisms are real physics but produce negligible power in small installations. This project focuses on wave-powered iron delivery and electrochemical restoration.

## Scientific Foundation

### Climate context (2025 observations)

From [State of the Climate in 2025](https://journals.ametsoc.org/view/journals/bams/107/8/2026BAMSStateoftheClimate.1.xml) (BAMS vol. 107 no. 8, published 10 August 2026; 625 scientists, 60 countries) — the figures that bear on what this project models:

| Indicator | 2025 value | Relevance here |
|---|---|---|
| Atmospheric CO₂ | 425.6 ± 0.1 ppm (+53% vs pre-industrial) | Sets the equilibrium pH the carbonate model solves for |
| Ocean heat content (0–2000 m) | Record high | Oceans hold ~90% of excess trapped heat |
| Sea surface temperature | 3rd highest in 172 years, despite cool ENSO | Temperature is an input to every module here |
| Marine heatwaves | **87%** of the ocean surface saw at least one | The stressor local restoration is responding to |

**Read this as scale, not as a mandate.** A community device buffers its own plume — meters to hundreds of meters. It does not move any number in that table. Ocean pH is set by global CO₂; local buffering helps a local ecosystem survive while the root cause is addressed elsewhere. This is triage, not cure.

The report's other headline findings — Arctic sea-ice age collapse, 38 consecutive years of glacier loss, record Antarctic warmth, sea level at 111.2 mm above the 1993 baseline, 97 named tropical cyclones — are not integrated here because none of them is an input to, or a consequence of, the physics in `equations/`. They are not less important; they are just not what this code computes.

### Iron Fertilization

Iron limits phytoplankton growth across ~30% of the ocean surface (the "High-Nutrient Low-Chlorophyll" regions). Adding small amounts of bioavailable iron (0.1–1.0 μg/L as dissolved Fe²⁺) stimulates phytoplankton blooms that:

- Fix CO₂ through photosynthesis
- Support marine food webs (phytoplankton → zooplankton → fish)
- Produce dimethyl sulfide (DMS) that seeds cloud formation

This has been demonstrated in 13+ open-ocean experiments (SOIREE, SOFeX, LOHAFEX, SERIES, etc.). The science is real; the debate is about permanence of carbon sequestration and unintended ecological effects.

**Key constraint**: Fe²⁺ oxidizes to Fe³⁺ in oxygenated seawater with a half-life of minutes to hours (pH and temperature dependent). Fe³⁺ rapidly forms insoluble oxyhydroxides and precipitates. Sustained delivery matters more than total mass.

### Ocean Alkalinity Enhancement

Ocean acidification reduces carbonate ion availability, threatening calcifying organisms.

The driver is measured, not modelled. [State of the Climate in 2025](https://journals.ametsoc.org/view/journals/bams/107/8/2026BAMSStateoftheClimate.1.xml) (BAMS, August 2026) reports atmospheric CO₂ at **425.6 ± 0.1 ppm**, 53% above the ~278 ppm pre-industrial baseline. Feeding those two numbers into `equilibrium_from_pCO2()` — holding alkalinity fixed at 2300 μmol/kg, 15 °C, S=35 — gives:

| | CO₂ (ppm) | pH | Ω_arag | CO₃²⁻ (μmol/kg) |
|---|---|---|---|---|
| Pre-industrial | 278.0 | 8.192 | 3.30 | 215.6 |
| 2025 (observed) | 425.6 | 8.034 | 2.43 | 158.8 |
| **Change** | **+147.6** | **−0.159** | **−0.87** | **−56.8** |

Carbonate ion is down to **74% of pre-industrial**. Run `python equations/carbonate_system.py` to regenerate this table.

That the module reproduces the observed modern surface pH (~8.03) from an independent measurement of atmospheric CO₂ is an end-to-end check on K₀, K₁ and K₂ together — it is pinned by a test.

Electrochemical alkalinity enhancement uses electrical energy to shift the carbonate equilibrium:

```
CO₂ + H₂O ⇌ H₂CO₃ ⇌ H⁺ + HCO₃⁻ ⇌ 2H⁺ + CO₃²⁻
```

By removing H⁺ electrochemically (or adding OH⁻), we shift equilibrium rightward, increasing pH and carbonate availability. At 1.8 kW from a wave device, we can process meaningful volumes of seawater for localized pH buffering.

### Wave Energy Capture

Deep-water wave power transport:

```
P = (ρ × g² × Hs² × Tp) / (64π)  [W per meter of wave crest]
```

The denominator is 64π, not the more commonly quoted 32π. The 32π form applies to *regular* waves of height H, where energy density is ρgH²/8. A real sea state is irregular, and for a Rayleigh distribution of wave heights the equivalent energy density is ρgHs²/16 — half as much. Using 32π with a significant wave height overestimates the resource by exactly 2×. As a check, this reduces to the standard engineering approximation P[kW/m] ≈ 0.49 × Hs² × Te.

For Hs=1m, Tp=8s: ~3.9 kW/m. A 10m capture width device at 15% efficiency yields ~5.9 kW. This is well within community-build capability — oscillating water column (OWC) devices have been built at this scale since the 1990s.

### Salinity Gradient Energy

The Nernst equation gives the open-circuit voltage across a salinity gradient:

```
ΔV = (RT / nF) × ln(C₁ / C₂)
```

For seawater (35 psu) vs. river water (5 psu): ~48 mV per ion pair. Reverse electrodialysis (RED) stacks multiple membrane pairs to reach useful voltages. At community scale this yields milliwatts — not enough to power restoration, but useful for low-power sensors.

### What Doesn't Work (and Why)

**Ocean current EM induction**: Faraday's law gives V = B × v × L × sin(θ). With Earth's field B ≈ 50 μT, current v ≈ 0.5 m/s, electrode separation L = 1 m: V ≈ 25 μV. The internal resistance of seawater between electrodes limits current to microamps. Total power: nanowatts to microwatts.

**Solar wind / CME harvesting at the surface**: CME energy (~10³² J) is absorbed by the magnetosphere and ionosphere at altitudes >80 km. The surface effect is geomagnetic field variation of ~100 nT during storms — four orders of magnitude smaller than Earth's ambient field. No meaningful energy couples to small coastal devices.

**Multiplicative energy coupling**: Multiplying energy sources together (E₁ × E₂ × E₃) is dimensionally incorrect (Energy³ ≠ Energy) and physically meaningless. Energy sources add; they don't multiply. Coupling between systems can improve efficiency of individual sources, but total power is bounded by the sum of inputs times conversion efficiency.

## Repository Structure

```
electromagnetic-ocean-restoration/
├── equations/
│   ├── ocean_restoration_simulation.py  # Integrated site assessment tool
│   ├── iron_chemistry.py               # Fe²⁺/Fe³⁺ kinetics, speciation, precipitation
│   ├── carbonate_system.py             # Ocean CO₂ equilibrium, pH buffering capacity
│   └── wave_energy.py                  # Wave power, device sizing, capture efficiency
├── community-tools/
│   └── deployment_calculator.py        # CLI tool for site assessment
├── tests/                              # Test suite (see Testing below)
│   ├── test_wave_energy.py
│   ├── test_iron_chemistry.py
│   ├── test_carbonate_system.py
│   └── test_integration.py
├── .github/workflows/tests.yml         # CI: pytest on Python 3.8–3.13
├── legacy/                             # Superseded claims + falsification log
│   ├── README.md                       # What was ruled out, and by what argument
│   ├── 2025-11-30-README.md
│   └── 2025-11-30-Potential-deployments.md
├── Potential-deployments.md            # Deployment strategies with real numbers
├── CLAUDE.md                           # AI assistant guide
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

### On the `legacy/` folder

Claims this project has abandoned are kept in `legacy/`, in the form they were
originally made, with a log of what falsified each one. A discarded hypothesis
is still a result: if you arrive with an idea this repo already tried — CME
harvesting, current-induction power, multiplicative energy coupling — you can
find out in one read why it does not work, rather than re-deriving it.

`legacy/README.md` also carries the **open questions**: places where the
current code is untested or under-justified, each with a suggested test. That
list is the next round of work.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run site assessment with default conditions
python equations/ocean_restoration_simulation.py

# Use the deployment calculator for your location
python community-tools/deployment_calculator.py \
  --wave-height 1.0 \
  --wave-period 8.0 \
  --salinity-high 35.0 \
  --salinity-low 5.0 \
  --temperature 15.0

# Explore individual modules
python equations/wave_energy.py
python equations/iron_chemistry.py
python equations/carbonate_system.py
```

## Testing

The core modules need only the standard library. Running the tests needs `pytest`:

```bash
pip install pytest
pytest                    # run everything
pytest -v                 # one line per test
pytest tests/test_iron_chemistry.py    # a single module
```

The suite checks physics, not just that the code runs. Where a published value
exists, the test asserts against the paper the module cites:

| Check | Source |
|---|---|
| pK₁ = 5.8472, pK₂ = 8.9660 at 25 °C, S=35 | Lueker et al. (2000) |
| K_sp aragonite = 6.48×10⁻⁷, calcite = 4.27×10⁻⁷ | Mucci (1983) |
| Fe²⁺ half-life of minutes at pH 8, 25 °C | Millero et al. (1987) |
| Fe(III) solubility 0.07–0.6 nM at pH 8 | Liu & Millero (2002) |
| [Ca²⁺] = 0.01028 mol/kg at S=35 | Riley & Tongudai (1967) |
| K₀ = 2.839×10⁻² mol/kg/atm at 25 °C, S=35 | Weiss (1974) |
| 425.6 ppm reproduces surface pH ~8.03 | State of the Climate in 2025 |

The rest cover scaling laws (wave power as Hs², oxidation rate as [OH⁻]²),
conservation (carbonate species summing to DIC, charge matching Faraday's law),
monotonicity, edge cases, and end-to-end consistency of the integrated
assessment and the CLI.

### Corrections these tests caught

Writing the suite surfaced four errors, all now fixed:

1. **Wave power was 2× too high.** `deep_water_wave_power()` divided by 32π
   (the regular-wave form) while being fed a significant wave height. Now 64π,
   pinned by three tests — against the docstring derivation, against the
   `0.49 Hs² Te` engineering approximation, and one asserting the result is
   exactly half the regular-wave value so the two forms cannot be re-conflated.
2. **Fe²⁺ half-life** was quoted as ~4 min at pH 8.1, 15 °C; the model gives
   ~26 min. The code was right — the temperature dependence enters twice, once
   through k_ox and again through Kw in the [OH⁻]² term.
3. **k_ox** was quoted as 8×10¹³ M⁻³s⁻¹; Millero's own expression gives
   8.2×10¹² M⁻³s⁻¹ at 25 °C, S=35.
4. **A 1000× unit error** in the iron release-rate calculation in
   `Potential-deployments.md` (0.054 g/hr where the arithmetic gives 54 g/hr),
   which had made passive iron release look ~280× easier than it is.

## Community Deployment Tiers

| Tier | Budget | What You Can Do |
|------|--------|-----------------|
| **Monitor** | $5–50 | pH/temperature logging with smartphone sensors. Contribute baseline data. |
| **Sensor** | $50–500 | Arduino/RPi water quality monitoring. Salinity gradient voltage measurement. Calibrated pH tracking. |
| **Restore** | $500–5,000 | Small oscillating water column (OWC) wave device. Passive iron release system. Local pH monitoring network. |
| **Research** | $5,000+ | Engineered wave energy converter. Controlled iron dosing. Electrochemical pH cell. Real-time data telemetry. |

## Key Equations Reference

### Wave Power (the actual energy source)

```
P_wave = (ρ g² Hs² Tp) / (64π)         # W/m of wave crest (irregular sea)
P_captured = P_wave × L_capture × η      # Total captured power (W)
```

### Iron Chemistry (the restoration mechanism)

```
Fe²⁺ oxidation: d[Fe²⁺]/dt = -k_ox × [Fe²⁺] × [O₂] × [OH⁻]²
  where k_ox ≈ 8.2 × 10¹² M⁻³s⁻¹ at 25°C, S=35 (Millero et al., 1987)
  (equivalently ~4.9 × 10¹⁴ M⁻³min⁻¹, the units Millero reports)

Half-life at pH 8.1, 15°C, O₂=250 μmol/kg: ~26 minutes
Half-life at pH 8.0, 25°C:                 ~5 minutes
  → strongly temperature-dependent, through both k_ox and Kw
  → sustained slow release beats single large dose
```

### Carbonate Equilibrium (the pH target)

```
CO₂(aq) + H₂O ⇌ H⁺ + HCO₃⁻     K₁ ≈ 1.4 × 10⁻⁶ (25°C, S=35)
HCO₃⁻ ⇌ H⁺ + CO₃²⁻              K₂ ≈ 1.1 × 10⁻⁹ (25°C, S=35)

Buffer capacity: β = 2.3 × DIC × (K₁[H⁺] + 4K₁K₂) / ([H⁺]² + K₁[H⁺] + K₁K₂)²
```

### Salinity Gradient (sensor power only)

```
ΔV = (RT/nF) × ln(C_high/C_low)        # ~48 mV for seawater/river
P_RED = n_pairs × ΔV × I × η           # Milliwatts at community scale
```

## Environmental Safety

**Iron release into marine environments requires regulatory approval.** This project provides modeling tools for planning and assessment. Before any field deployment:

1. Check local, national, and international regulations (London Protocol, CBD, national marine protection laws)
2. Conduct environmental impact assessment
3. Start with enclosed/contained experiments
4. Monitor for unintended effects (harmful algal blooms, oxygen depletion, ecosystem shifts)
5. Share data openly for community review

Iron fertilization is regulated under the London Protocol (2013 amendment). Open-ocean iron addition requires assessment and approval. Coastal/nearshore work may fall under different jurisdictions.

## Contributing

We welcome contributions in:

- **Physics/chemistry**: Improve equations, add models, validate against published data
- **Engineering**: Wave device designs, iron release mechanisms, sensor systems
- **Field data**: Baseline measurements, deployment results, ecosystem monitoring
- **Software**: Visualization, data pipelines, improved CLI tools
- **Review**: Identify errors, unrealistic claims, or safety concerns

### Principles

- **Honesty over hype** — show real numbers, acknowledge limitations
- **Safety first** — ecosystem health above technical performance
- **Community accessible** — code should be understandable by non-specialists
- **Open data** — share results freely

## References

- Millero, F.J. et al. (1987). Oxidation kinetics of Fe(II) in seawater. *Geochimica et Cosmochimica Acta*, 51(4), 793-801.
- Zeebe, R.E. & Wolf-Gladrow, D. (2001). *CO₂ in Seawater: Equilibrium, Kinetics, Isotopes*. Elsevier.
- Boyd, P.W. et al. (2007). Mesoscale iron enrichment experiments 1993–2005. *Science*, 315(5812), 612-617.
- Falnes, J. (2007). A review of wave-energy extraction. *Marine Structures*, 20(4), 185-201.
- Rau, G.H. et al. (2013). Electrochemical CO₂ capture and storage with hydrogen generation. *PNAS*, 110(32), 12885.
- Weiss, R.F. (1974). Carbon dioxide in water and seawater: the solubility of a non-ideal gas. *Marine Chemistry*, 2(3), 203-215.
- Blunden, J. & Boyer, T., Eds. (2026). [State of the Climate in 2025](https://journals.ametsoc.org/view/journals/bams/107/8/2026BAMSStateoftheClimate.1.xml). *Bulletin of the American Meteorological Society*, 107(8), Si–S484.

## License

MIT License — Use freely for ocean restoration research and deployment.
