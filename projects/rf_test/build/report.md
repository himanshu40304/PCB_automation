# Verification report: x_band_patch

- design hash: `0fe504ba0df77ec4`
- center frequency: 10 GHz
- overall: **PASS**

## Steps

| step | status | detail |
|------|--------|--------|
| geometry | pass | 2 shapes inside outline |
| kicad_drc | pass | DRC: 0 error(s), 0 warning(s), 0 unconnected item(s) |
| em_simulation | pass | f_res = 9.840 GHz (target 10 GHz, 1.6% off), S11 min = -11.5 dB |

## Metrics

- bandwidth_10db_hz: 1e+08
- directivity_dbi: 6.77623
- f_res_hz: 9.84e+09
- gain_dbi: 5.98729
- s11_min_db: -11.5387

## Artifacts

- board_render: `g:\PCB_automation\projects\rf_test\build\board_top.png`
- drc_json: `g:\PCB_automation\projects\rf_test\build\x_band_patch.drc.json`
- kicad_pcb: `g:\PCB_automation\projects\rf_test\build\x_band_patch.kicad_pcb`
- pattern_plot: `g:\PCB_automation\projects\rf_test\build\pattern.png`
- s11_plot: `g:\PCB_automation\projects\rf_test\build\s11.png`

## Synthesis parameters

- center_frequency: 10.0 GHz
- edge_resistance_ohm: 291.5035034780531
- eps_eff: 3.374697753293875
- feed_width: 1.1120102238061023 mm
- inset_depth: 2.1307054476073537 mm
- inset_gap: 0.5560051119030511 mm
- patch_length: 7.679288535729216 mm
- patch_width: 9.820028466961448 mm
- substrate: RO4350B
