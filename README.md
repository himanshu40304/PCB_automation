# PCB Automation & Design Pipeline

An autonomous, end-to-end PCB design, verification, and manufacturing pipeline powered by **KiCad**, **SPICE**, and **AI-driven Automation Agents**.

---

## 🚀 Overview & Automation Architecture

This repository contains automated workflows, design tools, and complete hardware projects demonstrating AI-assisted schematic creation, SPICE verification, electrical rules check (ERC), automated component placement, routing, clearance isolation, and design rules check (DRC).

```mermaid
graph LR
    A["Requirements & Spec"] --> B["Schematic Capture"]
    B --> C["SPICE Simulation & ERC"]
    C --> D["Board Setup & Constraints"]
    D --> E["Component Placement & Floorplanning"]
    E --> F["Routing & Isolated Plane Pours"]
    F --> G["DRC & DFM Production Audit"]
    G --> H["Manufacturing Gerber & BOM Export"]
```

---

## 📂 Projects in this Repository

### 1. `projects/ACtoDCtoMicrocontroller`
* **Description:** An integrated compact IoT board converting mains AC to regulated 5V & 3.3V DC to power an ESP32/Microcontroller with USB programming, switches, and antenna keepout.
* **Key Features:**
  * **Mains AC Input Stage:** Screw terminal (`J1`), NTC inrush limiter (`RT1`), X-Capacitor (`C1`), and HLK-5M05 isolated AC-DC module.
  * **Microcontroller & Logic Domain:** 3.3V LDO regulator, ESP32 module, reset & boot switches, Micro-USB interface, and dedicated RF Antenna Keep-Out Zone.
  * **Physical Isolation:** Strict primary-to-secondary dielectric isolation barrier.
  * **Artifacts:** Complete `.kicad_sch`, `.kicad_pcb`, interactive SVGs, manufacturing BOM, and CPL files.

#### Visual Showcase & 3D Previews

| Top Layer Layout (HV Isolation & 5V Fill) | Bottom Layer Layout (3.3V & Signal Routing) |
| :---: | :---: |
| ![Top Layout](docs/images/ACtoDCtoMicrocontroller/pcb_layout_front_2d.png) | ![Bottom Layout](docs/images/ACtoDCtoMicrocontroller/pcb_layout_back_2d.png) |

| Top 3D Assembly (HLK Module & AC Protection) | Bottom 3D Assembly (MCU, Buttons, USB) |
| :---: | :---: |
| ![Top 3D Render](docs/images/ACtoDCtoMicrocontroller/pcb_render_top_3d.png) | ![Bottom 3D Render](docs/images/ACtoDCtoMicrocontroller/pcb_render_bottom_3d.png) |

### 2. `projects/AC_DC_converter_with_regulated_dc`
* **Description:** A **$60\text{ mm} \times 50\text{ mm}$** AC-to-DC Adjustable Regulated Power Supply using a Full-Wave Bridge Rectifier and LM317.
* **Key Features:**
  * **Primary High-Voltage AC Domain ($X \le 120\text{ mm}$):** 2-pin screw terminal (`J1`), MOV surge suppressor (`RV_MOV1`), 5x20mm fuse (`F1`), and 1N4007 bridge rectifier (`D1–D4`).
  * **Secondary Low-Voltage DC Domain ($X \ge 122\text{ mm}$):** $1000\mu\text{F}$ bulk filter (`C1`), LM317 regulator (`U1`), 5k$\Omega$ precision trimpot (`RV1`), output decoupling (`C4`, `C5`), and green LED indicator (`D7`).
  * **Safety & Isolation:** $>3.0\text{ mm}$ physical creepage/clearance barrier between Primary AC and Secondary DC.
  * **Isolated Ground Pours:** Top and Bottom GND copper pours restricted to the DC secondary domain.
  * **Verification Status:** **0 ERC Errors, 0 DRC Errors, 0 Courtyard Overlaps, 0 Boundary Violations**.

#### Visual Showcase & Design Views

| Schematic (Annotated Sections) | 2D PCB Layout (HV/LV Split & GND Pour) |
| :---: | :---: |
| ![Schematic](docs/images/AC_DC_converter_with_regulated_dc/schematic.png) | ![2D PCB Layout](docs/images/AC_DC_converter_with_regulated_dc/pcb_layout_2d.png) |

<p align="center">
  <b>3D Board Assembly Render</b><br>
  <img src="docs/images/AC_DC_converter_with_regulated_dc/pcb_render_3d.png" width="75%" alt="3D Board Assembly Render" />
</p>

---

## 🛠️ Automated Tools & Pipeline Frameworks

* **`PCB_AUTOMATION_PIPELINE_GUIDE.md`**: Complete architectural reference guide for automating KiCad schematic capture, layout, SPICE simulation, and Gerber generation.
* **`pcb-workflow.md`**: Step-by-step workflow for executing design steps from netlist generation to DFM checks.
* **`KiCAD-MCP-Server`**: Model Context Protocol integration enabling autonomous LLM interaction with KiCad's layout engine.
* **`SPICEBridge`**: Automated SPICE netlist extraction and ngspice simulation harness.
* **`Konnect`**: Automated net connectivity and routing optimization toolset.

---

## 📄 License
MIT License. Open source hardware and automation scripts.
