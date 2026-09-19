# PCB Workflow Rules

## Mandatory Pre-Layout SPICE Verification Rule
- **Rule:** Run a SPICE simulation on any filter, oscillator, or gain-stage subcircuit before layout begins.
- **Tools:** Use `kicad-spice` tools (SPICEBridge / ngspice) to run AC analysis, transient analysis, and DC operating points on analog subcircuits.
- **Scope:** Any filter (low-pass, high-pass, band-pass, notch), oscillator/crystal circuit, amplifier/op-amp gain stage, or active analog processing block.
- **Action:** Before transitioning from schematic capture to PCB layout/footprint assignment, automatically verify simulation results (bandwidth, cutoff frequency, stability, gain, ripple) against target specifications.
