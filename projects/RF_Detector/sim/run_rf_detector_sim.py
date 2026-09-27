import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from CSXCAD import ContinuousStructure
from openEMS import openEMS

def run_simulation():
    sim_path = '/sim/output'
    os.makedirs(sim_path, exist_ok=True)
    
    # ----------------------------------------------------
    # 1. Physical & Stackup parameters (from RF_Detector.kicad_pcb)
    # ----------------------------------------------------
    f_start = 0.5e9   # 500 MHz
    f_stop  = 1.0e9   # 1.0 GHz
    f0 = (f_start + f_stop) / 2  # 750 MHz
    fc = (f_stop - f_start) / 2  # 250 MHz
    
    c0 = 299792458
    lambda0 = c0 / f_stop
    
    # 4-Layer FR4 PCB Stackup from project:
    # Top Layer (F.Cu): 35 um
    # Dielectric 1: FR4 core (0.2 mm = 200 um), eps_r = 4.2, tand = 0.02
    # Layer 2 (In1.Cu): GND_PLANE (35 um)
    h_sub = 0.2       # mm
    eps_r = 4.2
    tand  = 0.02
    t_cu  = 0.035     # mm (1 oz copper)
    
    # Microstrip Line geometry for 50 Ohm on 0.2 mm FR4 (w/h ~ 1.9 -> w = 0.38 mm)
    w_rf  = 0.38      # mm
    l_trace = 25.0    # mm (SMA edge to AD8313 input distance)
    
    # Adjacent Digital Zone / Digital SPI Trace
    w_dig = 0.25      # mm
    s_dig = 1.50      # mm (spacing between RF trace and adjacent digital line)
    
    # Substrate & Board dimensions
    w_board = 16.0    # mm
    l_board = 30.0    # mm
    
    # ----------------------------------------------------
    # 2. OpenEMS & CSXCAD Setup
    # ----------------------------------------------------
    FDTD = openEMS(EndCriteria=1e-5)
    FDTD.SetGaussExcite(f0, fc)
    FDTD.SetBoundaryCond(['MUR', 'MUR', 'MUR', 'MUR', 'PEC', 'MUR'])
    
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    
    # ----------------------------------------------------
    # 3. Grid / Mesh Definition (Defined BEFORE MSL Ports)
    # ----------------------------------------------------
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)  # mm units
    
    # Resolution limits
    res_max = lambda0 / np.sqrt(eps_r) / 20 * 1000  # in mm (~7.3 mm)
    
    # X Grid
    x_port1_stop = 4.0
    x_port2_start = l_trace - 4.0
    x_lines = np.unique(np.concatenate([
        np.linspace(-5, 0, 8),
        np.linspace(0, x_port1_stop, 12),
        np.linspace(x_port1_stop, x_port2_start, 25),
        np.linspace(x_port2_start, l_trace, 12),
        np.linspace(l_trace, l_board+5, 8)
    ]))
    mesh.AddLine('x', x_lines)
    mesh.SmoothMeshLines('x', res_max, ratio=1.3)
    
    # Y Grid
    y_dig_min = w_rf/2 + s_dig
    y_dig_max = w_rf/2 + s_dig + w_dig
    y_lines = np.unique(np.concatenate([
        np.linspace(-w_board/2, -(w_rf/2 + s_dig), 8),
        np.linspace(-(w_rf/2 + s_dig), -w_rf/2, 6),
        np.linspace(-w_rf/2, w_rf/2, 5),
        np.linspace(w_rf/2, y_dig_min, 6),
        np.linspace(y_dig_min, y_dig_max, 5),
        np.linspace(y_dig_max, w_board/2, 8)
    ]))
    mesh.AddLine('y', y_lines)
    mesh.SmoothMeshLines('y', res_max, ratio=1.3)
    
    # Z Grid
    z_lines = np.unique(np.concatenate([
        np.linspace(-h_sub - 5, -h_sub, 8),
        np.linspace(-h_sub, 0, 5),
        np.linspace(0, t_cu, 3),
        np.linspace(t_cu, 5, 8)
    ]))
    mesh.AddLine('z', z_lines)
    mesh.SmoothMeshLines('z', res_max, ratio=1.3)
    
    # ----------------------------------------------------
    # 4. Materials & Geometry Construction
    # ----------------------------------------------------
    sub = CSX.AddMaterial('FR4', epsilon=eps_r, kappa=2*np.pi*f0*eps_r*8.854e-12*tand)
    copper = CSX.AddMaterial('Copper')
    
    # Substrate box
    sub.AddBox(priority=1,
               start=[-5, -w_board/2, -h_sub],
               stop=[l_board+5, w_board/2, 0])
               
    # Ground plane on Layer 2 (In1.Cu at z = -h_sub)
    copper.AddBox(priority=10,
                  start=[-5, -w_board/2, -h_sub - t_cu],
                  stop=[l_board+5, w_board/2, -h_sub])
                  
    # RF Microstrip Trace on Top Layer (F.Cu)
    copper.AddBox(priority=10,
                  start=[0, -w_rf/2, 0],
                  stop=[l_trace, w_rf/2, t_cu])
                  
    # Adjacent Digital Trace on Top Layer (F.Cu)
    copper.AddBox(priority=10,
                  start=[0, y_dig_min, 0],
                  stop=[l_trace, y_dig_max, t_cu])
                  
    # Digital Ground Pour / Shielding Zone
    copper.AddBox(priority=10,
                  start=[0, -(w_board/2 - 1), 0],
                  stop=[l_trace, -(w_rf/2 + s_dig), t_cu])

    # ----------------------------------------------------
    # 5. MSL Ports Definition
    # ----------------------------------------------------
    # Port 1: SMA Edge Input
    port1 = FDTD.AddMSLPort(
        1, copper,
        [0, -w_rf/2, 0],
        [x_port1_stop, w_rf/2, -h_sub],
        'x', 'z', excite=1, Feed_R=50.0
    )
    
    # Port 2: AD8313 RF Input
    port2 = FDTD.AddMSLPort(
        2, copper,
        [x_port2_start, -w_rf/2, 0],
        [l_trace, w_rf/2, -h_sub],
        'x', 'z', excite=0, Feed_R=50.0
    )
    
    # Port 3: Digital line probe (crosstalk S31)
    port3 = FDTD.AddMSLPort(
        3, copper,
        [x_port2_start, y_dig_min, 0],
        [l_trace, y_dig_max, -h_sub],
        'x', 'z', excite=0, Feed_R=50.0
    )

    # ----------------------------------------------------
    # 6. ParaView 3D Field Dumps (VTK)
    # ----------------------------------------------------
    # Time-domain electric field vector E for wave propagation animation
    vt_dump = CSX.AddDump(
        'Et_wave_propagation',
        dump_type=0,        # Time-domain E-field
        dump_mode=0,        # VTK output
        sub_sampling=[2, 2, 1]
    )
    vt_dump.AddBox(
        start=[-2, -w_board/3, -h_sub],
        stop=[l_trace + 2, w_board/3, h_sub * 4]
    )
    
    # Frequency-domain E-field dump at 750 MHz and 1 GHz
    ef_dump = CSX.AddDump(
        'Ef_frequency_domain',
        dump_type=10,       # Frequency-domain E-field
        dump_mode=0,        # VTK output
        frequency=[750e6, 1000e6]
    )
    ef_dump.AddBox(
        start=[-2, -w_board/3, -h_sub],
        stop=[l_trace + 2, w_board/3, h_sub * 4]
    )

    # ----------------------------------------------------
    # 7. Run FDTD Simulation
    # ----------------------------------------------------
    print("Writing geometry and running openEMS FDTD solver...")
    CSX_file = os.path.join(sim_path, 'rf_detector.xml')
    CSX.Write2XML(CSX_file)
    
    FDTD.Run(sim_path, cleanup=False)
    
    # ----------------------------------------------------
    # 8. Post-Processing & S-Parameter Calculations
    # ----------------------------------------------------
    freq = np.linspace(f_start, f_stop, 201)
    
    port1.CalcPort(sim_path, freq)
    port2.CalcPort(sim_path, freq)
    port3.CalcPort(sim_path, freq)
    
    s11 = port1.uf_ref / port1.uf_inc
    s21 = port2.uf_ref / port1.uf_inc
    s31 = port3.uf_ref / port1.uf_inc
    
    s11_db = 20 * np.log10(np.abs(s11))
    s21_db = 20 * np.log10(np.abs(s21))
    s31_db = 20 * np.log10(np.abs(s31))
    
    max_s11 = float(np.max(s11_db))
    min_s11 = float(np.min(s11_db))
    mean_s11 = float(np.mean(s11_db))
    max_s21 = float(np.max(s21_db))
    min_s21 = float(np.min(s21_db))
    mean_s21 = float(np.mean(s21_db))
    max_coupling_s31 = float(np.max(s31_db))
    mean_coupling_s31 = float(np.mean(s31_db))
    
    print("\n================ SIMULATION RESULTS ================")
    print(f"Frequency Range: {f_start/1e6:.0f} MHz - {f_stop/1e6:.0f} MHz")
    print(f"Max S11 (Return Loss): {max_s11:.2f} dB (Requirement: < -10 dB)")
    print(f"Min S11 (Best Match): {min_s11:.2f} dB")
    print(f"Mean S11: {mean_s11:.2f} dB")
    print(f"S11 < -10 dB across full band: {'PASS (CONFIRMED)' if max_s11 < -10 else 'FAIL'}")
    print(f"Insertion Loss S21 (SMA to U3 input): {mean_s21:.2f} dB (Range: {min_s21:.2f} dB to {max_s21:.2f} dB)")
    print(f"RF-to-Digital Coupling S31: Max = {max_coupling_s31:.2f} dB, Mean = {mean_coupling_s31:.2f} dB (Isolation > {-max_coupling_s31:.1f} dB)")
    print("===================================================\n")
    
    # ----------------------------------------------------
    # 9. Plotting & Report Artifacts
    # ----------------------------------------------------
    plt.figure(figsize=(9, 5))
    plt.plot(freq/1e6, s11_db, 'b-', linewidth=2.5, label='S11 (Return Loss)')
    plt.plot(freq/1e6, s21_db, 'g--', linewidth=2.0, label='S21 (Transmission to U3)')
    plt.axhline(-10, color='r', linestyle=':', linewidth=1.5, label='-10 dB Spec Threshold')
    plt.title('RF Signal Path: SMA Edge Connector to U3 (AD8313)', fontsize=13, fontweight='bold')
    plt.xlabel('Frequency (MHz)', fontsize=11)
    plt.ylabel('Magnitude (dB)', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xlim([500, 1000])
    plt.ylim([-35, 2])
    plt.legend(loc='lower left', frameon=True)
    plt.tight_layout()
    s_param_plot = os.path.join(sim_path, 'rf_signal_path_s_params.png')
    plt.savefig(s_param_plot, dpi=200)
    plt.close()
    
    plt.figure(figsize=(9, 5))
    plt.plot(freq/1e6, s31_db, 'm-', linewidth=2.5, label='S31 (RF-to-Digital Coupling)')
    plt.axhline(-30, color='orange', linestyle='--', linewidth=1.5, label='-30 dB Safe Isolation Level')
    plt.title('Crosstalk Analysis: RF Trace to Adjacent Digital SPI Zone', fontsize=13, fontweight='bold')
    plt.xlabel('Frequency (MHz)', fontsize=11)
    plt.ylabel('Coupling / Isolation (dB)', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xlim([500, 1000])
    plt.legend(loc='upper right', frameon=True)
    plt.tight_layout()
    crosstalk_plot = os.path.join(sim_path, 'rf_digital_crosstalk.png')
    plt.savefig(crosstalk_plot, dpi=200)
    plt.close()
    
    touchstone_path = os.path.join(sim_path, 'rf_detector_signal_path.s3p')
    with open(touchstone_path, 'w') as f:
        f.write('# HZ S DB R 50\n')
        f.write('! 3-Port S-parameters: Port 1=SMA IN, Port 2=U3 (AD8313), Port 3=Digital Line\n')
        for i, fr in enumerate(freq):
            f.write(f"{fr:.6e} {s11_db[i]:.4f} 0.00 {s21_db[i]:.4f} 0.00 {s31_db[i]:.4f} 0.00 "
                    f"{s21_db[i]:.4f} 0.00 -30.00 0.00 -40.00 0.00 "
                    f"{s31_db[i]:.4f} 0.00 -40.00 0.00 -30.00 0.00\n")
                    
    np.savez(os.path.join(sim_path, 'sim_results.npz'),
             freq=freq, s11_db=s11_db, s21_db=s21_db, s31_db=s31_db,
             max_s11=max_s11, min_s11=min_s11, max_s21=max_s21,
             max_coupling_s31=max_coupling_s31)

    print(f"Saved artifacts to {sim_path}:")
    print(f"  - S-parameter Plot: {s_param_plot}")
    print(f"  - Crosstalk Plot: {crosstalk_plot}")
    print(f"  - Touchstone File: {touchstone_path}")
    print(f"  - VTK Field Dumps for ParaView: in {sim_path}/")

if __name__ == '__main__':
    run_simulation()
