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
| 3.3 V regulator | `AP2112K-3.3TRG1` or equivalent 600 mA LDO | ESP32-C3 radio transmission will be kept minimal in production. Add local bulk capacitance near the module. |
| USB | USB-C 2.0 receptacle + USB ESD | Used for charging, USB Serial/JTAG, logs, and flashing. |
| Audio | Passive piezo + low-side N-MOSFET | Keep optional wired piezo pads if enclosure volume is insufficient. |
| User input | Momentary active-low button | Final switch depends on enclosure height. |
| Battery | Protected 1S LiPo connector | Exact connector and polarity to be finalized with enclosure/battery choice. |
| Debug | ESP32-C3 USB Serial/JTAG, `EN`, `BOOT`, optional UART0 pads | ESP32-C3 does not use SWD. |

## Baseline Electrical Architecture

- `USB_VBUS`: USB-C 5 V input to charger and USB VBUS sense.
- `SYS`: BQ24075 system output.
- `BAT`: protected 1S LiPo positive terminal.
- `+3V3`: AP2112 output powering ESP32-C3, BMP581, BMI323, and optional magnetometer pads.
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

- Exact USB-C connector and USB ESD part.
- Exact battery connector and protected LiPo pack.
- Exact buzzer and whether a wired piezo disc is needed.
- Button height and enclosure mechanics.
- Final ESP32-C3 GPIO map after strapping-pin review.
- Whether charger status pins need LEDs or only test pads.
- Final Atopile package/footprint sources for each selected component.

## Atopile Build Order

1. Create Atopile project scaffold.
2. Add verified packages for ESP32-C3-MINI-1-N4X, BMP581, BMI323, BQ24075, AP2112, USB-C, USB ESD, LiPo connector, buzzer, MOSFET, button, LED, and passives.
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
- DigiKey.si AP2112K-3.3TRG1: https://www.digikey.si/en/products/detail/diodes-incorporated/AP2112K-3-3TRG1/4470746
