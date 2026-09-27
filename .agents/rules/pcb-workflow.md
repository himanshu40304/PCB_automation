# PCB Workflow Rules

## Mandatory Pre-Layout SPICE Verification Rule
- **Rule:** Run a SPICE simulation on any filter, oscillator, or gain-stage subcircuit before layout begins.
- **Tools:** Use `kicad-spice` tools (SPICEBridge / ngspice) to run AC analysis, transient analysis, and DC operating points on analog subcircuits.
- **Scope:** Any filter (low-pass, high-pass, band-pass, notch), oscillator/crystal circuit, amplifier/op-amp gain stage, or active analog processing block.
- **Action:** Before transitioning from schematic capture to PCB layout/footprint assignment, automatically verify simulation results (bandwidth, cutoff frequency, stability, gain, ripple) against target specifications.

## Mandatory Post-Layout RF & Antenna Verification Gate
- **Rule:** For any RF/antenna project, run an OpenEMS simulation on the completed RF signal path via the `openems-sim` server before final sign-off.
- **Tools:** Use `openems-sim` (antenna-cad / OpenEMS FDTD solver) to run 3D full-wave electromagnetic simulation.
- **Metrics to Report:** Report $S_{11}$ (return loss / resonance), $S_{21}$ (insertion loss / isolation), and radiation pattern against the target specification.
- **Strict Constraint:** Do **NOT** treat DRC-clean as sufficient for RF sign-off. An RF board is only approved when full-wave EM metrics satisfy the target frequency and return loss criteria.
