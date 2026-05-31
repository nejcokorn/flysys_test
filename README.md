# FlySys Hardware Plan

Updated: 2026-05-31

This folder is intentionally a planning workspace only. The next hardware build will be created from scratch in Atopile. Old EasyEDA, KiCad, generated production files, and JLC-specific draft outputs are not part of the active design.

## Goal

Build a compact FlySys variometer board with:

- BLE-first telemetry and configuration.
- Accurate pressure-based vertical-speed sensing.
- 6-axis inertial sensing for filtering/orientation support.
- LiPo charging and battery operation.
- Piezo audio output.
- Simple button, status LED, USB, and debug access.

## Selected Components

| Function | Selection | Supplier note |
| --- | --- | --- |
| MCU/BLE/Wi-Fi | Espressif `ESP32-C3-MINI-1-N4X` | Use this exact `N4X` variant. Do not use older `ESP32-C3-MINI-1-N4`, which was shown as not-for-new-design / 0 stock. |
| Pressure sensor | Bosch `BMP581` | Primary altitude/variometer pressure sensor. |
| 6-axis IMU | Bosch `BMI323` | Primary accelerometer/gyro. |
| Magnetometer | Not fitted | Keep unpopulated I2C pads or optional footprint for future magnetometer. |
| Charger / power path | TI `BQ24075RGTR` | 1S LiPo charger with power-path management. |
| 3.3 V regulator | TI `TLV75533PDBVR` | Replaces `AP2112K-3.3TRG1` because AP2112 was 0 stock in the DigiKey.si audit. ESP32-C3 radio transmission will be kept minimal in production. Add local bulk capacitance near the module. |
| USB | GCT `USB4105-GF-A` + ST `USBLC6-2SC6` | USB-C 2.0 receptacle and USB ESD for charging, USB Serial/JTAG, logs, and flashing. |
| Audio | Same Sky `CPT-9019A-SMT-TR` + `AO3400A` N-MOSFET | 3 V externally driven piezo plus low-side driver. Keep optional wired piezo pads if enclosure volume is insufficient. |
| User input | C&K `KMR211NG LFS` | Momentary active-low tactile switch. Final actuator geometry still depends on enclosure height. |
| Battery | JST `S2B-PH-SM4-TB` | 2-pin JST-PH right-angle SMD header. Confirm protected pack and cable polarity. |
| Debug | ESP32-C3 USB Serial/JTAG, `EN`, `BOOT`, optional UART0 pads | ESP32-C3 does not use SWD. |

## DigiKey.si Availability Audit

Checked: 2026-05-31. Stock changes quickly; recheck before ordering.

| Function | MPN | DigiKey cut-tape part | Observed availability | Status |
| --- | --- | --- | --- | --- |
| MCU/BLE/Wi-Fi | `ESP32-C3-MINI-1-N4X` | `1965-ESP32-C3-MINI-1-N4XCT-ND` | 955 in stock | Selected |
| Pressure sensor | `BMP581` | `828-BMP581CT-ND` | 46,324 in stock | Selected |
| 6-axis IMU | `BMI323` | `828-BMI323CT-ND` | 663 in stock | Selected |
| Charger / power path | `BQ24075RGTR` | `296-38874-1-ND` | 3,702 in stock | Selected |
| 3.3 V LDO, rejected | `AP2112K-3.3TRG1` | `AP2112K-3.3TRG1DICT-ND` | 0 in stock | Do not use for current DigiKey-sourced build |
| 3.3 V LDO, replacement | `TLV75533PDBVR` | `296-50411-1-ND` | 110,688 in stock | Selected replacement |
| USB-C receptacle | `USB4105-GF-A` | `2073-USB4105-GF-ACT-ND` | 126,702 in stock | Selected |
| USB ESD | `USBLC6-2SC6` | `497-5235-1-ND` | 86,224 in stock | Selected |
| Battery connector | `S2B-PH-SM4-TB` | `455-S2B-PH-SM4-TBCT-ND` | 71,350 in stock | Selected |
| Buzzer | `CPT-9019A-SMT-TR` | `2223-CPT-9019A-SMT-TRCT-ND` | 23,410 in stock | Selected |
| Buzzer MOSFET | `AO3400A` | `785-1000-1-ND` | 168,023 in stock | Selected |
| User button | `KMR211NG LFS` | `CKN10243CT-ND` | 44,917 in stock | Selected |
| Status LED | `LTST-C190KRKT` | `160-1436-1-ND` | 631,926 in stock | Selected |
| Resistors | Yageo `RC0603FR` 1% 0603 family | Value-specific | `RC0603FR-0710KL` observed at 9,468,329 in stock | Use same family for 100R, 1k, 3k, 5.1k, 10k, 100k, 1M as needed |
| 100 nF decoupling capacitor | Samsung `CL10B104KB8NNNC` | `1276-1000-1-ND` | 9,953,497 in stock | Selected family |
| Other ceramics | Samsung CL-series MLCCs | Value-specific | Not individually locked yet | Select exact 1 uF, 10 uF, and 220 nF parts during Atopile binding |

Main audit result: all active semiconductors, sensors, connector choices, buzzer, button, LED, and common passives are available from DigiKey.si. The only rejected current-plan part is `AP2112K-3.3TRG1`, replaced by `TLV75533PDBVR`.

## Baseline Electrical Architecture

- `USB_VBUS`: USB-C 5 V input to charger and USB VBUS sense.
- `SYS`: BQ24075 system output.
- `BAT`: protected 1S LiPo positive terminal.
- `+3V3`: TLV75533 output powering ESP32-C3, BMP581, BMI323, and optional magnetometer pads.
- `I2C_SCL`, `I2C_SDA`: shared sensor bus for BMP581, BMI323, and DNP magnetometer option.
- `USB_DP`, `USB_DM`: USB full-speed pair to ESP32-C3.
- `BUZZER_PWM`: ESP32-C3 PWM-capable GPIO to MOSFET gate.
- `USER_BTN_N`: active-low button input.
- `BAT_SENSE`: high-value battery divider to ESP32-C3 ADC-capable GPIO.
- `STATUS_LED`: low-current LED GPIO.
- `EN`, `BOOT`: required ESP32-C3 bring-up/programming access.

## Sensor Plan

Use BMP581 and BMI323 as the fitted sensor stack.

Do not fit a magnetometer for the first Atopile board. The core variometer behavior depends on pressure and vertical-motion filtering, not absolute compass heading. Without a magnetometer, yaw/heading can drift; that is acceptable for this baseline.

Keep an unpopulated future magnetometer option with:

- `+3V3`
- `GND`
- `I2C_SCL`
- `I2C_SDA`
- Optional `MAG_INT`

Place the optional magnetometer pads away from USB shield, charger, buzzer, battery current loops, steel screws, and magnets.

## Layout Constraints

- Put the ESP32-C3-MINI-1-N4X antenna at a board edge and follow Espressif keepout guidance.
- Put BMP581 near a pressure vent and away from heat, board flex, adhesive, conformal coating, and direct buzzer airflow.
- Put BMI323 near the board center in a mechanically stable area and document axis orientation.
- Keep sensor supply decoupling close to each VDD/VDDIO pin.
- Keep USB D+/D- short, impedance-conscious, and protected by ESD near the connector.
- Keep buzzer and charger return currents away from sensor ground return.
- Avoid assigning functional loads to ESP32-C3 boot strapping pins until boot behavior is checked.

## Firmware Impact

- Port board support from Arduino Nano 33 BLE Sense Rev2 / nRF52840 assumptions to ESP32-C3.
- Use ESP32-C3 BLE stack and keep transmission duty cycle low in production.
- Add direct BMP581 driver support.
- Add direct BMI323 driver support.
- Remove required magnetometer reads from the baseline firmware path.
- Rework GPIO mapping for ESP32-C3, including `BUZZER_PWM`, `USER_BTN_N`, `BAT_SENSE`, `STATUS_LED`, I2C, USB, `EN`, and `BOOT`.
- Revalidate sensor axis mapping and calibration on the actual PCB.

## Open Decisions

- Protected LiPo pack and cable polarity.
- Whether a wired piezo disc is needed in addition to the selected SMD buzzer.
- Button actuator/enclosure mechanics.
- Final ESP32-C3 GPIO map after strapping-pin review.
- Whether charger status pins need LEDs or only test pads.
- Final Atopile package/footprint sources and exact passive values.

## Atopile Build Order

1. Create Atopile project scaffold.
2. Add verified packages for ESP32-C3-MINI-1-N4X, BMP581, BMI323, BQ24075, TLV75533, USB-C, USB ESD, LiPo connector, buzzer, MOSFET, button, LED, and passives.
3. Capture power path and 3.3 V rail.
4. Capture ESP32-C3 USB, `EN`, `BOOT`, and debug access.
5. Capture BMP581 and BMI323 on shared I2C.
6. Add unpopulated magnetometer I2C pads or optional footprint.
7. Capture user I/O.
8. Assign supplier/manufacturer metadata for audit.
9. Run electrical/package checks before PCB routing.

## Source Links

- ESP32-C3-MINI-1 datasheet: https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.html
- DigiKey.si ESP32-C3-MINI-1-N4X: https://www.digikey.si/en/products/detail/espressif-systems/ESP32-C3-MINI-1-N4X/27525554
- Bosch BMP581: https://www.bosch-sensortec.com/en/products/environmental-sensors/pressure-sensors/bmp581/
- DigiKey.si BMP581: https://www.digikey.si/en/products/detail/bosch-sensortec/BMP581/16036134
- Bosch BMI323: https://www.bosch-sensortec.com/en/products/motion-sensors/imus/bmi323/
- DigiKey.si BMI323: https://www.digikey.si/en/products/detail/bosch-sensortec/BMI323/16719593
- TI BQ24075: https://www.ti.com/product/BQ24075
- DigiKey.si BQ24075RGTR: https://www.digikey.si/en/products/detail/texas-instruments/BQ24075RGTR/2047273
- DigiKey.si AP2112K-3.3TRG1, rejected due to 0 stock: https://www.digikey.si/en/products/detail/diodes-incorporated/AP2112K-3-3TRG1/4470746
- DigiKey.si TLV75533PDBVR: https://www.digikey.si/en/products/detail/texas-instruments/TLV75533PDBVR/9356541
- DigiKey.si USB4105-GF-A: https://www.digikey.si/en/products/detail/gct/USB4105-GF-A/11198441
- DigiKey.si USBLC6-2SC6: https://www.digikey.si/en/products/detail/stmicroelectronics/USBLC6-2SC6/1121688
- DigiKey.si S2B-PH-SM4-TB: https://www.digikey.si/en/products/filter/headers-male-pins/314?s=N4Ig7CBcoIYE5QIwA5EGYA0IYBcmZAAcBLJAJjLUQE4wBfOoA
- DigiKey.si CPT-9019A-SMT-TR: https://www.digikey.si/en/products/detail/same-sky-formerly-cui-devices/CPT-9019A-SMT-TR/19105220
- DigiKey.si AO3400A: https://www.digikey.si/en/products/detail/alpha-omega-semiconductor-inc/AO3400A/1855772
- DigiKey.si KMR211NG LFS: https://www.digikey.si/en/products/detail/c-k/Y78B21120FP/2176482
- DigiKey.si LTST-C190KRKT: https://www.digikey.si/en/products/detail/lite-on-inc/LTST-C190KRKT/386817
- DigiKey.si RC0603FR resistor family: https://www.digikey.si/en/products/filter/chip-resistor-surface-mount/52
- DigiKey.si CL10B104KB8NNNC: https://www.digikey.si/en/products/detail/samsung-electro-mechanics/CL10B104KB8NNNC/3886658
