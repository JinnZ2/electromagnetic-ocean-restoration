# Deployment Strategies

Real-world deployment planning with actual numbers, honest energy budgets, and regulatory context.

## La Jolla Marine Sanctuary — Pilot Site Assessment

### Why La Jolla

- Scripps Institution of Oceanography nearby for validation
- Marine Protected Area with well-documented baseline ecology
- Kelp forests, rocky reef, sandy bottom — diverse habitats for monitoring
- California Current provides consistent wave energy and upwelling
- Iron-limited phytoplankton communities in offshore waters

### Site Conditions (measured values)

| Parameter | Value | Source |
|---|---|---|
| Significant wave height (annual mean) | 0.8–1.2 m | CDIP Station 073 |
| Dominant wave period | 8–14 s | CDIP Station 073 |
| Sea surface temperature | 14–21°C (seasonal) | Scripps Pier records |
| Surface pH | 7.95–8.15 | Scripps CO₂ monitoring |
| Salinity | 33.2–33.8 psu | CalCOFI |
| Current velocity (nearshore) | 0.1–0.4 m/s | HF radar, Scripps |
| Dissolved iron (offshore) | 0.05–0.2 nM | CalCOFI |
| Magnetic field | ~48 μT | IGRF-13 |

### Energy Budget for La Jolla

**Wave energy available** (using measured conditions):
```
P = (ρ g² Hs² Tp) / (64π)
P = (1025 × 9.81² × 0.8² × 10) / (64π)
P ≈ 3,140 W/m of wave crest
```

(64π, not 32π — the 32π form is for regular waves of height H. For a sea
state characterised by significant height Hs the energy density is halved.)

A 5m-wide oscillating water column (OWC) at 12% efficiency:
```
P_captured = 3,140 × 5 × 0.12 ≈ 1,880 W
```

**What 1.9 kW powers**:
- Electrochemical pH cell processing ~50 L/min of seawater
- Controlled iron release pump and sensors
- Data logging and telemetry (cellular/LoRa)
- LED marker lights for navigation safety

**What it does NOT power** (correcting earlier claims):
- It does not harvest kilowatts from CME events (those affect the ionosphere at 80+ km altitude)
- It does not multiply energy through "electromagnetic coupling cascades"
- Salinity gradient contributes <0.01 mW at this site (no major river mouth)
- Ocean current EM induction: ~14 μV across 2m electrodes — unmeasurable noise floor

### Iron Release Strategy

Target: maintain 0.1–1.0 μg/L dissolved Fe in a ~500m downstream plume.

**Problem**: Fe²⁺ oxidizes in oxygenated seawater, and the plume dilutes.
```
Half-life at pH 8.05, 17°C, S=33.5: ~21 minutes
```

Oxidation is *not* the binding constraint over the first few hundred metres.
At a 0.25 m/s current, ~80% of the released Fe²⁺ is still un-oxidized 100 m
downstream, and it takes roughly 1 km before 90% has been lost to oxidation.

Dilution is what actually limits the plume. Running
`equations/iron_chemistry.py` for these conditions, a 300 μg/hr release falls
from 60 nM at the outlet to 0.19 nM at 100 m — a 300-fold drop, almost all of
it turbulent spreading rather than chemistry, and already well under the
0.1 μg/L (1.8 nM) target. Reaching that target at 100 m needs a release rate
of several mg/hr, not hundreds of μg/hr.

Both facts point the same way, so the strategies below still hold — but the
reason is dilution first, oxidation second:

1. **Slow continuous release** from iron-bearing minerals (olivine, magnetite sand) in wave-agitated chambers — dissolution rate limits iron delivery to ecologically relevant concentrations
2. **Chelated iron** (Fe-EDTA or natural ligands like siderophores) — extends residence time to hours but adds cost
3. **Multiple release points** along current direction — each extends effective plume length

**Release rate calculation** (from `equations/iron_chemistry.py`):
```
To maintain 0.5 μg/L across a 10m × 10m cross-section at 0.3 m/s current:
Volume flux = 100 m² × 0.3 m/s = 30 m³/s
Mass flux   = 0.5 μg/L × 1000 L/m³ × 30 m³/s
            = 1.5 × 10⁻² g/s = 54 g/hr of dissolved Fe²⁺

Accounting for oxidation en route (~39% still dissolved at 500 m):
Actual release: ~140 g/hr of dissolved Fe²⁺
```

This is far larger than earlier drafts of this document claimed (they carried
a 1000× unit-conversion error, giving 0.054 g/hr). Sustaining a 10m × 10m
plume at ecologically relevant concentrations is a **kilogram-per-day**
problem, not a gram-per-day one, and that reframes the release hardware below.

### Target Species and Ecosystem Effects

| Species/Habitat | Iron Effect | pH Effect | Evidence Level |
|---|---|---|---|
| Giant kelp (*Macrocystis*) | Iron not limiting nearshore | pH buffering may help spore survival | Low — kelp are nitrate-limited here |
| Phytoplankton (offshore) | Growth stimulation in HNLC conditions | Marginal effect at this scale | High (Boyd et al., 2007) |
| Calcifying organisms | Indirect via food web | Direct benefit from higher Ω_aragonite | Moderate |
| Sea urchins / abalone | Indirect | Improved shell formation | Moderate (Gruber et al., 2012) |

**Honest assessment**: La Jolla nearshore waters are NOT iron-limited — the California Current upwelling provides iron from deep water. Iron fertilization makes more sense at the offshore HNLC boundary (~200 km west) or in truly iron-limited regions. La Jolla is better suited as a **pH buffering + monitoring** pilot site.

## River Mouth Deployment (Generic Template)

River mouths are the strongest sites for this approach because they provide:
- Salinity gradients (the only place salinity energy is non-trivial)
- Natural iron transport from terrestrial runoff
- High biological productivity (estuarine systems)
- Wave energy from coastal exposure

### Energy Sources at a River Mouth

**Wave energy** (same calculation, site-specific H and T):
```
Typical: 2–15 kW captured depending on wave climate and device size
```

**Salinity gradient** (this is where RED actually works):
```
ΔV = (RT/nF) × ln(35/2) = (8.314 × 288) / (1 × 96485) × ln(17.5)
ΔV = 0.0248 × 2.862 = 71 mV per ion pair

With a 100-pair RED stack, 0.1 m² membranes, 1 L/min flow:
P_RED ≈ 100 × 0.071 × 0.01 × 0.40 = 28 mW
```

Still milliwatts. RED at community scale powers sensors, not restoration equipment. Industrial RED (Statkraft, REDstack) uses thousands of square meters of membrane to reach kilowatts.

**Iron availability**: River water carries 1–100 μg/L dissolved iron plus particulate iron. The challenge at river mouths is iron *excess* causing harmful algal blooms, not iron limitation. Iron release at river mouths is counterproductive.

### River Mouth Strategy

Focus on **pH buffering** using wave-powered electrochemistry, not iron release:
1. Capture wave energy via OWC or point absorber
2. Drive electrochemical cell splitting seawater to produce alkalinity
3. Enhance pH in estuary mixing zone where acidification stress is highest
4. Monitor with salinity-gradient-powered sensor array (milliwatt load — good match)

## Device Sizing Guide

### Oscillating Water Column (OWC)

The simplest community-buildable wave energy converter.

```
Chamber width: W (m) — determines power capture
Chamber depth: must extend below wave trough
Air column: drives a Wells turbine or simple check-valve pump
```

**Sizing from wave conditions**:
```
Available power:  P_avail = (ρ g² Hs² Tp) / (64π) × W
Captured power:   P_cap = P_avail × η_owc

η_owc typical values:
  - Simple check-valve pump: 5–10%
  - Wells turbine (machined): 15–25%
  - Optimized OWC with control: 25–40%
```

| Wave Height | Period | 5m OWC (10% eff.) | 5m OWC (20% eff.) |
|---|---|---|---|
| 0.5 m | 6 s | 370 W | 740 W |
| 1.0 m | 8 s | 1,960 W | 3,930 W |
| 1.5 m | 10 s | 5,520 W | 11,040 W |
| 2.0 m | 12 s | 11,780 W | 23,550 W |

Generated by `python equations/wave_energy.py` — regenerate this table rather
than hand-editing it. The upper rows describe storm conditions a small
community device would be shut down or damaged in, not a design point.

### Electrochemical pH Cell

Power requirement for meaningful local pH change:

```
Seawater buffer capacity (Revelle factor ~10):
  To shift pH by 0.1 in 1 m³ of seawater requires ~0.2 mol OH⁻
  Electrochemical production: 96,485 C/mol ÷ efficiency
  At 70% Faradaic efficiency: ~27,600 C = 460 W for 1 minute

Continuous processing of 50 L/min (small pump):
  Requires ~380 W sustained
```

This matches well with a community-scale OWC in moderate wave conditions.

### Iron Release Chamber

Passive dissolution from iron minerals in wave-agitated chambers:

Rates below are from `iron_dissolution_rate()` in `equations/iron_chemistry.py`,
which uses a metallic-iron rate of 1×10⁻¹⁰ mol/cm²/s with Arrhenius
temperature and pH corrections.

```
Iron filings, 1 kg (surface area ~0.5 m² = 5,000 cm²), pH 8.05, 17°C:
  Release: ~58 mg/hr of dissolved Fe

To deliver 140 g/hr dissolved Fe (see La Jolla calculation):
  Need: ~2,400 kg of filings (~1,200 m² of exposed surface), OR
  Acidified chamber at pH 5.5 accelerates dissolution ~18×
    → ~140 kg of filings, but needs continuous acid supply, OR
  Electrolytic dissolution powered by wave energy
```

Two and a half tonnes of iron filings is not a community-scale passive
chamber. Electrolytic dissolution is the practical path — use wave power to
dissolve iron electrodes directly into seawater at controlled rates, which is
also the only one of the three that gives real-time control over dose.

**Or target a smaller plume.** The 10m × 10m cross-section above is what drives
the mass requirement. A 2m × 2m plume needs 25× less iron (~5.6 g/hr), which
~100 kg of filings can sustain passively. Contained or semi-enclosed sites
(tide pools, enclosed bays) are where passive release actually works.

## Regulatory Framework

### Iron Fertilization

- **London Protocol** (2013 amendment): Regulates marine geoengineering including ocean iron fertilization. Legitimate scientific research may be permitted with assessment framework.
- **Convention on Biological Diversity** (2010 Decision X/33): De facto moratorium on climate-related geoengineering except small-scale scientific research.
- **National laws**: Vary by country. In the US, NOAA and EPA have jurisdiction over intentional ocean modifications.

### Wave Energy Devices

- Require permits for fixed installations in navigable waters (US Army Corps of Engineers in US)
- Marine Protected Areas have additional restrictions
- Environmental assessment typically required for any permanent coastal structure

### Community Scale

Small, temporary, research-scale deployments generally face fewer regulatory barriers than commercial-scale operations. Partner with a research institution (like Scripps at La Jolla) to operate under their research permits.

## What Actually Works at Each Budget

### $50–500: Monitoring Station

**Build**: Arduino + pH sensor + temperature probe + SD card logger + waterproof housing.

**Do**: Collect baseline pH and temperature data at your local coastal site. Log hourly for 3+ months. Share data. This is genuinely useful — long-term coastal pH records are sparse.

**Power**: 18650 lithium battery + small solar panel. No wave energy needed.

### $500–5,000: Wave-Powered Sensor + Passive Iron Test

**Build**: Small OWC chamber (concrete/steel, 1–2m wide) + check-valve air pump + iron mineral chamber + pH/DO sensor array.

**Do**: Measure whether passive iron dissolution from wave-agitated olivine sand produces measurable downstream effects. Monitor pH, dissolved oxygen, chlorophyll-a fluorescence in a contained test area (tide pool or enclosed bay).

**Power**: 100–500 W from OWC drives sensors and data logging. Excess charges battery bank.

### $5,000+: Active Restoration Pilot

**Build**: Engineered OWC (3–5m wide) + Wells turbine + electrochemical pH cell + controlled iron dosing system + telemetry.

**Do**: Sustained electrochemical pH buffering in a localized area. Controlled iron delivery experiment with before/after ecosystem monitoring. Publish results.

**Power**: 1–5 kW from OWC. Sufficient for electrochemical cell + iron dosing + full sensor suite.

## Scaling Considerations

Individual community installations affect a small area (meters to hundreds of meters downstream). Scaling up requires:

1. **Multiple installations** — each covers its local area. Effects don't "multiply."
2. **Coordination for monitoring** — shared data standards so results are comparable.
3. **Realistic expectations** — community-scale restoration supplements, not replaces, emissions reduction and policy action.

Ocean pH is set by global CO₂ levels. Local electrochemical buffering helps local ecosystems survive while the root cause is addressed. This is triage, not cure.
