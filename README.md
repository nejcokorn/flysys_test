# FlySys Hardware Plan

Updated: 2026-06-03

This folder is intentionally a planning workspace only. The next hardware build will be created from scratch in Atopile. Old EasyEDA, KiCad, generated production files, and JLC-specific draft outputs are not part of the active design.

## Goal

Build a compact FlySys variometer board with:

- BLE-first telemetry and configuration.
- Accurate pressure-based vertical-speed sensing.
- 6-axis inertial sensing for filtering/orientation support.
- LiPo charging and battery operation.
- Loud firmware-controlled audio output.
- USB mass-storage device access for logs/configuration.
- Power button, hidden BOOT/RESET recovery controls, green power LED, blue BLE pairing LED, USB, and software-first firmware update access without debug pads.

## Selected Components

| Function | Selection | Supplier note |
| --- | --- | --- |
| MCU/BLE/Wi-Fi/USBMSD | Espressif `ESP32-S3-MINI-1-N8` | Use ESP32-S3 because USBMSD needs configurable USB device support. `N8` provides 8 MB flash and is stocked; it has no PSRAM. |
| Pressure sensor | Bosch `BMP581` | Primary altitude/variometer pressure sensor. |
| 6-axis IMU | Bosch `BMI323` | Primary accelerometer/gyro. |
| Magnetometer | Not fitted | Keep unpopulated I2C pads or optional footprint for future magnetometer. |
| Charger / power path | TI `BQ24075RGTR` | 1S LiPo charger with power-path management. |
| 3.3 V regulator | TI `TLV75533PDBVR` | Replaces `AP2112K-3.3TRG1` because AP2112 was 0 stock in the DigiKey.si audit. Recheck current and thermal margin with ESP32-S3 peaks. Add local bulk capacitance near the module. |
| USB | GCT `USB4105-GF-A` + ST `USBLC6-2SC6Y` | USB-C 2.0 receptacle and automotive/AEC-Q101 USB ESD for charging, ESP32-S3 native USB, USBMSD, logs, and flashing. |
| Audio | Same Sky `CSS-J4D20-SMT-TR` + `AO3400A` N-MOSFET | Externally driven SMD magnetic transducer from the old device BOM. Drive from the 1S battery/SYS rail; keep firmware tone, carrier-duty, and envelope control. |
| User input | C&K `KMR211NG LFS` | Momentary active-low tactile switch for power/user input plus hidden BOOT and RESET service switches. Final actuator and pinhole geometry still depends on enclosure height. |
| Indicators | Lite-On `LTST-C190GKT` + `LTST-C190TBKT` | 0603 LEDs: green always-on `+3V3` power-present indicator, blue firmware-controlled BLE pairing/advertising indicator. The blue LED is driven from `SYS` with a GPIO-controlled low-side MOSFET. |
| Battery | JST `S2B-PH-SM4-TB` | 2-pin JST-PH right-angle SMD header. Confirm protected pack and cable polarity. |
| Firmware update | Application-level updater + hidden ESP32-S3 BOOT/RESET recovery | Normal users update through firmware while USB or another supported link is connected. Debug pads are not fitted; hidden BOOT+RESET remains the recovery fallback for the ESP32-S3 ROM USB bootloader. |

## DigiKey.si Availability Audit

Initial audit checked: 2026-05-31. Audio and LED changes rechecked: 2026-06-01. Stock changes quickly; recheck before ordering.

| Function | MPN | DigiKey cut-tape part | Observed availability | Status |
| --- | --- | --- | --- | --- |
| MCU/BLE/Wi-Fi/USBMSD | `ESP32-S3-MINI-1-N8` | `5407-ESP32-S3-MINI-1-N8CT-ND` | 3,843 in stock | Selected |
| Pressure sensor | `BMP581` | `828-BMP581CT-ND` | 46,324 in stock | Selected |
| 6-axis IMU | `BMI323` | `828-BMI323CT-ND` | 663 in stock | Selected |
| Charger / power path | `BQ24075RGTR` | `296-38874-1-ND` | 3,702 in stock | Selected |
| 3.3 V LDO | `TLV75533PDBVR` | `296-50411-1-ND` | 110,688 in stock | Selected |
| USB-C receptacle | `USB4105-GF-A` | `2073-USB4105-GF-ACT-ND` | 126,702 in stock | Selected |
| USB ESD | `USBLC6-2SC6Y` | `497-11882-1-ND` | 35,783 in stock | Selected automotive/AEC-Q101 part; LCSC `C2969755` |
| Battery connector | `S2B-PH-SM4-TB` | `455-S2B-PH-SM4-TBCT-ND` | 71,350 in stock | Selected |
| Loud SMD buzzer | `CSS-J4D20-SMT-TR` | `102-1198-1-ND` | 2,332 in stock | Selected old-device buzzer: externally driven magnetic transducer, 90 dB at 3.6 V, 5 cm, 80 mA, 3.1 kHz |
| N-MOSFETs | `AO3400A` | `785-1000-1-ND` | 168,023 in stock | Low-side drivers for buzzer PWM, blue BLE pairing LED switching, and power-latch control |
| Battery switch P-MOSFET | `DMP3098L-7` | `DMP3098L-7DICT-ND` | Recheck before ordering | High-side hard-off switch between battery connector and internal `BAT` rail |
| Power-start diodes | `1N4148W-7-F` | `1N4148W-FDICT-ND` | Recheck before ordering | Diode isolation for power button, battery switch gate, and charger `SYSOFF` |
| User button | `KMR211NG LFS` | `CKN10243CT-ND` | 44,917 in stock | Selected |
| Power LED | `LTST-C190GKT` | `160-LTST-C190GKTCT-ND` | 1,068,260 in stock | Selected 0603 green LED, 2.1 V typical Vf |
| BLE LED | `LTST-C190TBKT` | `160-1646-1-ND` | 92,246 in stock | Selected 0603 blue LED for BLE pairing/advertising indication, 3.3 V typical Vf |
| Resistors | Yageo `RC0603FR` 1% 0603 family | Value-specific | `RC0603FR-0710KL` observed at 9,468,329 in stock | Use same family for 100R, 1k, 3k, 5.1k, 10k, 100k, 1M as needed |
| 100 nF decoupling capacitor | Samsung `CL10B104KB8NNNC` | `1276-1000-1-ND` | 9,953,497 in stock | Selected family |
| Other ceramics | Samsung CL-series MLCCs | Value-specific | Not individually locked yet | Select exact 1 uF, 10 uF, and 220 nF parts during Atopile binding |

Main audit result: all selected active semiconductors, sensors, connector choices, audio parts, button, LED, and common passives are available from DigiKey.si.

## Baseline Electrical Architecture

- `USB_VBUS`: USB-C 5 V input to charger and USB VBUS sense divider/comparator.
- `SYS`: BQ24075 system output.
- `BAT_RAW`: protected 1S LiPo positive terminal at the connector.
- `BAT`: switched internal battery rail after the hard-off P-MOSFET.
- `+3V3`: TLV75533 output powering ESP32-S3, BMP581, BMI323, and optional magnetometer pads.
- `I2C_SCL`, `I2C_SDA`: shared sensor bus for BMP581, BMI323, and DNP magnetometer option.
- `USB_OTG_DP`, `USB_OTG_DM`: USB full-speed pair to ESP32-S3 native USB pins (`GPIO20` D+, `GPIO19` D-).
- `BUZZER_VM`: battery/SYS-powered audio rail feeding the buzzer; no boost in the baseline.
- `BUZZER_PWM`: ESP32-S3 PWM-capable GPIO to the MOSFET gate.
- `PWR_SW_N`: raw active-low power switch node.
- `PWR_BTN_N`: diode-isolated active-low button input to ESP32-S3.
- `BOOT_USER_BTN_N`: ESP32-S3 GPIO0 boot strap, pulled low by the hidden BOOT service button for ROM bootloader recovery.
- `BAT_SENSE`: high-value divider from switched `BAT` to ESP32-S3 ADC-capable GPIO; it has no DC path to `BAT_RAW` when the hard-off switch is open.
- `POWER_LED`: low-current green `+3V3` rail indicator with series resistor. It is on whenever `+3V3` is up and is not firmware-controlled.
- `BLE_LED`: low-current blue indicator for BLE pairing/advertising mode only. Firmware should drive `BLE_LED_PWM` active only while connectable BLE advertising/pairing is active and keep it low or high-Z otherwise. Because the blue LED has high forward voltage, prefer `SYS` plus a current-limit resistor and a small GPIO-controlled low-side switch instead of direct `+3V3` GPIO drive.
- `EN`, `BOOT`: hidden physical RESET and BOOT service controls for ESP32-S3 ROM bootloader recovery only.

## USBMSD / Storage Plan

USBMSD is now a baseline requirement. Use ESP32-S3 native USB OTG device mode with the ESP-IDF TinyUSB MSC class.

Route the USB-C D+/D- pair to ESP32-S3 `GPIO20`/`GPIO19`, keep the ESD part near the connector, and add a USB VBUS monitor path because this is a battery-powered, self-powered USB device.

Initial storage options:

- Internal flash FAT partition for small configuration import/export and short log files.
- External SPI flash, SPI NAND, or microSD if host-visible logs need materially more capacity or write endurance.

Do not let firmware and the USB host write the same mounted filesystem at the same time. Define a mode switch or mount arbitration before implementing firmware.

## Firmware Update UX

Normal firmware update is software-first. When USB is connected, application
firmware should expose an update path such as USB MSC drag-and-drop firmware
copy, a USB CDC update tool, BLE DFU, or OTA. The image must be validated before
activation, and firmware should use OTA partitions with rollback so a failed
image can revert automatically.

USB attach is allowed to power the ESP32-S3 electrically. If `USB_VBUS_SENSE`
shows USB present and the user has not pressed `POWER`, firmware enters
USB-attached idle mode instead of starting the vario application. In this mode,
do not start vario sensing, BLE advertising, buzzer output, logging, or normal
flight behavior. Only minimal charging/status indication, the firmware update
endpoint, and an optional command to start normal mode should run.

Pressing `POWER` while USB is connected records user intent and starts the normal
application. The hidden `BOOT` (`GPIO0`) and `RST` (`EN`) controls remain behind
service access only. Recovery sequence: connect USB-C, hold hidden `BOOT`, press
and release hidden `RST`, release `BOOT`, then flash with the ESP32-S3 native USB
ROM bootloader tool.

## Audio Plan

The buzzer must be loud enough for a paragliding vario used in open air with wind noise. Treat acoustic output as a primary requirement, not a secondary indicator.

Use an externally driven passive SMD transducer so firmware keeps control over pitch, cadence, envelope, mute profiles, and sink/climb tone patterns. Do not use an internally driven active buzzer.

Selected audio path:

- Transducer: `CSS-J4D20-SMT-TR`, externally driven magnetic SMD transducer from the old device BOM, 90 dB at 3.6 V, 5 cm, 3.1 kHz, about 80 mA at rated drive.
- Driver: `AO3400A` low-side N-MOSFET, with the buzzer powered from the 1S battery/SYS rail and the MOSFET gate driven by one ESP32-S3 PWM GPIO.

This matches the old `MX270_MiniUP` firmware model: one output-compare PWM channel generated the audio carrier, `beep->volume` changed the carrier duty, and the vario queue changed the beep envelope/cadence. Port that control model to ESP32-S3 LEDC or MCPWM.

Use the battery/SYS rail, not raw USB VBUS. A normal 1S Li-ion/LiPo pack is 4.2 V full and about 3.6-3.7 V nominal; that fits the buzzer's 3-5 V operating range. Confirm BQ24075 `SYS` behavior so the buzzer never sees an out-of-range USB-derived rail.

Drive the buzzer near its 3.1 kHz rated frequency for maximum SPL. For lower volume, prefer carrier-duty control and audible envelope control; avoid detuning far from resonance just to reduce volume. The old firmware's tone table can be reused as a behavioral reference, but final tones should be revalidated against this buzzer in the enclosure.

Add a gate resistor, gate pulldown, local bulk capacitance near the buzzer supply, and a footprint option for coil clamp/snubber parts. Keep the buzzer current loop compact and scope the first PCB for ringing and EMI while the buzzer is running.

The enclosure must include a real acoustic outlet or sound channel. Verify SPL after the PCB is installed in the actual enclosure, because the port, chamber volume, venting, clothing, helmet, and mounting orientation can dominate the result.

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

- Put the ESP32-S3-MINI-1-N8 antenna at a board edge and follow Espressif keepout guidance.
- Put BMP581 near a pressure vent and away from heat, board flex, adhesive, conformal coating, and direct buzzer airflow.
- Put BMI323 near the board center in a mechanically stable area and document axis orientation.
- Keep sensor supply decoupling close to each VDD/VDDIO pin.
- Keep USB D+/D- short, impedance-conscious, protected by ESD near the connector, and routed to ESP32-S3 `GPIO20`/`GPIO19`.
- Include USB VBUS monitoring suitable for self-powered USB device behavior.
- Give the buzzer a clear acoustic outlet; do not bury the port in a sealed or foam-covered enclosure pocket.
- Keep buzzer switching current and charger return currents away from sensor ground return.
- Avoid assigning functional loads to ESP32-S3 boot strapping pins, USB pins, and flash/PSRAM-reserved pins until boot behavior and the exact module variant are checked.

## Firmware Impact

- Port board support from Arduino Nano 33 BLE Sense Rev2 / nRF52840 assumptions to ESP32-S3.
- Use ESP32-S3 BLE stack and keep transmission duty cycle low in production.
- Add USBMSD using ESP-IDF TinyUSB MSC over ESP32-S3 native USB OTG.
- Define the USBMSD storage backend and host-visible filesystem.
- Prevent concurrent writes between firmware logging/config code and the mounted USB host filesystem.
- Decide whether USB presents MSC only, CDC+MSC composite, or a boot/mode-selected function.
- Add software-first firmware update handling with image validation and OTA partition rollback.
- On USB attach from off state, enter USB-attached idle mode until `PWR_BTN_N` is pressed or a supported start command is received.
- In USB-attached idle mode, keep vario sensing, BLE normal operation, buzzer output, and logging inactive.
- Add direct BMP581 driver support.
- Add direct BMI323 driver support.
- Remove required magnetometer reads from the baseline firmware path.
- Rework GPIO mapping for ESP32-S3, including `BUZZER_PWM`, `PWR_BTN_N`, `PWR_HOLD`, `BAT_SENSE`, `BLE_LED_PWM`, I2C, USB, `EN`, and `BOOT`.
- Add configurable audio profiles for vario use: climb cadence, sink alarm, mute, startup check, and volume/power-saving modes.
- Port the old single-PWM buzzer model, then retune frequency and volume tables around the `CSS-J4D20-SMT-TR` response on the new PCB.
- Revalidate sensor axis mapping and calibration on the actual PCB.

## Open Decisions

- Protected LiPo pack and cable polarity.
- USBMSD storage backend: internal flash FAT partition vs external flash/NAND/microSD.
- USB device mode policy: MSC only, CDC+MSC composite, boot/mode-selected function, and the exact software update endpoint.
- Final volume-control policy: envelope levels, quiet mode, and startup volume.
- Enclosure acoustic outlet, port orientation, and measured SPL after installation.
- Button actuator/enclosure mechanics.
- Final ESP32-S3 GPIO map after strapping-pin, USB-pin, and reserved-pin review.
- Whether `ESP32-S3-MINI-1-N8` without PSRAM is sufficient for the final USBMSD firmware.
- TLV75533 current and thermal margin with ESP32-S3 RF peaks and USB-attached operation.
- Whether charger status pins need LEDs or only test pads.
- Final Atopile package/footprint sources and exact passive values.

## Atopile Build Order

1. Create Atopile project scaffold.
2. Add verified packages for ESP32-S3-MINI-1-N8, BMP581, BMI323, BQ24075, TLV75533, USB-C, USB ESD, LiPo connector, CSS-J4D20 buzzer, MOSFET driver, button, green power LED, blue BLE pairing LED, and passives.
3. Capture power path and 3.3 V rail.
4. Capture ESP32-S3 native USB OTG, USB VBUS sense, `EN`, `BOOT`, and hidden service bootloader buttons.
5. Capture BMP581 and BMI323 on shared I2C.
6. Add unpopulated magnetometer I2C pads or optional footprint.
7. Add the selected USBMSD storage backend if external storage is selected.
8. Capture loud audio and user I/O.
9. Assign supplier/manufacturer metadata for audit.
10. Run electrical/package checks before PCB routing.

## Atopile Project Status

Atopile is now the active project source in this repo:

- `ato.yaml`: Atopile 0.15.7 project config.
- `main.ato`: FlySysVario schematic source and Atopile `RectangularBoardShape` board outline.
- `parts/`: generated and local part definitions, including local draft footprints for battery, buzzer, MOSFETs, signal diodes, buttons, and optional magnetometer pads.
- `layouts/default/default.kicad_pcb`: Atopile-generated layout artifact used by the Atopile Autolayout panel.
- `docs/components-and-placement.md`: component map, passive explanations, and placement intent.

Current modeled nets include USB-C, USB ESD, BQ24075 power path, P-MOS battery hard-off switch, TLV75533 3.3 V rail, ESP32-S3 native USB, I2C sensor bus, BMP581, BMI323, battery connector, switched battery/USB sense dividers, buzzer MOSFET driver, always-on green power LED, blue BLE pairing LED low-side switch, power/user button, hidden BOOT and RESET service buttons, and optional future magnetometer pads. See `docs/firmware-update-ux.md` for the software-first update flow and recovery fallback.

`ato --non-interactive build` completes the current Atopile workflow. The 90 mm x 45 mm board outline is defined in `main.ato` with `RectangularBoardShape`, so the Atopile Autolayout panel has a board boundary to place and route against. The remaining warnings are expected for local or DigiKey-only parts because the current picker support is not covering those local packages. Before production, verify the local draft footprints for `S2B-PH-SM4-TB`, `CSS-J4D20-SMT-TR`, `AO3400A`, `DMP3098L`, `1N4148W`, `KMR211NG LFS`, and optional magnetometer pads against manufacturer land patterns and enclosure mechanics.

## Source Links

- Atopile project structure: https://docs.atopile.io/atopile-0.14.x/essentials/5-project-structure
- Atopile language reference: https://docs.atopile.io/atopile-0.14.x/essentials/1-the-ato-language
- ESP32-S3-MINI-1 datasheet: https://documentation.espressif.com/esp32-s3-mini-1_mini-1u_datasheet_en.html
- DigiKey.si ESP32-S3-MINI-1-N8: https://www.digikey.si/en/products/detail/espressif-systems/ESP32-S3-MINI-1-N8/15295890
- ESP-IDF ESP32-S3 USB Device Stack / TinyUSB MSC: https://docs.espressif.com/projects/esp-usb/en/latest/esp32s3/usb_device.html
- ESP-IDF ESP32-C3 USB Serial/JTAG fixed-function note: https://docs.espressif.com/projects/esp-idf/en/release-v5.2/esp32c3/api-guides/usb-serial-jtag-console.html
- Bosch BMP581: https://www.bosch-sensortec.com/en/products/environmental-sensors/pressure-sensors/bmp581/
- Bosch BMP581 datasheet / land pattern: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf
- DigiKey.si BMP581: https://www.digikey.si/en/products/detail/bosch-sensortec/BMP581/16036134
- Bosch BMI323: https://www.bosch-sensortec.com/en/products/motion-sensors/imus/bmi323/
- DigiKey.si BMI323: https://www.digikey.si/en/products/detail/bosch-sensortec/BMI323/16719593
- TI BQ24075: https://www.ti.com/product/BQ24075
- DigiKey.si BQ24075RGTR: https://www.digikey.si/en/products/detail/texas-instruments/BQ24075RGTR/2047273
- DigiKey.si TLV75533PDBVR: https://www.digikey.si/en/products/detail/texas-instruments/TLV75533PDBVR/9356541
- DigiKey.si USB4105-GF-A: https://www.digikey.si/en/products/detail/gct/USB4105-GF-A/11198441
- DigiKey.si USBLC6-2SC6Y: https://www.digikey.si/en/products/detail/stmicroelectronics/USBLC6-2SC6Y/2819177
- DigiKey.si S2B-PH-SM4-TB: https://www.digikey.si/en/products/filter/headers-male-pins/314?s=N4Ig7CBcoIYE5QIwA5EGYA0IYBcmZAAcBLJAJjLUQE4wBfOoA
- DigiKey.si CSS-J4D20-SMT-TR: https://www.digikey.si/en/products/detail/same-sky-formerly-cui-devices/CSS-J4D20-SMT-TR/504819
- DigiKey.si AO3400A: https://www.digikey.si/en/products/detail/alpha-omega-semiconductor-inc/AO3400A/1855772
- DigiKey.si KMR211NG LFS: https://www.digikey.si/en/products/detail/c-k/Y78B21120FP/2176482
- DigiKey.si LTST-C190GKT: https://www.digikey.si/en/products/detail/lite-on-inc/LTST-C190GKT/269230
- DigiKey.si LTST-C190TBKT: https://www.digikey.si/en/products/detail/lite-on-inc/LTST-C190TBKT/388529
- DigiKey.si RC0603FR resistor family: https://www.digikey.si/en/products/filter/chip-resistor-surface-mount/52
- DigiKey.si CL10B104KB8NNNC: https://www.digikey.si/en/products/detail/samsung-electro-mechanics/CL10B104KB8NNNC/3886658
