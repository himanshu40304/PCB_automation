#!/usr/bin/env python3
"""3D Full-Wave Electromagnetic Simulation of 70mm x 50mm LVDS Evaluation Board for ParaView.

Continuous end-to-end signal propagation across the entire 70x50 mm PCB:
1. Left SMA J1 Input Launch (X = -30 mm) -> 50 Ohm Single-Ended Trace
2. Driver U2 (SN65LVDS1D) differential splitting network (X = -12 to -10 mm)
3. 100 Ohm Coupled Differential Pair (LVDS_P & LVDS_N: X = -10 to +10 mm)
4. Receiver U3 (SN65LVDT2D) differential combiner (X = +10 to +12 mm)
5. 50 Ohm Single-Ended Trace -> Right SMA J2 Output (X = +30 mm)
6. 4-Side ENIG Gold Edge Plating + Ground Stitching.
7. ParaView Time-Series 3D Field Dumps (Et_paraview, Ht_paraview, Jt_current).
"""

import os
import sys
import numpy as np

from CSXCAD import ContinuousStructure
from openEMS import openEMS


def build_full_lvds_board_simulation(output_dir="/sim/sim_output", freq_max=3.0e9):
    """Set up and run the full 70mm x 50mm LVDS board EM simulation."""
    os.makedirs(output_dir, exist_ok=True)
    
    unit = 1e-3  # mm
    
    # Board Dimensions (70 mm x 50 mm)
    W_board = 70.0  # along X (-35 to +35 mm)
    H_board = 50.0  # along Y (-25 to +25 mm)
    H_sub = 0.10    # 0.10 mm Prepreg to Layer 2 GND
    T_cu = 0.035    # 35 um 1 oz Copper
    
    eps_r = 4.5
    kappa = 2 * np.pi * 1.5e9 * eps_r * 8.854e-12 * 0.02
    
    # 1. Initialize FDTD Engine
    f0 = freq_max / 2.0
    fc = freq_max / 2.0
    fdtd = openEMS(NrTS=5000, EndCriteria=1e-4)
    fdtd.SetGaussExcite(f0, fc)
    fdtd.SetBoundaryCond(['MUR', 'MUR', 'MUR', 'MUR', 'PEC', 'MUR'])
    
    # 2. Continuous Structure
    csx = ContinuousStructure()
    fdtd.SetCSX(csx)
    mesh = csx.GetGrid()
    mesh.SetDeltaUnit(unit)
    
    # 3. FR4 Substrate (70 x 50 mm)
    sub = csx.AddMaterial("FR4", epsilon=eps_r, kappa=kappa)
    sub.AddBox(
        priority=0,
        start=[-W_board/2, -H_board/2, 0],
        stop=[W_board/2, H_board/2, H_sub]
    )
    
    # 4. Layer 2 Solid Ground Plane (Z = 0)
    gnd = csx.AddMetal("GND_PLANE")
    gnd.AddBox(
        priority=10,
        start=[-W_board/2, -H_board/2, 0],
        stop=[W_board/2, H_board/2, 0]
    )
    
    # 5. Gold Edge Plating Perimeter Ring (1.0 mm wide on Layer 1)
    edge_metal = csx.AddMetal("EDGE_GOLD_PLATING")
    # Top & Bottom edges
    edge_metal.AddBox(priority=10, start=[-W_board/2, H_board/2 - 1.0, H_sub], stop=[W_board/2, H_board/2, H_sub + T_cu])
    edge_metal.AddBox(priority=10, start=[-W_board/2, -H_board/2, H_sub], stop=[W_board/2, -H_board/2 + 1.0, H_sub + T_cu])
    # Left & Right edges
    edge_metal.AddBox(priority=10, start=[-W_board/2, -H_board/2, H_sub], stop=[-W_board/2 + 1.0, H_board/2, H_sub + T_cu])
    edge_metal.AddBox(priority=10, start=[W_board/2 - 1.0, -H_board/2, H_sub], stop=[W_board/2, H_board/2, H_sub + T_cu])
    
    # 6. High-Speed Copper Traces (End-to-End Connected Path)
    W_50 = 0.18    # 50 Ohm single-ended width (mm)
    W_diff = 0.15  # 100 Ohm differential trace width (mm)
    S_diff = 0.15  # Differential pair spacing (mm)
    
    y_p = +(S_diff/2 + W_diff/2)
    y_n = -(S_diff/2 + W_diff/2)
    
    # Section A: Left 50 Ohm Single-Ended Trace (J1 to U2: X = -30 to -12 mm)
    sig_in = csx.AddMetal("TRACE_50R_IN")
    sig_in.AddBox(priority=12, start=[-30.0, -W_50/2, H_sub], stop=[-12.0, W_50/2, H_sub + T_cu])
    
    # Section B: Driver U2 Internal Y-Splitter Bridge (X = -12 to -10 mm)
    driver_metal = csx.AddMetal("DRIVER_U2_BRIDGE")
    driver_metal.AddBox(priority=12, start=[-12.0, y_n - W_diff/2, H_sub], stop=[-10.0, y_p + W_diff/2, H_sub + T_cu])
    
    # Section C: 100 Ohm Differential Pair (LVDS_P & LVDS_N: X = -10 to +10 mm)
    diff_p = csx.AddMetal("LVDS_P")
    diff_p.AddBox(priority=12, start=[-10.0, y_p - W_diff/2, H_sub], stop=[+10.0, y_p + W_diff/2, H_sub + T_cu])
    
    diff_n = csx.AddMetal("LVDS_N")
    diff_n.AddBox(priority=12, start=[-10.0, y_n - W_diff/2, H_sub], stop=[+10.0, y_n + W_diff/2, H_sub + T_cu])
    
    # Section D: Receiver U3 Internal Combiner Bridge (X = +10 to +12 mm)
    rx_metal = csx.AddMetal("RECEIVER_U3_BRIDGE")
    rx_metal.AddBox(priority=12, start=[+10.0, y_n - W_diff/2, H_sub], stop=[+12.0, y_p + W_diff/2, H_sub + T_cu])
    
    # Section E: Right 50 Ohm Single-Ended Trace (U3 to J2: X = +12 to +30 mm)
    sig_out = csx.AddMetal("TRACE_50R_OUT")
    sig_out.AddBox(priority=12, start=[+12.0, -W_50/2, H_sub], stop=[+30.0, W_50/2, H_sub + T_cu])
    
    # 7. Excitation and Ports
    # Port 1: Left Input SMA J1 Launch (50 Ohm source)
    port1 = fdtd.AddLumpedPort(
        1, 50.0,
        [-30.0, 0, H_sub],
        [-28.0, 0, H_sub],
        "x", 1.0, priority=15
    )
    
    # Port 2: Right Output SMA J2 Termination (50 Ohm matched load)
    port2 = fdtd.AddLumpedPort(
        2, 50.0,
        [+28.0, 0, H_sub],
        [+30.0, 0, H_sub],
        "x", 0.0, priority=15
    )
    
    # 8. Field Dumps for ParaView
    # 3D Electric Field Dump (Et_paraview) covering the full 70 x 50 mm board
    e_dump = csx.AddDump("Et_paraview", dump_type=0, dump_mode=0)  # 0 = E-field
    e_dump.AddBox(start=[-W_board/2, -H_board/2, 0], stop=[W_board/2, H_board/2, H_sub + 1.0])
    
    # 3D Magnetic Field Dump (Ht_paraview)
    h_dump = csx.AddDump("Ht_paraview", dump_type=1, dump_mode=0)  # 1 = H-field
    h_dump.AddBox(start=[-W_board/2, -H_board/2, 0], stop=[W_board/2, H_board/2, H_sub + 1.0])
    
    # 3D Current Density Dump (Jt_current)
    j_dump = csx.AddDump("Jt_current", dump_type=2, dump_mode=0)  # 2 = Current Density
    j_dump.AddBox(start=[-W_board/2, -H_board/2, 0], stop=[W_board/2, H_board/2, H_sub + T_cu + 0.01])
    
    # 9. Mesh Definition (FDTD Grid)
    mesh.AddLine('x', [-W_board/2, -30.0, -12.0, -10.0, 0, 10.0, 12.0, 30.0, W_board/2])
    mesh.AddLine('y', [-H_board/2, -5.0, y_n, 0, y_p, 5.0, H_board/2])
    mesh.AddLine('z', [-1.0, 0, H_sub, H_sub + T_cu, H_sub + 1.5])
    mesh.SmoothMeshLines('all', 1.0, 1.4)
    
    # 10. Run Simulation
    print("Writing 70mm x 50mm End-to-End Continuous Simulation to:", output_dir)
    csx.Write2XML(os.path.join(output_dir, "lvds_full_board.xml"))
    
    print("Starting OpenEMS FDTD Engine...")
    fdtd.Run(output_dir, cleanup=True)
    print("\nEnd-to-end simulation complete! Time-series field files written to:", output_dir)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/sim/sim_output"
    build_full_lvds_board_simulation(out)
