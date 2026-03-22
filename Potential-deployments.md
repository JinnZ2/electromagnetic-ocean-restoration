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
P = (ρ g² H² T) / (32π)
P = (1025 × 9.81² × 0.8² × 10) / (32π)
P ≈ 3,140 W/m of wave crest
```

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

**Problem**: Fe²⁺ oxidizes fast in oxygenated seawater.
```
Half-life at pH 8.05, 17°C: ~3.5 minutes
```

This means a single iron release point creates a plume only ~60m long before >90% has oxidized and precipitated. Strategies:

1. **Slow continuous release** from iron-bearing minerals (olivine, magnetite sand) in wave-agitated chambers — dissolution rate limits iron delivery to ecologically relevant concentrations
2. **Chelated iron** (Fe-EDTA or natural ligands like siderophores) — extends residence time to hours but adds cost
3. **Multiple release points** along current direction — each extends effective plume length

**Release rate calculation** (from `equations/iron_chemistry.py`):
```
To maintain 0.5 μg/L across a 10m × 10m cross-section at 0.3 m/s current:
Mass flux = 0.5e-9 kg/L × 1000 L/m³ × 100 m² × 0.3 m/s
         = 1.5 × 10⁻⁵ kg/s = 0.054 g/hr of dissolved Fe²⁺

Accounting for oxidation losses (only ~10% stays dissolved at 500m):
Actual release: ~0.5 g/hr of iron filings
```

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
Available power:  P_avail = (ρ g² H² T) / (32π) × W
Captured power:   P_cap = P_avail × η_owc

η_owc typical values:
  - Simple check-valve pump: 5–10%
  - Wells turbine (machined): 15–25%
  - Optimized OWC with control: 25–40%
```

| Wave Height | Period | 5m OWC (10% eff.) | 5m OWC (20% eff.) |
|---|---|---|---|
| 0.5 m | 6 s | 120 W | 240 W |
| 1.0 m | 8 s | 790 W | 1,570 W |
| 1.5 m | 10 s | 2,650 W | 5,300 W |
| 2.0 m | 12 s | 5,960 W | 11,920 W |

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

```
Iron filing dissolution rate in seawater:
  ~0.01–0.1 mg/cm²/day at pH 8, 15°C (varies with grain size)

For 1 kg of iron filings (surface area ~0.5 m²):
  Release: 0.5–5 mg/day = 0.02–0.2 mg/hr

To deliver 0.5 g/hr dissolved Fe (see La Jolla calculation):
  Need: ~2,500–25,000 kg of iron filings, OR
  Use acidified chamber (pH 5-6) to accelerate dissolution 100×, OR
  Use electrolytic dissolution powered by wave energy
```

Electrolytic dissolution is the practical path — use wave power to dissolve iron electrodes directly into seawater at controlled rates.

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
