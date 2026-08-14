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
├── tests/                              # pytest suite (132 tests)
│   ├── conftest.py                     # Puts equations/ on sys.path
│   ├── test_wave_energy.py
│   ├── test_iron_chemistry.py
│   ├── test_carbonate_system.py
│   └── test_integration.py             # End-to-end + CLI subprocess tests
├── .github/workflows/tests.yml         # CI: pytest 3.8–3.13 + stdlib-only check
├── pytest.ini                          # Test configuration
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

## Testing

```bash
pip install pytest    # the only dev dependency
pytest                # 132 tests, ~1 second
```

Tests live in `tests/` and assert real physics, not just that the code runs.
Equilibrium constants are pinned to the published values in the papers each
module cites (Lueker 2000, Mucci 1983, Millero 1987, Liu & Millero 2002), so a
regression in a fitted coefficient fails loudly instead of quietly shifting
every downstream number.

`tests/conftest.py` puts `equations/` and `community-tools/` on `sys.path`,
because the modules import each other by bare name.

When adding a model, add tests in the same style: a known-value check against
the literature where one exists, plus scaling, conservation, and edge cases.

### Open issue pinned by a test

`deep_water_wave_power()` divides by 32π, but its own docstring derivation
(`E = ρgHs²/16`, `cg = gTp/4π`) and the standard irregular-sea result both give
64π — the 32π form is for regular waves of height H, not a sea state
characterised by Hs. The function therefore overestimates wave power by 2×.
`test_wave_power_matches_documented_derivation` is marked `xfail` with
`xfail_strict = true`; fixing the denominator makes it XPASS, which fails CI
until the marker is removed. Fixing it changes every wave-power figure in
`README.md` and `Potential-deployments.md`, which also disagree with each other
today (the README quotes 4.9 kW/m for Hs=1 m, Tp=8 s where the code returns
7.85 and the corrected formula gives 3.92).

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
- **Tests**: pytest (`tests/`), the only dev dependency
- **CI**: GitHub Actions — pytest on Python 3.8–3.13, plus a job that installs
  nothing and runs every entry point to enforce the stdlib-only guarantee
- **No build system or packaging** (modules are run directly, not installed)

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
