# CLAUDE.md

## Project Overview

**Electromagnetic Ocean Restoration** — Community-deployable electromagnetic systems for marine ecosystem restoration. The project leverages natural energy patterns (solar-polar coupling, ocean currents, wave action) to address ocean acidification and marine ecosystem collapse.

**Stage**: Early concept phase — documentation and scientific framework established, no code implementation yet.

## Repository Structure

```
/
├── README.md                  # Core project documentation, scientific principles, planned architecture
├── Potential-deployments.md   # Deployment strategies, technical equations, real-world examples
└── CLAUDE.md                  # This file
```

### Planned Directory Structure (from README)

These directories are described in documentation but not yet created:

- `equations/` — Mathematical models (solar-polar coupling, wave dynamics, iron bioavailability)
- `sensor-calibration/` — Calibration protocols for community-built sensors
- `iron-pump-designs/` — Open-source electromagnetic iron pump designs
- `data-sharing/` — Community data collection and sharing protocols
- `case-studies/` — Real-world deployment documentation
- `community-tools/` — Deployment calculators and network tools

### Planned Python Modules

- `solar-polar-coupling.py` — Solar-polar electromagnetic coupling models
- `iron-wave-pump-dynamics.py` — Iron wave pump dynamics
- `ecosystem-restoration-models.py` — Ecosystem restoration modeling
- `coupling-optimization.py` — Energy coupling optimization
- `noise-characterization-tools.py` — Environmental noise characterization
- `deployment-calculator.py` — Community deployment planning
- `community-network-protocols.py` — Network coordination protocols

## Technology Stack

- **Primary language**: Python (planned)
- **No build system, package manager, or dependency manifest yet**
- **No test framework configured**
- **No CI/CD pipeline**
- **No linting/formatting tools configured**

## Development Workflow

### Git

- **Main branch**: `main` (remote) / `master` (local)
- **Branching**: Feature branches prefixed with `claude/`
- **Commits**: Descriptive messages; two commits exist so far

### When Code Implementation Begins

The following should be established:

1. `requirements.txt` or `pyproject.toml` for Python dependencies
2. A test framework (e.g., `pytest`)
3. Linting/formatting (e.g., `ruff`, `black`)
4. `.gitignore` for Python artifacts (`__pycache__/`, `*.pyc`, `.venv/`, etc.)
5. CI/CD via GitHub Actions

## Key Concepts & Conventions

### Scientific Principles

- **Solar-Polar Electromagnetic Coupling**: Uses solar maximum cycles and polar magnetic field shifts
- **Iron-Based Ecosystem Restoration**: Electromagnetic delivery of bioavailable iron to marine ecosystems
- **Energy-Based Problem Solving**: Optimization through natural energy patterns, not brute force
- **Cascading Restoration**: Small coordinated interventions triggering large-scale ecosystem recovery

### Community Resource Tiers

| Tier | Budget | Description |
|------|--------|-------------|
| Basic | $5–50 | Smartphone-based sensors, simple measurements |
| Intermediate | $50–500 | Arduino/Raspberry Pi systems, calibrated sensors |
| Advanced | $500+ | Research-grade equipment, real-time monitoring |

### Contributing Principles

1. **Energy-based thinking** over linear constraints
2. **Community accessibility** — solutions must work at any resource level
3. **Environmental ethics** — ecosystem health above technical performance
4. **Indigenous knowledge integration** — traditional knowledge with consent
5. **Open collaboration** — share knowledge freely

## Notes for AI Assistants

- This repo is documentation-only right now. Do not assume code infrastructure exists.
- When adding code, follow the planned module structure from the README.
- Use Python with clear, well-documented scientific code.
- Prioritize community accessibility — code should be understandable by non-experts.
- Equations referenced in documentation should be implemented faithfully.
- Environmental safety is paramount; any modeling code should include appropriate warnings and validation.
