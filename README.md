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
| **Wave energy** (1m wave, 8s period, 10m capture) | ~11 kW available, ~1.8 kW captured | **Yes** | Dominant source. Well-proven technology. |
| **Salinity gradient** (river mouth, small RED cell) | ~50 mV, ~0.07 mW | Marginal | Needs large membrane area to be useful. Research-scale. |
| **Ocean current EM induction** | ~25 μV, ~0.003 μW | **No** | Earth's field is ~50 μT. Yields microwatts. Not practical. |
| **Piezoelectric** | ~0.05 μV per element | **No** | Supplementary sensor power only. |
| **Solar/CME coupling** | N/A at surface | **No** | Affects ionosphere, not coastal devices. |

**Bottom line**: Wave energy is the only viable power source at community scale. The other mechanisms are real physics but produce negligible power in small installations. This project focuses on wave-powered iron delivery and electrochemical restoration.

## Scientific Foundation

### Iron Fertilization

Iron limits phytoplankton growth across ~30% of the ocean surface (the "High-Nutrient Low-Chlorophyll" regions). Adding small amounts of bioavailable iron (0.1–1.0 μg/L as dissolved Fe²⁺) stimulates phytoplankton blooms that:

- Fix CO₂ through photosynthesis
- Support marine food webs (phytoplankton → zooplankton → fish)
- Produce dimethyl sulfide (DMS) that seeds cloud formation

This has been demonstrated in 13+ open-ocean experiments (SOIREE, SOFeX, LOHAFEX, SERIES, etc.). The science is real; the debate is about permanence of carbon sequestration and unintended ecological effects.

**Key constraint**: Fe²⁺ oxidizes to Fe³⁺ in oxygenated seawater with a half-life of minutes to hours (pH and temperature dependent). Fe³⁺ rapidly forms insoluble oxyhydroxides and precipitates. Sustained delivery matters more than total mass.

### Ocean Alkalinity Enhancement

Ocean acidification (current pH ~8.05, pre-industrial ~8.18) reduces carbonate ion availability, threatening calcifying organisms. Electrochemical alkalinity enhancement uses electrical energy to shift the carbonate equilibrium:

```
CO₂ + H₂O ⇌ H₂CO₃ ⇌ H⁺ + HCO₃⁻ ⇌ 2H⁺ + CO₃²⁻
```

By removing H⁺ electrochemically (or adding OH⁻), we shift equilibrium rightward, increasing pH and carbonate availability. At 1.8 kW from a wave device, we can process meaningful volumes of seawater for localized pH buffering.

### Wave Energy Capture

Deep-water wave power transport:

```
P = (ρ × g² × H² × T) / (32π)  [W per meter of wave crest]
```

For H=1m, T=8s: ~4.9 kW/m. A 10m capture width device at 15% efficiency yields ~7.4 kW. This is well within community-build capability — oscillating water column (OWC) devices have been built at this scale since the 1990s.

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
├── Potential-deployments.md            # Deployment strategies with real numbers
├── CLAUDE.md                           # AI assistant guide
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

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
P_wave = (ρ g² H² T) / (32π)           # W/m of wave crest
P_captured = P_wave × L_capture × η      # Total captured power (W)
```

### Iron Chemistry (the restoration mechanism)

```
Fe²⁺ oxidation: d[Fe²⁺]/dt = -k_ox × [Fe²⁺] × [O₂] × [OH⁻]²
  where k_ox ≈ 8 × 10¹³ M⁻³s⁻¹ at 25°C (Millero et al., 1987)

Half-life at pH 8.1, 15°C: ~4 minutes
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

## License

MIT License — Use freely for ocean restoration research and deployment.
