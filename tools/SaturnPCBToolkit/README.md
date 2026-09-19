# Saturn PCB Toolkit

Portable PCB engineering calculation utility for manual trace impedance, current capacity, and net-class calculations.

## Official Download
1. Visit the official website: https://saturnpcb.com/saturn-pcb-toolkit/
2. Click **Download Saturn PCB Toolkit** and fill in your name and email.
3. Download the executable installer/portable package and extract `PCB Toolkit.exe` into this folder:
   `G:\PCB_automation\tools\SaturnPCBToolkit\`

## How to Run
- Double-click `PCB Toolkit.exe` directly in Windows File Explorer (no installation or admin rights required).
- Or run from PowerShell / Terminal:
  ```powershell
  Start-Process "G:\PCB_automation\tools\SaturnPCBToolkit\PCB Toolkit.exe"
  ```

## Key Calculator Tabs for PCB Routing

### 1. Conductor Current (IPC-2152)
- **Goal:** Determine required copper trace width based on current carrying requirements.
- **Inputs:**
  - Current ($I$ in Amperes)
  - Allowable temperature rise ($\Delta T$, e.g., $10^\circ\text{C}$ or $20^\circ\text{C}$)
  - Copper weight ($1\text{ oz} = 35\,\mu\text{m}$, $2\text{ oz} = 70\,\mu\text{m}$)
  - Layer (External vs. Internal)
- **Output:** Minimum trace width ($W$).

### 2. Microstrip / Stripline (Controlled Impedance)
- **Goal:** Single-ended controlled impedance routing (e.g. 50 $\Omega$ RF, clock, high-speed lines).
- **Inputs:**
  - Substrate dielectric constant ($\varepsilon_r$, typically $4.2 - 4.5$ for FR4)
  - Substrate height ($H$)
  - Copper thickness ($T$)
  - Target impedance ($Z_0 = 50\,\Omega$)
- **Output:** Trace width ($W$).

### 3. Differential Pairs
- **Goal:** Differential pair routing (e.g. USB 90 $\Omega$, Ethernet/PCIe 100 $\Omega$).
- **Inputs:**
  - Target differential impedance ($Z_{\text{diff}}$)
  - Dielectric height ($H$) and $\varepsilon_r$
- **Output:** Trace width ($W$) and edge-to-edge trace spacing ($S$).

### 4. Via Current Capacity & Resistance
- **Goal:** Sizing power/GND vias to prevent bottlenecks and excessive voltage drop.
- **Inputs:**
  - Via drill diameter
  - Plating thickness ($0.5\text{ oz} - 1\text{ oz}$)
- **Output:** DC resistance ($R$), maximum current ($I_{\text{max}}$), and thermal rise.
