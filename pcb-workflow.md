# PCB Design & Automation Workflow

## Mandatory Design Rules & Verification Stages

### Stage 1: Schematic Capture & Functional Verification
1. **Schematic Design:** Place and interconnect components with standard reference designators and clean net naming.
2. **Mandatory SPICE Simulation Check:**
   > **Rule:** Run a SPICE simulation on any filter, oscillator, or gain-stage subcircuit before layout begins.
   - Use `kicad-spice` (SPICEBridge / ngspice) to run AC sweep, transient analysis, and DC operating point simulation.
   - Verify frequency response (cutoff frequency, passband ripple, roll-off), oscillation stability/frequency, and gain/linearity before freezing component values and footprint selection.
3. **Electrical Rules Check (ERC):** Run ERC to verify no unconnected pins or power/ground conflicts exist.

---

### Stage 2: Net Classes & Design Rules Definition
1. **Net Class Definition:** Define trace width and clearance rules based on signal class:
   - Power Rails & Ground
   - High-Speed / Controlled Impedance (e.g. 50 $\Omega$ single-ended, 90/100 $\Omega$ differential)
   - Standard Signal
2. **Calculations:** Use Saturn PCB Toolkit or impedance models for precise trace width, dielectric spacing, and via sizing calculations.

---

### Stage 3: PCB Layout & Placement
1. **Synchronize Schematic to Board:** Import nets and footprints from schematic.
2. **Floorplanning & Placement:** Group and orient components logically by functional blocks (power stage, analog/filter stage, digital stage, I/O connectors).
3. **Courtyard & Clearance Verification:** Ensure zero courtyard overlaps and adequate spacing for soldering and thermals.

---

### Stage 4: Routing
1. **Critical Analog & RF Traces:** Route SPICE-validated filter, gain-stage, and sensitive analog paths with proper ground referencing.
2. **Differential Pairs & High Speed:** Route with constant impedance and length/phase matching.
3. **Power & Ground:** Route wide traces or copper pours; apply ground stitching vias where appropriate.
4. **General Signals:** Complete routing manually or with autorouting tools (e.g. Freerouting).

---

### Stage 5: Design Rule Check (DRC) & Output Generation
1. **Design Rule Check (DRC):** Run DRC and resolve all clearance, track width, and unrouted net violations.
2. **Inspection:** Generate 2D/3D views for mechanical fit check.
3. **Manufacturing Outputs:** Export Gerbers, drill files, IPC-D-356, BOM, and pick-and-place (POS) files.
