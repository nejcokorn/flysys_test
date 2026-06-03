# FlySys KiCad Components and Placement

Updated: 2026-06-03

The KiCad schematic is in `kicad/flysys_vario.kicad_sch`. It uses the generated
local symbol library `kicad/flysys_symbols.kicad_sym` and footprint libraries
from `parts/`.

The DigiKey purchasing BOM is generated at
`kicad/flysys_vario_digikey_bom.csv`. A readable version is in
`docs/digikey-bom.md`. Debug pads are not fitted in this design; normal firmware
update is software-first, and ESP32-S3 ROM bootloader entry is a hidden service
fallback through the USB connector plus `BOOT`/`RST` buttons.

The Atopile/LCSC picked component set is documented separately in
`docs/lcsc-bom.md`. The full text description of the schematic, capacitor
roles, and wiring/layout constraints is in `docs/schematic-description.md`.
The firmware update and USB-attached idle UX is in
`docs/firmware-update-ux.md`.

Regenerate and verify the schematic with:

```sh
python3 tools/generate_kicad_schematic.py
snap run kicad.kicad-cli sch export netlist --format kicadsexpr --output build/kicad/flysys_vario.net kicad/flysys_vario.kicad_sch
snap run kicad.kicad-cli sch erc --format json --output build/kicad/flysys_vario_erc.json kicad/flysys_vario.kicad_sch
```

The component positions below describe intended physical placement for the PCB
layout review. They are not a claim that the KiCad PCB has been placed or
routed.

## Main Components

| Ref | Source instance | Component | Role | Placement intent |
| --- | --- | --- | --- | --- |
| `USB1` | `usb` | `USB4105-GF-A` USB-C receptacle | USB 2.0 device, charging input, flashing/log/config access | On board edge. Keep `D+`/`D-` short into `D1`; keep CC resistors next to connector. |
| `D1` | `usb_esd` | `USBLC6-2SC6Y` | Automotive/AEC-Q101 USB ESD protection | Between `USB1` and `U4`, close to `USB1`, before the USB pair enters the board. Same SOT-23-6L placement intent as the previous part. |
| `U1` | `charger` | `BQ24075RGTR` | LiPo charger and power-path management | Near USB VBUS and battery connector. Keep `IN`, `BAT`, `OUT`, and thermal ground paths short and wide. |
| `U3` | `ldo_3v3` | `TLV75533PDBVR` | 3.3 V regulator from `SYS` | Near `U1` and the `+3V3` loads. Keep input/output caps tight to pins. |
| `U4` | `mcu` | `ESP32-S3-MINI-1-N8` | BLE, USB device, application MCU | Top/right edge so the module antenna faces the board edge/keepout. Do not place copper or tall metal in antenna keepout. |
| `U5` | `pressure` | `BMP581` | Pressure sensor for altitude/vario | Near pressure vent, away from heat, adhesive, board flex, and buzzer airflow. |
| `U2` | `imu` | `BMI323` | 6-axis accelerometer/gyro | Near board center on mechanically stable PCB area. Document final axis orientation in firmware. |
| `J1` | `battery` | `S2B-PH-SM4-TB` | 2-pin LiPo connector | Near charger `BAT` pins. Confirm protected pack polarity before ordering/build. |
| `BZ1` | `buzzer` | `CSS-J4D20-SMT-TR` | Loud firmware-driven vario tone output | Lower/right side near acoustic outlet. Keep buzzer current loop local to `BZ1`, `Q1`, and `C3`. |
| `Q1` | `q_buzzer` | `AO3400A` | Low-side MOSFET for buzzer PWM | Next to buzzer return pad. Keep drain loop compact. |
| `Q2` | `q_ble_led` | `AO3400A` | Low-side MOSFET for blue BLE LED | Near `LED1`/`R5`. Needed because blue LED is powered from `SYS`. |
| `Q3` | `q_sysoff` | `AO3400A` | Low-side MOSFET that latches BQ24075 `SYSOFF` low | Near `U1`/`SYSOFF` control resistors. Keep `CHG_SYSOFF` compact and quiet. |
| `Q4` | `q_bat_switch` | `DMP3098L` | P-channel high-side battery hard-off switch from `BAT_RAW` to `BAT` | Between `J1` and `U1 BAT`. Keep the switched battery path short and wide. |
| `Q5` | `q_bat_gate` | `AO3400A` | Low-side MOSFET that holds `Q4` gate low while power is latched | Near `Q4` gate and `R28`. |
| `D2`, `D3`, `D4` | power-start diodes | `1N4148W` | Diode isolation from raw power button to MCU input, `BAT_SWITCH_GATE`, and `CHG_SYSOFF` | Near `SW1` and the power latch nets. |
| `SW1` | `user_button` | `KMR211NG LFS` | Active-low power/user button | Accessible edge area. Pressing it starts the board from battery hard-off and is read by the MCU through `D2`; firmware also uses it to leave USB-attached idle mode. |
| `SW2` | `boot_button` | `KMR211NG LFS` | ESP32-S3 BOOT recovery button | Hidden service/pinhole access only. Label on PCB as `BOOT`; hold while tapping `RST` to enter ROM bootloader recovery. |
| `SW3` | `reset_button` | `KMR211NG LFS` | ESP32-S3 RESET recovery button | Hidden service/pinhole access only. Label on PCB as `RST`; use with `BOOT` for ROM bootloader recovery. |
| `LED2` | `power_led` | `LTST-C190GKT` green LED | Power indicator | Lower edge where visible; series resistor `R20` next to it. |
| `LED1` | `ble_led` | `LTST-C190TBKT` blue LED | Firmware BLE status indicator | Lower/right visible edge; driven through `Q2`. |

## Capacitors

| Ref | Source instance | Value | Connected nets | Purpose and placement |
| --- | --- | --- | --- | --- |
| `C14` | `c_vbus_in` | 1 uF | `USB_VBUS` to `GND` | USB input bulk/decoupling. Place close to `USB1`/`U1 IN`. |
| `C13` | `c_sys_bulk` | 10 uF | `SYS` to `GND` | Charger system rail bulk. Place close to `U1 OUT`; helps `U3` and buzzer transients. |
| `C1` | `c_bat_bulk` | 10 uF | `BAT` to `GND` | Switched battery rail bulk. Place near `Q4` drain and `U1 BAT`. |
| `C7` | `c_ldo_in` | 1 uF | `SYS` to `GND` | LDO input capacitor. Place at `U3 IN/GND`. |
| `C8` | `c_ldo_out` | 1 uF | `+3V3` to `GND` | LDO output capacitor. Place at `U3 OUT/GND`. |
| `C9` | `c_mcu_bulk` | 10 uF | `+3V3` to `GND` | ESP32-S3 local bulk for RF/current peaks. Place close to `U4 3V3`. |
| `C10` | `c_mcu_decoup` | 100 nF | `+3V3` to `GND` | ESP32-S3 high-frequency decoupling. Place close to `U4 3V3`. |
| `C12` | `c_pressure_vdd` | 100 nF | `BMP581 VDD` to `GND` | Pressure sensor core decoupling. Place next to `U5`. |
| `C11` | `c_pressure_vddio` | 100 nF | `BMP581 VDDIO` to `GND` | Pressure sensor I/O decoupling. Place next to `U5`. |
| `C6` | `c_imu_vdd` | 100 nF | `BMI323 VDD` to `GND` | IMU core decoupling. Place next to `U2`. |
| `C5` | `c_imu_vddio` | 100 nF | `BMI323 VDDIO` to `GND` | IMU I/O decoupling. Place next to `U2`. |
| `C3` | `c_buzzer_bulk` | 10 uF | `SYS` to `GND` | Local buzzer supply reservoir. Place close to `BZ1`/`Q1` to keep current loop local. |
| `C4` | `c_en` | 100 nF | `EN` to `GND` | ESP32-S3 reset/enable RC cap. Place close to `U4 EN`. |
| `C2` | `c_bat_sense` | 100 nF | `BAT_SENSE` to `GND` | ADC filter for battery divider. Place near MCU ADC pin and divider midpoint. |

## Resistors

| Ref | Source instance | Value | Purpose and placement |
| --- | --- | --- | --- |
| `R9` | `r_cc1` | 5.1 k | USB-C `CC1` pull-down. Place close to `USB1`. |
| `R10` | `r_cc2` | 5.1 k | USB-C `CC2` pull-down. Place close to `USB1`. |
| `R15` | `r_chg_ts` | 10 k | Charger TS bias for baseline no-thermistor setup. Place close to `U1 TS`; revisit if using pack thermistor. |
| `R12` | `r_chg_iset` | 2 k | BQ24075 charge-current set resistor. Place close to `U1 ISET`. |
| `R11` | `r_chg_ilim` | 1.1 k | BQ24075 input current-limit set resistor. Place close to `U1 ILIM`. |
| `R14` | `r_chg_tmr` | 47 k | BQ24075 timer set resistor. Place close to `U1 TMR`. |
| `R13` | `r_chg_pullup` | 10 k | Pull-up for charger `nCHG` status into MCU. Place near `U1`/routing to `U4`. |
| `R19` | `r_pgood_pullup` | 10 k | Pull-up for charger `nPGOOD` status into MCU. Place near `U1`/routing to `U4`. |
| `R16` | `r_en_pullup` | 10 k | ESP32-S3 `EN` pull-up. Place close to `U4 EN`; keep near `C4`. |
| `R6` | `r_boot_pullup` | 10 k | ESP32-S3 `IO0`/BOOT pull-up. Place near `U4`/`SW2`. |
| `R23` | `r_sysoff_pullup` | 1 M | Pull-up from `CHG_SYSOFF` to switched `BAT`. Place near `U1 SYSOFF`. |
| `R24` | `r_pwr_hold_gate_pu` | 100 k | Pull-up from `PWR_HOLD_GATE` to `+3V3` so power latches even in ROM bootloader. Place near `Q3`/`Q5`. |
| `R25` | `r_pwr_hold_gate` | 100 ohm | Series resistor from MCU `PWR_HOLD` to the latch gate. Place near `U4`/`Q3` route. |
| `R26` | `r_pwr_hold_gate_pd` | 1 M | Latch-gate pulldown while `+3V3` is absent. Place near `Q3`/`Q5`. |
| `R27` | `r_pwr_btn_pullup` | 4.7 k | Pull-up for active-low `PWR_BTN_N` button input. Place near `U4`/`SW1`. |
| `R28` | `r_bat_switch_gate_pu` | 1 M | Pull-up from `BAT_SWITCH_GATE` to `BAT_RAW` for true battery disconnect by default. Place near `Q4`. |
| `R2` | `r_bat_sense_top` | 1 M | Top of battery voltage divider from `BAT` to `BAT_SENSE`. Place near `R1`/`C2`; keep divider node quiet. |
| `R1` | `r_bat_sense_bottom` | 1 M | Bottom of battery voltage divider from `BAT_SENSE` to `GND`. Place near `R2`/`C2`. |
| `R22` | `r_vbus_sense_top` | 1 M | Top of USB VBUS sense divider. Place near `R21` and route to MCU sense input. |
| `R21` | `r_vbus_sense_bottom` | 330 k | Bottom of USB VBUS sense divider. Place near `R22`. |
| `R17` | `r_i2c_scl_pullup` | 4.7 k | I2C SCL pull-up to `+3V3`. Place between MCU and sensors; keep away from noisy buzzer loop. |
| `R18` | `r_i2c_sda_pullup` | 4.7 k | I2C SDA pull-up to `+3V3`. Place next to `R17`. |
| `R8` | `r_buzzer_gate` | 100 ohm | Series gate resistor from ESP32 PWM to `Q1`. Place at `Q1` gate. |
| `R7` | `r_buzzer_gate_pd` | 100 k | `Q1` gate pulldown so buzzer stays off at reset. Place at `Q1` gate/source. |
| `R20` | `r_power_led` | 1 k | Green power LED current limit from `+3V3`. Place next to `LED2`. |
| `R5` | `r_ble_led` | 1 k | Blue BLE LED current limit from `SYS`. Place next to `LED1`/`Q2`. |
| `R4` | `r_ble_gate` | 100 ohm | Series gate resistor from ESP32 GPIO to `Q2`. Place at `Q2` gate. |
| `R3` | `r_ble_gate_pd` | 100 k | `Q2` gate pulldown so BLE LED stays off at reset. Place at `Q2` gate/source. |

## Routing Constraints for PCB Layout Review

See `docs/schematic-description.md` for the full text version of the schematic
and detailed connection constraints.

- USB `D+`/`D-` must route from `USB1` through `D1` before going to `U4 GPIO20/GPIO19`. Keep this pair short and parallel in the final layout review.
- `SW2` and `SW3` should be reachable only through service access or pinholes, not as normal exposed user controls. Add `BOOT` and `RST` PCB/service labels.
- `USB_VBUS`, `BAT`, and `SYS` are routed wider than logic nets. These carry charger, regulator, and buzzer current.
- `+3V3` fans out from `U3` to `U4`, `U5`, `U2`, pull-ups, and LEDs.
- `U5` and `U2` decoupling capacitors are placed adjacent to their devices rather than grouped with generic capacitors.
- `BZ1`, `Q1`, `R8`, `R7`, and `C3` are grouped together to keep the buzzer switching current local.
- `U1`, `Q3`, `Q4`, `Q5`, `D2`-`D4`, `R23`, `R24`, `R26`, and `R28` should keep the hard-off latch short and away from the buzzer gate and USB data routing.

## Current Limitations

The local footprints for `J1`, `BZ1`, `Q1`, `Q2`, `Q3`, `Q4`, `Q5`, `D2`-`D4`, and `SW1`-`SW3` are draft local footprints. Before production, verify each against manufacturer land-pattern drawings and enclosure mechanics.

Atopile 0.15.7 currently supports only LCSC in its built-in `has_part_picked`
BOM path. For DigiKey-only ordering, use the generated DigiKey BOM above. For
the current Atopile-picked LCSC subset, use `docs/lcsc-bom.md`.

The KiCad schematic is verified by ERC and netlist export, but the PCB placement and routing still need a separate KiCad layout pass.
