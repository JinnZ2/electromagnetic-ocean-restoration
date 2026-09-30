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
├── legacy/                             # Superseded claims + falsification log
│   ├── README.md                       # What was ruled out, by what argument
│   ├── 2025-11-30-README.md            # Original docs, verbatim
│   └── 2025-11-30-Potential-deployments.md
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

### Errors the suite caught (all fixed)

Keep these in mind when touching the docs — the numbers in `README.md` and
`Potential-deployments.md` are now derived from the code, not hand-written.

1. **Wave power was 2× too high.** `deep_water_wave_power()` used 32π (the
   regular-wave form) with a significant wave height. Now 64π. Three tests
   pin it, including one asserting the result is exactly half the 32π value,
   so the two forms cannot be silently re-conflated.
2. **Fe²⁺ half-life** in the docs (~4 min at pH 8.1, 15 °C) contradicted the
   model (~26 min). The code was correct: temperature enters both through
   k_ox and through Kw in the [OH⁻]² term, and the module deliberately uses
   pure-water (NBS-scale) Kw to match Millero's calibration.
3. **k_ox** was documented as 8×10¹³ M⁻³s⁻¹; the cited expression gives
   8.2×10¹² M⁻³s⁻¹ at 25 °C, S=35.
4. **A 1000× unit error** in the iron release calculation in
   `Potential-deployments.md`, which understated the passive-dissolution
   requirement by ~280×.

The pattern: the *code* was right in every case except the wave-power
denominator, and the prose had drifted. Prefer regenerating doc tables from
the modules over editing them by hand.

## Legacy / falsification log

`legacy/` holds claims the project has abandoned, in the form they were
originally made, plus a log of what falsified each one. **When a claim turns
out to be wrong, move it there rather than deleting it** — a ruled-out
hypothesis is a result, and it stops the same idea being re-proposed.

`legacy/README.md` also tracks the **open questions**: ten places where the
current code is untested or under-justified (a clamped Revelle factor, a
hand-fitted Fe(III) solubility, unused function parameters, hard-coded
turbulent diffusion, omitted borate alkalinity, and so on), each with a
suggested test. Start there when
looking for what to work on next, and add a row to the round table when one is
resolved.

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
- Wave power: `P = (ρg²Hs²Tp)/(64π)` — linear wave theory, irregular sea.
  64π not 32π: the 32π form is for regular waves of height H, and using it
  with a significant wave height doubles the answer.
- Nernst equation: `ΔV = (RT/nF)ln(C₁/C₂)` — salinity gradient voltage
- Fe²⁺ oxidation: `k ≈ 8.2×10¹² M⁻³s⁻¹` at 25 °C, S=35 — Millero et al. (1987)
- Carbonate: Lueker et al. (2000) K₁/K₂, Mucci (1983) K_sp, Weiss (1974) K₀
- Atmospheric CO₂: `CO2_PPM_2025 = 425.6` — State of the Climate in 2025
  (BAMS 107(8), Aug 2026). `equilibrium_from_pCO2()` solves for the pH this
  implies, so the observation is an *input* and pH is a computed consequence.

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

<!-- clone-refspec-note v1.1 -->
## Cloning and pushing
Shallow clones are single-branch by default.
Before pushing any branch other than the default
branch, run:

    git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
    git fetch --depth 1

Or clone with: git clone --depth 1 --no-single-branch <url>
Without this, the first push of a new branch
fails the tracking-ref check even when the
commit landed.
<!-- /clone-refspec-note v1.1 -->
