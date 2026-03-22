# CLAUDE.md

## Project Overview

**Electromagnetic Ocean Restoration** — Community-deployable systems for marine ecosystem restoration, combining wave energy capture, controlled iron release, and electrochemical pH buffering.

**Stage**: Working simulation code with physics-based models. No field deployment infrastructure yet.

## Repository Structure

```
/
├── equations/
│   ├── ocean_restoration_simulation.py  # Integrated site assessment (main entry point)
│   ├── wave_energy.py                   # Wave power and OWC device sizing
│   ├── iron_chemistry.py               # Fe²⁺/Fe³⁺ kinetics, speciation, plume modeling
│   ├── carbonate_system.py             # Ocean CO₂ equilibrium, pH buffering, alkalinity
│   └── __init__.py
├── community-tools/
│   └── deployment_calculator.py        # CLI tool for site assessment
├── README.md                           # Project documentation with honest energy budget
├── Potential-deployments.md            # Deployment strategies with real numbers
├── CLAUDE.md                           # This file
├── requirements.txt                    # Dependencies (stdlib only for core)
└── .gitignore
```

## Running the Code

```bash
# All modules use only Python standard library — no pip install needed

# Run integrated simulation (3 predefined sites)
python equations/ocean_restoration_simulation.py

# Run individual modules
python equations/wave_energy.py
python equations/iron_chemistry.py
python equations/carbonate_system.py

# CLI deployment calculator
python community-tools/deployment_calculator.py --preset la-jolla
python community-tools/deployment_calculator.py --wave-height 1.0 --wave-period 8
```

## Key Physics (What's Real, What's Not)

### Works at community scale
- **Wave energy**: 100W–10kW from oscillating water column devices
- **Electrochemical pH buffering**: Wave-powered seawater electrolysis
- **Iron fertilization**: Controlled release of bioavailable Fe²⁺

### Does NOT work at community scale
- **Ocean current EM induction**: Yields microwatts (Earth's field ~50 μT)
- **Solar/CME coupling at surface**: Absorbed at ionosphere altitude (80+ km)
- **Multiplicative energy equations**: Dimensionally incorrect (Energy × Energy ≠ Energy)
- **Salinity gradient power**: Milliwatts without industrial-scale membranes

### Core Equations
- Wave power: `P = (ρg²H²T)/(32π)` — standard linear wave theory
- Nernst equation: `ΔV = (RT/nF)ln(C₁/C₂)` — salinity gradient voltage
- Fe²⁺ oxidation: `k ≈ 8×10¹³ M⁻³s⁻¹` — Millero et al. (1987)
- Carbonate: Lueker et al. (2000) K₁/K₂, Mucci (1983) K_sp

## Technology Stack

- **Language**: Python 3.8+
- **Dependencies**: Standard library only (math, dataclasses, argparse)
- **No build system, test framework, or CI/CD yet**

## Development Conventions

- **Honesty over hype** — every claim must have units that work out and realistic parameter values
- **Cite sources** — reference published literature for rate constants and equilibrium values
- **Safety warnings** — iron release requires regulatory approval (London Protocol)
- **Community accessible** — code should be readable by non-specialists
- **Energy sources add, not multiply** — total power is sum of inputs × efficiencies

## Git

- **Main branch**: `main`
- **Feature branches**: `claude/` prefix
- **Commits**: Descriptive messages explaining what and why
