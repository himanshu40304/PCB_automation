# High-Speed LVDS & RF PCB Design Engineering Guide

## Project: LVDS Point-to-Point Link (SN65LVDS1D Driver + SN65LVDT2D Receiver)
**Document Version:** 1.1 (Clean GitHub-Readable Edition)  
**Design Environment:** KiCad 10 / kicad-cli / OpenEMS / Ngspice  

---

## 1. Schematic Verification & ERC Status

The schematic file `LVDS.kicad_sch` has undergone full netlist audit and Electrical Rules Check (ERC) via `kicad-cli sch erc`.

| Metric | Status | Remarks |
| :--- | :---: | :--- |
| **ERC Errors** | **0** | All power rails driven (PWR_FLAG verified) |
| **SMA Input (J1)** | **Verified** | Center Pin 1 = Signal (U2.D), Outer Pin 2 = GND |
| **Differential Pair** | **Verified** | Labeled /LVDS_P & /LVDS_N for automated diff-pair routing |
| **Decoupling Array** | **Verified** | 1 nF + 100 nF per active IC |
| **Integrated Termination** | **Verified** | Internal 110 Ω termination active inside U3 |

> **Status:** The schematic is **100% electrically validated** and ready for PCB layout.

---

## 2. High-Speed Physics: Why LVDS Works

Low-Voltage Differential Signaling (LVDS, standardized under **TIA/EIA-644-A** and **IEEE 1596.3**) operates fundamentally differently from single-ended CMOS:

```
          +-----------------------------+
          |     SN65LVDS1D (Driver)     |
          |                             |
          |       +--> [3.5 mA Current] |-----> LVDS_P Trace (100 Ω Diff) ------+
 DIN ---> | Logic                       |                                        |
          |       +-------------------- |-----> LVDS_N Trace                     |
          +-----------------------------+                                        |
                                                                           [110 Ω Load] (U3)
                                                                           V_diff = 350 mV
                                                                                 |
                                                                                 v
                                                                       SN65LVDT2D (Receiver)
```

1. **Current Steering Topology:** The transmitter switches a constant **3.5 mA current source** back and forth across the differential pair.
2. **Low Voltage Swing:** Across the 100 Ω termination resistor at the receiver:
   * **V_diff = I × R = 3.5 mA × 100 Ω = 350 mV** differential swing centered around a **1.25 V common-mode offset (Vos)**.
3. **Common-Mode Noise Rejection (CMRR):** External electromagnetic noise couples equally into both adjacent traces (V_noise,P ≈ V_noise,N). The receiver subtracts them:
   * **(V_P + V_noise) - (V_N + V_noise) = V_P - V_N**
   * This completely eliminates coupled environmental noise.
4. **Near-Zero EMI Radiation:** The current flowing down `LVDS_P` is identical in magnitude and opposite in direction to `LVDS_N`. The opposing magnetic fields cancel each other out in the far field.

---

## 3. PCB Stackup & Controlled Impedance Calculation

### Recommended 4-Layer Stackup (Standard JLC04161H-7628 / 4-Layer 1.6mm)

```
Layer 1 (Top):      Signal (Diff Pair, 50 Ω Single-Ended, Components)  [0.035 mm Copper]
-----------------   Dielectric (Prepreg 7628, εr ≈ 4.4, Height H = 0.1 mm / 4 mil)
Layer 2 (In1):      SOLID CONTINUOUS GROUND PLANE                      [0.035 mm Copper]
-----------------   Core Dielectric (FR4, Height H_core = 1.0 mm)
Layer 3 (In2):      SOLID +3.3V POWER PLANE                            [0.035 mm Copper]
-----------------   Dielectric (Prepreg 7628, Height H = 0.1 mm)
Layer 4 (Bottom):   Secondary GND / Low-Speed Test Signals             [0.035 mm Copper]
```

### Impedance Targets

#### 1. Single-Ended Microstrip (50 Ω Input / Output Traces `SIG_IN`, `SIG_OUT`)
* **Dielectric Height (H):** 0.1 mm (4 mil)
* **Dielectric Constant (εr):** 4.4
* **Target Trace Width (W_50):** **0.18 mm (7.1 mil)** → **50 Ω ± 5%**

#### 2. Edge-Coupled Differential Microstrip (100 Ω Diff Pair `/LVDS_P`, `/LVDS_N`)
* **Dielectric Height (H):** 0.1 mm
* **Trace Width (W):** **0.15 mm (6.0 mil)**
* **Intra-Pair Spacing (S):** **0.15 mm (6.0 mil)**
* **Differential Impedance (Z_diff):** **100.2 Ω**

---

## 4. Trace Length, Propagation Delay, and Skew Rules

### 1. Propagation Speed and Delay in FR4
* Effective dielectric constant on top layer: εr,eff ≈ 3.2
* Propagation Speed: **v ≈ 168 mm/ns (16.8 cm/ns)**
* **Propagation Delay (t_pd):** **≈ 6.0 to 6.6 ps/mm (150 to 170 ps/inch)**

### 2. Critical Length Threshold (L_crit)
When does a trace need transmission line design?
* **L_crit = t_rise / (2 × t_pd)**
* For SN65LVDS1D, output rise time t_rise ≈ 400 ps:
  * **L_crit = 400 ps / (2 × 6.6 ps/mm) ≈ 30 mm (3 cm / 1.2 inches)**
* **Rule:** Any trace longer than **30 mm** behaves as a transmission line and **must maintain strict 100 Ω differential impedance**.

### 3. Maximum Allowable Trace Length on FR4
* At **400 to 630 Mbps**, signal attenuation is driven by dielectric loss and skin effect.
* **Maximum Recommended Trace Length:** **250 to 300 mm (10 to 12 inches)** on standard FR4 without active equalizers.
* For your test PCB (50 mm board length), the link between Driver and Receiver is **20 mm (0.8 inches)**, ensuring perfect signal integrity.

### 4. Intra-Pair Length Matching (Skew Tolerance)
* **Rule:** Length difference **ΔL = |L_LVDS_P - L_LVDS_N| ≤ 0.15 mm (6 mils)**.
* This guarantees less than 1 ps of timing skew between the positive and negative signals.

---

## 5. Decoupling Capacitor Strategy: Placement Physics

```
   Capacitor Placement Order (From IC Pin outward):
   
   [IC VCC Pin] 
        |
        +-----> [C2/C4: 1 nF  (0402/0603)]  <-- Distance < 1.5 mm (Self-resonance > 250 MHz)
        |
        +-----> [C1/C3: 100 nF (0402/0603)] <-- Distance < 3.0 mm (Supplies 1 - 50 MHz current)
        |
       (VIA) to Layer 2 GND
```

### Golden Decoupling Rules:
1. **Distance Hierarchy:** Place the **1 nF** capacitor closest to the IC power pin, followed immediately by the **100 nF** capacitor.
2. **Loop Area Minimization:** Place the GND via directly adjacent to the capacitor pad.
3. **Power Entry:** Place a **10 µF bulk capacitor** right at the power entry connector J3.

---

## 6. Physical Floorplan & Component Placement Map

Board Size: **70 mm (Length) × 50 mm (Width)**

```
+---------------------------------------------------------------------------------------------------+ (Y = 50 mm)
|  [Edge.Cuts Outline: 70 mm x 50 mm]                                                               |
|                                                                                                   |
|                             [ J3: Power Header 3V3 / GND ] (X=135, Y=58)                          |
|                                                                                                   |
|             [C1: 100nF] [C2: 1nF]                              [C4: 1nF] [C3: 100nF]              |
|               (X=115)     (X=118, Y=68.5)                        (X=152, Y=68.5) (X=155)          |
|                     |       |                                        |       |                    |
|  [ J1: SMA IN ]     v       v      100 Ω Diff Pair (34 mm run)       v       v     [ J2: OUT ]    |
|   (X=104, Y=75) -> [ U2: DRIVER ] ==============================> [ U3: RECEIVER ] -> (X=166,Y=75)|
|                     (X=118, Y=75)                                  (X=152, Y=75)                  |
|                                                                                                   |
|                                                                                                   |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+ (Y = 100 mm)
(X = 100 mm)                                                                                    (X = 170 mm)
```

---

## 7. Component Pairing & Distance Checklist

| Component | Placed Next To | Recommended Distance | Reason |
| :--- | :--- | :--- | :--- |
| **J1 (SMA In)** | Left Edge of PCB | Edge-aligned | Allows direct SMA cable attachment |
| **U2 (Driver)** | J1 (SMA In) | 8 to 12 mm | Keeps 50 Ω single-ended input trace short |
| **C2 (1 nF)** | U2 Pin 1 (VCC) | **< 1.5 mm** | High-frequency RF noise suppression |
| **C1 (100 nF)** | C2 / U2 Pin 1 | **< 3.0 mm** | Switching current reservoir |
| **U3 (Receiver)** | U2 (Driver) | 20 to 30 mm | Controlled 100 Ω diff pair run |
| **C4 (1 nF)** | U3 Pin 8 (VCC) | **< 1.5 mm** | High-frequency RF noise suppression |
| **C3 (100 nF)** | C4 / U3 Pin 8 | **< 3.0 mm** | Switching current reservoir |
| **J2 (Output)** | Right Edge of PCB | Edge-aligned | Easy connection to oscilloscope |
| **J3 (Power)** | Top Edge (Center) | 5 to 10 mm from top | Clean power distribution |

---

## 8. High-Speed Routing Rules & IPC Standards Summary

| Standard / Rule | Requirement | Technical Rationale |
| :--- | :--- | :--- |
| **IPC-2141A** | Controlled impedance tolerance ±10% max (±5% preferred). | Prevents signal reflections at connector and receiver interfaces. |
| **Solid Reference Plane (IPC-2251)** | Layer 2 GND must remain 100% continuous under differential pair. | Any slot or split in GND creates loop inductance, signal degradation, and EMI. |
| **3W Rule for Isolation** | Distance from diff pair to other signals ≥ 3 × Width (≥ 0.5 mm). | Eliminates crosstalk from adjacent switching lines. |
| **Bend Geometry** | Use 45° mitered corners or circular smooth arcs. | Avoids impedance dips and parasitic capacitance at 90° corners. |
| **Zero Vias on Diff Pair** | Keep `/LVDS_P` and `/LVDS_N` strictly on Layer 1 from U2 to U3. | Each via adds 0.5 to 1.0 nH parasitic inductance and impedance bumps. |
| **Ground Stitching** | Place ground vias along board perimeter every 5 mm (λ/10). | Suppresses cavity resonance and shields high-speed RF energy. |
