# Legacy — Falsification Log

This folder keeps claims the project has **abandoned**, in the form they were
originally made.

It exists because a discarded hypothesis is still a result. Knowing that
"harvest CME energy at the sea surface" was tried and ruled out — and *by what
argument* — is worth more than a repo that silently looks as though it always
knew better. Anyone arriving with the same idea can find out in one read why it
does not work, instead of re-deriving it.

**Nothing in this folder is current guidance.** The files are superseded, and
they are kept unaltered apart from a banner at the top of each.

## Contents

| File | Original commit | Date | Superseded by |
|---|---|---|---|
| `2025-11-30-README.md` | `cb8ee00` | 2025-11-30 | `ced09ef` (2026-03-22) |
| `2025-11-30-Potential-deployments.md` | `3f6b6ca` | 2025-11-30 | `ced09ef` (2026-03-22) |

## Round 1 — 2026-03-22 (`ced09ef`)

The original documents proposed a coupled electromagnetic restoration system.
Checking the claims against dimensional analysis and order-of-magnitude
estimates removed most of the energy story and left the chemistry intact.

| Claim | Test applied | Result |
|---|---|---|
| `E_total = (E_solar_wind × E_polar_gradient × E_ocean_current × E_wave) × η` | Dimensional analysis | **Falsified.** Multiplying four energies gives Energy⁴. Energy sources add; they do not multiply. |
| Harvest solar-wind / CME energy at the sea surface | Order of magnitude | **Falsified.** CME energy is absorbed by the magnetosphere and ionosphere above ~80 km. Surface signature during a storm is ~100 nT against a ~50,000 nT ambient field. |
| Ocean-current EM induction as a power source | Faraday's law | **Falsified.** V = BvL ≈ 50 μT × 0.5 m/s × 1 m = 25 μV. Seawater's internal resistance limits this to microamps — nanowatts to microwatts. |
| One intervention influences restoration "hundreds of miles away through field propagation" | Sought a mechanism | **Falsified.** No proposed mechanism carries a meaningful signal at that range. Removed with no replacement. |
| "Nonlinear cascades" giving effects "orders of magnitude" beyond linear | Sought a mechanism | **Falsified.** Rests on the multiplicative equation above. |
| Salinity-gradient energy powers restoration | Nernst + RED stack sizing | **Downgraded, not removed.** Real physics, but ~48–71 mV and milliwatts at community scale. Retained for *sensor* power only. |
| Wave energy as a power source | Linear wave theory | **Survived.** Promoted to the primary — and only viable — energy source. |
| Iron limitation of phytoplankton; controlled Fe²⁺ release | Literature (13+ open-ocean experiments) | **Survived,** with the London Protocol constraint attached. |
| Electrochemical pH buffering | Carbonate equilibrium + Faraday's law | **Survived.** Now the main use for captured wave power. |

The surviving mechanisms became `equations/`. The ruled-out ones are recorded
in the "What Doesn't Work (and Why)" section of the root `README.md`, so the
negative results stay visible in the live docs rather than only here.

## Round 2 — 2026-08-14 (`ea52613`, `6d782ec`)

Round 1 replaced prose with code but never tested the code. Adding a test
suite that asserts published values — rather than just checking the modules
run — falsified four more claims.

| Claim | Test applied | Result |
|---|---|---|
| `P = ρg²Hs²Tp / (32π)` | Compared against the function's own docstring derivation, and against `P ≈ 0.49 Hs² Te` | **Falsified.** 32π is the *regular-wave* form. For an irregular sea characterised by Hs the energy density is halved, giving 64π. Every wave-power figure was 2× too high. |
| Fe²⁺ half-life ~4 min at pH 8.1, 15 °C | Ran the model | **Falsified — the docs, not the code.** Model gives ~26 min. Temperature enters twice: through k_ox and through Kw in the [OH⁻]² term. |
| k_ox ≈ 8×10¹³ M⁻³s⁻¹ | Evaluated Millero's own expression | **Falsified — the docs.** 8.2×10¹² at 25 °C, S=35. |
| Iron release of 0.054 g/hr sustains a 10 m × 10 m plume | Redid the unit conversion | **Falsified — the docs.** 1.5×10⁻² g/s is 54 g/hr. A 1000× error that made passive release look ~280× easier than it is. Sustaining that plume needs ~2,400 kg of filings, not ~2.5 kg. |
| A release point makes a ~60 m plume because Fe²⁺ oxidises | Ran the plume model | **Falsified — and backwards.** At 0.25 m/s, ~80% of Fe²⁺ is still un-oxidised at 100 m. Concentration falls 300× from *turbulent dilution*. The plume is dilution-limited, not chemistry-limited. |

The pattern in round 2 is the mirror of round 1: the **code was right in every
case except the wave-power denominator**, and the prose had drifted away from
it. Hence the current convention — regenerate doc tables from the modules
rather than editing them by hand.

## Search for unknowns — the next round

Open questions, roughly in descending order of how much they could move a
number. None of these is known to be wrong; they are untested or
under-justified.

1. **The Revelle factor is clamped to 8–25** (`carbonate_system.py:200`). A
   clamp is a symptom: either the analytic expression is right and the clamp
   never binds, or it is wrong and the clamp is hiding it. *Test:* compare
   against PyCO2SYS across the T/S/DIC/pH ranges the module claims to cover,
   then delete the clamp or fix the formula.
2. **Fe(III) solubility is hand-fitted to a figure**, not to Liu & Millero's
   published equation — `log_sol = −0.7 − 2.5(pH−8) + 0.015(T−25)`. *Test:*
   digitise the paper's Figure 4 or use its stated expression, and check the
   residual over pH 7–9.
3. **`fe3_solubility()` accepts a salinity argument it never uses**, and
   `fe2_oxidation_rate_constant()` accepts a pH it never uses. Either the
   parameters belong in the physics or they should leave the signature; today
   a caller can vary salinity and get an unchanged answer.
4. **The plume model hard-codes `D_turb = 0.01 m²/s` and floors the plume
   cross-section at 0.1 m².** Both are unjustified, and the floor sets the
   near-field concentration that everything downstream scales from. *Test:*
   sensitivity sweep, and check the 0.1 m² floor is never the binding
   constraint at realistic release rates.
5. **OWC efficiency is a lookup table with ad-hoc penalties.** The docstring
   mentions resonance tuning, but chamber dimensions never affect the answer —
   `chamber_length_m` is declared and never read. *Test:* an actual chamber
   resonance model, or drop the field and the resonance claim.
6. **Capacity factor uses two seasons of six months each.** Real wave climates
   are a distribution, not a step function. *Test:* recompute from a wave
   height histogram (CDIP data exists for the La Jolla site) and see how far
   off the two-season figure is.
7. **The alkalinity budget assumes 2.2 V, 70% faradaic efficiency, and one
   mole of OH⁻ per mole of alkalinity.** None is validated against Rau (2008).
   *Test:* check the cell voltage and efficiency against the reported
   electrochemical splitting numbers.
8. **The two modules use different Kw.** `iron_chemistry` uses pure-water
   (NBS-scale) Kw deliberately, to match Millero's calibration;
   `carbonate_system` uses a seawater pKw. Both may be individually correct,
   but nothing checks that the pH scales stay consistent when results are
   combined in `ocean_restoration_simulation`. *Test:* make the scale explicit
   at each interface.
9. **`S_factor` in `carbonate_system.py` is computed and discarded.**
   Harmless, but it suggests the Revelle expression was mid-edit when it
   landed — worth resolving alongside item 1.
10. **`equilibrium_from_pCO2()` omits borate alkalinity.** It uses the same
    carbonate-only TA definition as the rest of the module, but real seawater
    TA includes ~100 μmol/kg of borate. Absolute pH from an observed TA will
    therefore be slightly off; *differences* between two scenarios at the same
    TA are much more reliable, which is how the acidification comparison uses
    it. *Test:* add borate (Uppström 1974 total boron, Dickson 1990 K_B) and
    measure how far the absolute pH moves.

When one of these is resolved, add a row to the round table above. If a claim
in the live docs turns out to be wrong, move it here rather than deleting it.
