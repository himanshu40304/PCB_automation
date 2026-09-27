#!/usr/bin/env python3
"""3D Full-Wave Electromagnetic Simulation of LVDS Differential Microstrip for ParaView.

This script uses OpenEMS / CSXCAD (FDTD solver) to model:
1. Two coupled microstrip lines (W = 0.15 mm, S = 0.15 mm, Length = 34 mm).
2. FR4 Dielectric Substrate (Height = 0.1 mm, eps_r = 4.4, tan_delta = 0.02).
3. Solid Layer 2 Ground Reference Plane.
4. Differential Lumped Ports (Port 1 = Driver TX, Port 2 = Receiver RX with 110 Ohm load).
5. 3D Time-Domain E-Field & H-Field Dump (.vtr files) for ParaView 3D animated visualization.
"""

import os
import sys
import numpy as np

from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.ports import UI_data


def build_lvds_simulation(output_dir="/sim/sim_output", freq_max=2.0e9):
    """Set up and run the 3D FDTD electromagnetic simulation."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Unit: millimeters
    unit = 1e-3
    
    # Geometric Parameters (from your KiCad PCB)
    W = 0.15          # Trace width (mm)
    S = 0.15          # Edge-to-edge gap (mm)
    H = 0.10          # Substrate height to GND (mm)
    T = 0.035         # 1 oz Copper thickness (mm)
    L_trace = 34.0    # Physical run length (mm)
    L_sub = 40.0      # Substrate length (mm)
    W_sub = 10.0      # Substrate width (mm)
    
    eps_r = 4.4
    kappa = 2 * np.pi * 1e9 * eps_r * 8.854e-12 * 0.02
    
    # 1. Initialize FDTD Engine (4 GHz bandwidth for crisp, high-speed traveling pulse)
    f0 = 2.0e9
    fc = 2.0e9
    fdtd = openEMS(NrTS=4000, EndCriteria=1e-4)
    fdtd.SetGaussExcite(f0, fc)
    fdtd.SetBoundaryCond(['MUR', 'MUR', 'MUR', 'MUR', 'PEC', 'MUR'])
    
    # 2. Continuous Structure Setup (CSXCAD)
    csx = ContinuousStructure()
    fdtd.SetCSX(csx)
    mesh = csx.GetGrid()
    mesh.SetDeltaUnit(unit)
    
    # 3. Add FR4 Substrate
    substrate = csx.AddMaterial("FR4", epsilon=eps_r, kappa=kappa)
    substrate.AddBox(
        priority=0,
        start=[-W_sub/2, 0, 0],
        stop=[W_sub/2, L_sub, H]
    )
    
    # 4. Add Solid Ground Plane (Layer 2)
    gnd = csx.AddMetal("GND_PLANE")
    gnd.AddBox(
        priority=10,
        start=[-W_sub/2, 0, 0],
        stop=[W_sub/2, L_sub, 0]
    )
    
    # 5. Add Differential Traces (Layer 1 Top)
    x_p_center = +(S/2 + W/2)
    x_n_center = -(S/2 + W/2)
    
    trace_p = csx.AddMetal("LVDS_P")
    trace_p.AddBox(
        priority=10,
        start=[x_p_center - W/2, (L_sub - L_trace)/2, H],
        stop=[x_p_center + W/2, (L_sub + L_trace)/2, H + T]
    )
    
    trace_n = csx.AddMetal("LVDS_N")
    trace_n.AddBox(
        priority=10,
        start=[x_n_center - W/2, (L_sub - L_trace)/2, H],
        stop=[x_n_center + W/2, (L_sub + L_trace)/2, H + T]
    )
    
    # 6. Differential Ports (Lumped Ports between P and N)
    y_start = (L_sub - L_trace)/2
    y_end = (L_sub + L_trace)/2
    
    port1 = fdtd.AddLumpedPort(
        1, 100.0,
        [x_n_center, y_start, H],
        [x_p_center, y_start, H],
        "x", 1.0, priority=5
    )
    
    port2 = fdtd.AddLumpedPort(
        2, 110.0,
        [x_n_center, y_end, H],
        [x_p_center, y_end, H],
        "x", 0.0, priority=5
    )
    
    # 7. 3D Electric Field Dump (Et_paraview)
    efield_dump = csx.AddDump(
        "Et_paraview",
        dump_type=0,       # 0 = Time domain E-field (V/m)
        dump_mode=0
    )
    efield_dump.AddBox(
        start=[-W_sub/2, 0, 0],
        stop=[W_sub/2, L_sub, H + 0.5]
    )
    
    # 8. 3D Current Density Dump (Jt_current) - shows physical current moving along wires
    jfield_dump = csx.AddDump(
        "Jt_current",
        dump_type=2,       # 2 = Time domain Current Density (A/m^2)
        dump_mode=0
    )
    jfield_dump.AddBox(
        start=[-W_sub/2, 0, 0],
        stop=[W_sub/2, L_sub, H + T + 0.01]
    )
    
    # 9. Define FDTD Mesh
    mesh.AddLine('x', [-W_sub/2, x_n_center - W, x_n_center, x_n_center + W/2, 0, x_p_center - W/2, x_p_center, x_p_center + W, W_sub/2])
    mesh.AddLine('y', [0, y_start, (y_start + y_end)/2, y_end, L_sub])
    mesh.AddLine('z', [0, H, H + T, H + 0.5])
    mesh.SmoothMeshLines('all', 0.6, 1.4)
    
    # 9. Run FDTD Simulation
    print("Writing OpenEMS simulation files to:", output_dir)
    csx.Write2XML(os.path.join(output_dir, "lvds_pcb.xml"))
    
    print("Starting OpenEMS FDTD Solver...")
    fdtd.Run(output_dir, cleanup=False)
    print("Simulation finished successfully! 3D VTR files written to:", output_dir)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/sim/sim_output"
    build_lvds_simulation(out)
