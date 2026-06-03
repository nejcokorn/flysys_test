# FlySys Schematic Description

Updated: 2026-06-03

This document describes the KiCad schematic in text form. The schematic file is
`kicad/flysys_vario.kicad_sch`; the Atopile source net plan is `main.ato`.

## Functional Blocks

FlySys is a small BLE/USB variometer board built around `U4`, an
`ESP32-S3-MINI-1-N8` module. Power enters from USB-C at `USB1` or from a LiPo
battery at `J1`. `U1` manages LiPo charging and the system power path, `U3`
generates the regulated `+3V3` rail, `U5` measures pressure for altitude/vario
data, `U2` provides IMU motion data, and `BZ1` gives loud acoustic feedback.

The board uses the following main nets:

| Net | Meaning |
| --- | --- |
| `USB_VBUS` | 5 V from USB-C connector. Feeds charger input and USB VBUS sense divider. |
| `BAT_RAW` | LiPo battery positive terminal at `J1`, before the hard-off battery switch. |
| `BAT` | Switched internal battery rail after `Q4`. Feeds charger battery pin and battery ADC divider only while the battery switch is on. |
| `SYS` | Charger power-path output. Feeds 3.3 V regulator and high-current buzzer/blue LED loads when the system is on. |
| `+3V3` | Regulated logic rail for ESP32-S3, sensors, pull-ups, and the green power LED. |
| `CHG_SYSOFF` | BQ24075 ship-mode control. High disconnects battery from `SYS`; low enables battery-to-`SYS` operation. |
| `PWR_SW_N` | Raw active-low power button node from `SW1`, isolated from MCU and latch nodes by diodes. |
| `PWR_BTN_N` | Isolated active-low power/user button input read by the MCU on GPIO7. |
| `USB_VBUS_SENSE` | Divided USB VBUS monitor read by the MCU on GPIO2. Firmware uses it to detect USB-attached idle/update mode. |
| `PWR_HOLD` | MCU GPIO10 output that can release the self-latching power circuit by driving `PWR_HOLD_GATE` low. |
| `BAT_SWITCH_GATE` | Gate of the battery high-side P-channel MOSFET `Q4`. |
| `GND` | Common ground and USB shield reference. |

## USB-C And ESD

`USB1` is the USB-C device connector. `CC1` and `CC2` are each pulled down to
ground by `R9` and `R10`, both 5.1 kohm, so the board presents itself as a USB
device/sink.

USB data exits the connector as `USB_DP_CONN` and `USB_DM_CONN`, passes through
`D1` (`USBLC6-2SC6Y`) for ESD protection, then continues to the ESP32-S3 as
`USB_OTG_DP` and `USB_OTG_DM`. `D1` must stay physically between `USB1` and
`U4`, close to the connector, so ESD current is shunted before it reaches the
MCU.

The USB-C shell/mechanical pads are tied to `GND`. The local USB footprint maps
all shell pads to the same symbol pin so KiCad does not leave shield pads
unconnected during PCB update.

## Charger And Power Path

`U1` (`BQ24075RGTR`) receives `USB_VBUS` on `IN`, connects to the switched
internal battery rail on `BAT`, and produces the system rail on `OUT`/`SYS`.
The charger is enabled by tying `nCE` low. `EN1`, `EN2`, `TS`, `ISET`, `ILIM`,
and `TMR` are configured with fixed resistors, so the current limits and timer
behavior are set in hardware.

`Q4` (`DMP3098L`) is a high-side P-channel MOSFET between `BAT_RAW` and `BAT`.
`R28` pulls `BAT_SWITCH_GATE` up to `BAT_RAW`, so the default battery-only state
physically disconnects the battery from the BQ24075 `BAT` pin and from the
`BAT_SENSE` divider. In this state the board has no intentional DC battery load;
only MOSFET/diode leakage remains.

`SYSOFF` is still used as the BQ24075 power-path off control. `R23` pulls
`CHG_SYSOFF` up to the switched `BAT` rail, while `Q3` pulls it low when the
power latch is active. Pressing `SW1` grounds `PWR_SW_N`; `D3` pulls
`BAT_SWITCH_GATE` low to turn `Q4` on, and `D4` pulls `CHG_SYSOFF` low so
`SYS` turns on from the battery. Once `+3V3` is up, `R24` pulls
`PWR_HOLD_GATE` high and turns on both `Q3` and `Q5`, which latches
`CHG_SYSOFF` and `BAT_SWITCH_GATE` low after `SW1` is released. `R26` keeps the
latch off before `+3V3` is present.

Firmware can shut the board down from battery power by driving GPIO10
(`PWR_HOLD`) low through `R25`; this turns off `Q3` and `Q5`, after which `R23`
and `R28` return the charger and battery switch to their off states. During
normal operation and during the ESP32-S3 ROM bootloader, `PWR_HOLD` may remain
high impedance because `R24` provides the hardware hold.

When USB is present, the BQ24075 can still power `SYS` from `USB_VBUS`. Firmware
should keep the latch active while battery charging is desired so `Q4` is on and
the BQ24075 `BAT` pin is connected to the pack.

`nCHG` and `nPGOOD` are open-drain charger status outputs. `R13` and `R19` pull
them up to `+3V3`, and the MCU reads them on GPIOs. These nets should not be
pulled to `SYS` because the ESP32-S3 GPIOs are 3.3 V only.

`J1` is the 2-pin LiPo connector. `BAT_POS` goes to `BAT_RAW`, and `BAT_NEG`
goes to `GND`. The final build must confirm connector polarity against the
actual battery harness before ordering or assembly.

## 3.3 V Regulation

`U3` (`TLV75533PDBVR`) converts `SYS` into `+3V3`. The regulator enable pin is
tied to `SYS`, so the 3.3 V rail is on whenever `SYS` is present. On battery
power, `SYS` is present only after `CHG_SYSOFF` is pulled low by `SW1` or `Q3`.

`+3V3` powers the ESP32-S3 module, BMP581 pressure sensor, BMI323 IMU, I2C
pull-ups, charger status pull-ups, the always-on green power LED, and
button/latch pull-ups.

## ESP32-S3 MCU

`U4` is the main controller. It uses native USB through `USB_OTG_DP` and
`USB_OTG_DM`, reads battery and USB voltage dividers, reads charger status, runs
the I2C sensor bus, drives the buzzer PWM MOSFET, and drives the BLE
pairing/advertising LED MOSFET.

`EN` has a 10 kohm pull-up (`R16`) and 100 nF capacitor (`C4`) for a simple reset
RC network. `SW3` pulls `EN` low for a hidden service reset button labeled
`RST` on the PCB.

`BOOT_USER_BTN_N` is pulled up by `R6` and pulled low by `SW2`. `SW2` is a
hidden service `BOOT` button, not a normal user update control. To enter the
ESP32-S3 ROM USB bootloader for recovery, connect USB-C, hold `SW2` (`BOOT`),
press and release `SW3` (`RST`), then release `BOOT`. If a service setup must
keep the board powered from battery before USB is attached, press `SW1` first to
latch power; recovery flashing still requires USB. No debug pads are fitted.

`SW1` is the active-low power button on `PWR_SW_N`. `D2` lets the MCU read this
button as `PWR_BTN_N` on GPIO7 while preventing `BAT_RAW` or latch nodes from
feeding the unpowered MCU in hard-off.

## Firmware Update And USB-Attached Idle UX

Normal firmware update is software-first. Application firmware should expose an
update endpoint such as USB MSC drag-and-drop, USB CDC update tooling, BLE DFU,
or OTA. Firmware must validate the image before activating it and should use OTA
partitions with rollback so a failed update returns to the previous working
image.

USB attach is allowed to power the ESP32-S3 electrically through the charger
power path. On boot, firmware must read `USB_VBUS_SENSE` and the current or
persisted power-intent state. If USB is present and the user has not pressed
`POWER`, firmware enters USB-attached idle mode rather than starting the vario
application.

In USB-attached idle mode, firmware must not start pressure/IMU vario sensing,
BLE advertising or normal telemetry, buzzer output, flight logging, or normal
flight behavior. Only minimal charging/status indication, the firmware update
endpoint, and an optional command to start normal mode should run. Pressing
`SW1` drives `PWR_BTN_N` low; firmware records this user intent and starts the
normal application.

The hidden `BOOT` + `RST` sequence remains the documented recovery fallback only
when the application updater is unavailable or application firmware is broken.
See `docs/firmware-update-ux.md` for the service flow and verification plan.

## Sensor Bus

`U5` (`BMP581`) and `U2` (`BMI323`) share the I2C bus:

| Net | MCU | Loads |
| --- | --- | --- |
| `I2C_SCL` | ESP32-S3 GPIO8 | `U5 SCK`, `U2 SCX`, pull-up `R17` |
| `I2C_SDA` | ESP32-S3 GPIO9 | `U5 SDI`, `U2 SDX`, pull-up `R18` |

Both pull-ups are 4.7 kohm to `+3V3`. `BMP581 SDO` and `BMI323 SDO` are tied to
ground to select their I2C addresses. Their chip-select pins are tied high so
the devices remain in I2C mode. Sensor interrupt pins are routed to ESP32 GPIOs
for firmware use.

## Buzzer Driver

`BZ1` is powered from `SYS`, not from `+3V3`, so it can use the higher available
system voltage and avoid loading the LDO. `Q1` (`AO3400A`) is a low-side
N-channel MOSFET controlled by ESP32 PWM through `R8`. `R7` pulls the MOSFET
gate down so the buzzer stays off while the MCU is reset or booting.

The buzzer current loop is `SYS -> BZ1 -> Q1 -> GND`. This loop must be compact
and kept away from the pressure sensor and I2C lines.

## LEDs

`LED2` is the green power LED. It is powered from `+3V3` through `R20`, then
returns directly to `GND`. It is a power-present indicator and is on whenever
`+3V3` is up; firmware does not control it.

`LED1` is the blue BLE pairing LED. It is powered from `SYS` through `R5` and
switched by `Q2`, another low-side `AO3400A`. `R4` is the series gate resistor,
and `R3` is the gate pulldown. This keeps the LED off while the ESP32-S3 GPIO is
high impedance. Firmware should drive `BLE_LED_PWM` active only while BLE
pairing/connectable advertising mode is active, and keep it low or high-Z
otherwise.

## Capacitors And Their Roles

| Ref | Value | Net | Role |
| --- | --- | --- | --- |
| `C14` | 1 uF | `USB_VBUS` to `GND` | USB input decoupling. It supplies short input-current pulses and should sit close to `USB1`/`U1 IN`. |
| `C1` | 10 uF | `BAT` to `GND` | Switched battery rail bulk capacitance. It stabilizes the charger battery pin after `Q4` is on. |
| `C13` | 10 uF | `SYS` to `GND` | Main system rail bulk. It helps the charger power-path output handle load changes from the LDO and buzzer. |
| `C7` | 1 uF | `SYS` to `GND` | LDO input capacitor. It must be placed at `U3 IN/GND` to keep the regulator stable. |
| `C8` | 1 uF | `+3V3` to `GND` | LDO output capacitor. It must be placed at `U3 OUT/GND` to meet regulator stability requirements. |
| `C9` | 10 uF | `+3V3` to `GND` | ESP32-S3 local bulk capacitor. It supports RF and CPU current bursts. |
| `C10` | 100 nF | `+3V3` to `GND` | ESP32-S3 high-frequency decoupling. It should be very close to the module power pin. |
| `C12` | 100 nF | `BMP581 VDD` to `GND` | Pressure sensor core decoupling. Place next to `U5`. |
| `C11` | 100 nF | `BMP581 VDDIO` to `GND` | Pressure sensor I/O decoupling. Place next to `U5`. |
| `C6` | 100 nF | `BMI323 VDD` to `GND` | IMU core decoupling. Place next to `U2`. |
| `C5` | 100 nF | `BMI323 VDDIO` to `GND` | IMU I/O decoupling. Place next to `U2`. |
| `C3` | 10 uF | `SYS` to `GND` | Local buzzer reservoir. Place close to `BZ1` and `Q1` so buzzer current does not disturb the rest of `SYS`. |
| `C4` | 100 nF | `EN` to `GND` | ESP32-S3 enable/reset RC capacitor with `R16`. Place close to `U4 EN`. |
| `C2` | 100 nF | `BAT_SENSE` to `GND` | ADC filter for the switched-battery divider midpoint. Place near `R1`/`R2` and the MCU ADC input. |

## No-Connect Rules

Every intentionally unused schematic pin must be marked as no-connect in KiCad.
Do not silently leave an unused pin without either a net label or a no-connect
marker.

`NC` means no copper connection: do not tie the pin to `GND`, `+3V3`, `SYS`, or
any other net unless the datasheet explicitly asks for it. Do not add test pads
to `NC` pins unless the schematic is updated to document that future option.

For this design, the intentionally unused pins are:

| Component | Pins | Required treatment |
| --- | --- | --- |
| `USB1` | `A8`, `B8` | USB-C SBU pins are unused. Leave floating and mark no-connect. |
| `U3` | `4` | TLV75533 `NC` pin. Leave floating and mark no-connect. |
| `U4` | `7`, `15`, `16`, `17`, `18`, `19`, `20`, `25`, `26`, `27`, `28`, `29`, `30`, `31`, `32`, `35`, `36`, `37`, `38`, `39`, `40`, `41`, `44` | Unused ESP32-S3 GPIO/module pins. Leave floating and mark no-connect. Do not tie unused GPIOs to rails in hardware. |
| `U2` | `2`, `3`, `10`, `11` | BMI323 datasheet NC pins. Leave floating and mark no-connect. |

The USB-C shell pads are not `NC`; they are part of the connector shield and are
tied to `GND`.

## Component Pin Connection Instructions

The tables below define what every component pin must connect to in the
schematic and PCB. `NC` rows follow the no-connect rules above.

### Connectors And Protection

| Ref | Pin | Pin name | Connect to | Instruction |
| --- | --- | --- | --- | --- |
| `USB1` | `1` | `EH` | `GND` | USB-C shell/edge hardware ground. All shell mounting pads in the footprint are mapped to this grounded pin. |
| `USB1` | `A1`, `A12`, `B1`, `B12` | `GND` | `GND` | Connector signal grounds. Tie directly to the ground plane. |
| `USB1` | `A4`, `A9`, `B4`, `B9` | `VBUS` | `USB_VBUS` | USB 5 V input. Route to `U1 IN`, `D1 VBUS`, `C14`, and USB VBUS sense divider. |
| `USB1` | `A5` | `CC1` | `CC1` | Connect only to `R9`, then to `GND`. |
| `USB1` | `B5` | `CC2` | `CC2` | Connect only to `R10`, then to `GND`. |
| `USB1` | `A6`, `B6` | `DP1`, `DP2` | `USB_DP_CONN` | Connector-side USB D+. Route to `D1` first. |
| `USB1` | `A7`, `B7` | `DN1`, `DN2` | `USB_DM_CONN` | Connector-side USB D-. Route to `D1` first. |
| `USB1` | `A8`, `B8` | `SBU1`, `SBU2` | `NC` | Leave floating; this board does not use USB-C alternate modes. |
| `D1` | `1` | `IO1_A` | `USB_DP_CONN` | Connector-side D+ input to ESD device. |
| `D1` | `2` | `GND` | `GND` | Short ESD return to ground. |
| `D1` | `3` | `IO2_A` | `USB_DM_CONN` | Connector-side D- input to ESD device. |
| `D1` | `4` | `IO2_B` | `USB_OTG_DM` | MCU-side D- output from ESD device. |
| `D1` | `5` | `VBUS` | `USB_VBUS` | ESD reference to USB VBUS. |
| `D1` | `6` | `IO1_B` | `USB_OTG_DP` | MCU-side D+ output from ESD device. |
| `J1` | `1` | `BAT+` | `BAT_RAW` | LiPo positive terminal before the hard-off battery switch. Confirm pack polarity before assembly. |
| `J1` | `2` | `BAT-` | `GND` | LiPo negative terminal. |

### Power Management

| Ref | Pin | Pin name | Connect to | Instruction |
| --- | --- | --- | --- | --- |
| `U1` | `1` | `TS` | `CHG_TS` | Connect to `R15` then `GND`. This is the fixed TS bias for no pack thermistor. |
| `U1` | `2`, `3` | `BAT` | `BAT` | Battery charger node. Keep short to `J1` and `C1`. |
| `U1` | `4` | `nCE` | `GND` | Charger enabled. |
| `U1` | `5` | `EN2` | `SYS` | Charger input-current mode strap. |
| `U1` | `6` | `EN1` | `GND` | Charger input-current mode strap. |
| `U1` | `7` | `nPGOOD` | `nPGOOD` | Open-drain status output. Pull up through `R19` to `+3V3`; also route to `U4`. |
| `U1` | `8` | `VSS` | `GND` | Ground. |
| `U1` | `9` | `nCHG` | `nCHG` | Open-drain charge status output. Pull up through `R13` to `+3V3`; also route to `U4`. |
| `U1` | `10`, `11` | `OUT` | `SYS` | Charger system output. Keep wide to `U3`, `C13`, buzzer, and LED load. |
| `U1` | `12` | `ILIM` | `CHG_ILIM` | Connect to `R11` then `GND`. |
| `U1` | `13` | `IN` | `USB_VBUS` | USB input power. Keep short to `USB1` and `C14`. |
| `U1` | `14` | `TMR` | `CHG_TMR` | Connect to `R14` then `GND`. |
| `U1` | `15` | `SYSOFF` | `CHG_SYSOFF` | Ship-mode control. High disconnects battery from `SYS`; low enables battery-to-`SYS` operation. |
| `U1` | `16` | `ISET` | `CHG_ISET` | Connect to `R12` then `GND`. |
| `U1` | `17` | `EP` | `GND` | Exposed pad. Stitch to ground plane for thermal and electrical return. |
| `Q4` | `1` | `G` | `BAT_SWITCH_GATE` | P-channel battery switch gate. Pull high to `BAT_RAW` for off, pull low to connect `BAT_RAW` to `BAT`. |
| `Q4` | `2` | `S` | `BAT_RAW` | P-channel source to raw battery connector positive. |
| `Q4` | `3` | `D` | `BAT` | P-channel drain to switched internal battery rail. |
| `Q5` | `1` | `G` | `PWR_HOLD_GATE` | N-channel gate driven by the hardware hold node. |
| `Q5` | `2` | `S` | `GND` | Low-side switch source. |
| `Q5` | `3` | `D` | `BAT_SWITCH_GATE` | Pulls `Q4` gate low while the power latch is active. |
| `U3` | `1` | `IN` | `SYS` | LDO input. Place `C7` at this pin. |
| `U3` | `2` | `GND` | `GND` | LDO ground. |
| `U3` | `3` | `EN` | `SYS` | LDO enabled whenever `SYS` is present. |
| `U3` | `4` | `NC` | `NC` | Leave floating and mark no-connect. |
| `U3` | `5` | `OUT` | `+3V3` | Regulated logic rail. Place `C8` at this pin. |

### ESP32-S3 Module

| Ref | Pin | Pin name | Connect to | Instruction |
| --- | --- | --- | --- | --- |
| `U4` | `1`, `2`, `42`, `43`, `46`, `47`, `48`, `49`, `50`, `51`, `52`, `53`, `54`, `55`, `56`, `57`, `58`, `59`, `60`, `GND` | `GND` | `GND` | Tie all module grounds to the ground plane. Do not leave any ground pad isolated. |
| `U4` | `3` | `3V3` | `+3V3` | Main module supply. Place `C9` and `C10` close to the module. |
| `U4` | `4` | `IO0` | `BOOT_USER_BTN_N` | Boot-mode strap/recovery net with pull-up `R6`; not connected to `SW1`. |
| `U4` | `5` | `IO1` | `BAT_SENSE` | Battery ADC sense divider midpoint with filter `C2`. |
| `U4` | `6` | `IO2` | `USB_VBUS_SENSE` | USB VBUS ADC sense divider midpoint. Firmware uses this to enter USB-attached idle/update mode. |
| `U4` | `7` | `IO3` | `NC` | Leave floating and mark no-connect. |
| `U4` | `8` | `IO4` | `BMP581_INT` | Pressure sensor interrupt input. |
| `U4` | `9` | `IO5` | `BMI323_INT1` | IMU interrupt input 1. |
| `U4` | `10` | `IO6` | `BMI323_INT2` | IMU interrupt input 2. |
| `U4` | `11` | `IO7` | `PWR_BTN_N` | Active-low power/user button input from `SW1`. |
| `U4` | `12` | `IO8` | `I2C_SCL` | I2C clock with pull-up `R17`. |
| `U4` | `13` | `IO9` | `I2C_SDA` | I2C data with pull-up `R18`. |
| `U4` | `14` | `IO10` | `PWR_HOLD` | Power-hold release output. Leave high-Z/high for normal hold; drive low to shut down from battery. |
| `U4` | `15`, `16`, `17`, `18`, `19`, `20` | `IO11` to `IO16` | `NC` | Leave floating and mark no-connect. |
| `U4` | `21` | `IO17` | `BUZZER_PWM` | PWM output to `Q1` through `R8`. |
| `U4` | `22` | `IO18` | `BLE_LED_PWM` | BLE pairing/advertising LED control output to `Q2` through `R4`. |
| `U4` | `23` | `IO19` | `USB_OTG_DM` | Native USB D-. Route as controlled short USB pair with pin 24. |
| `U4` | `24` | `IO20` | `USB_OTG_DP` | Native USB D+. Route as controlled short USB pair with pin 23. |
| `U4` | `25`, `26`, `27`, `28`, `29`, `30`, `31`, `32` | `IO21`, `IO26`, `IO47`, `IO33`, `IO34`, `IO48`, `IO35`, `IO36` | `NC` | Leave floating and mark no-connect. |
| `U4` | `33` | `IO37` | `nCHG` | Charger status input from `U1`, pulled up to `+3V3` by `R13`. |
| `U4` | `34` | `IO38` | `nPGOOD` | Charger power-good input from `U1`, pulled up to `+3V3` by `R19`. |
| `U4` | `35`, `36`, `37`, `38` | `IO39` to `IO42` | `NC` | Leave floating and mark no-connect. |
| `U4` | `39` | `TXD0` | `NC` | Debug pads are not fitted. Leave floating and mark no-connect. |
| `U4` | `40` | `RXD0` | `NC` | Debug pads are not fitted. Leave floating and mark no-connect. |
| `U4` | `41` | `IO45` | `NC` | Leave floating and mark no-connect. |
| `U4` | `44` | `IO46` | `NC` | Leave floating and mark no-connect; do not drive this strapping-sensitive GPIO high during reset. |
| `U4` | `45` | `EN` | `EN` | Module enable/reset net with `R16` pull-up and `C4` to ground. |

### Sensors

| Ref | Pin | Pin name | Connect to | Instruction |
| --- | --- | --- | --- | --- |
| `U5` | `1` | `VDDIO` | `+3V3` | Pressure sensor I/O supply. Decouple with `C11`. |
| `U5` | `2` | `SCK` | `I2C_SCL` | I2C clock. |
| `U5` | `3`, `8`, `9` | `VSS` | `GND` | Pressure sensor grounds. |
| `U5` | `4` | `SDI` | `I2C_SDA` | I2C data. |
| `U5` | `5` | `SDO` | `GND` | I2C address strap. |
| `U5` | `6` | `CSB` | `+3V3` | I2C mode strap. |
| `U5` | `7` | `INT` | `BMP581_INT` | Interrupt output to `U4.8`. |
| `U5` | `10` | `VDD` | `+3V3` | Pressure sensor core supply. Decouple with `C12`. |
| `U2` | `1` | `SDO` | `GND` | I2C address strap. |
| `U2` | `2`, `3`, `10`, `11` | `NC` | `NC` | Leave floating and mark no-connect. |
| `U2` | `4` | `INT1` | `BMI323_INT1` | Interrupt output to `U4.9`. |
| `U2` | `5` | `VDDIO` | `+3V3` | IMU I/O supply. Decouple with `C5`. |
| `U2` | `6` | `GNDIO` | `GND` | IMU I/O ground. |
| `U2` | `7` | `GND` | `GND` | IMU core ground. |
| `U2` | `8` | `VDD` | `+3V3` | IMU core supply. Decouple with `C6`. |
| `U2` | `9` | `INT2` | `BMI323_INT2` | Interrupt output to `U4.10`. |
| `U2` | `12` | `CSB` | `+3V3` | I2C mode strap. |
| `U2` | `13` | `SCX` | `I2C_SCL` | I2C clock. |
| `U2` | `14` | `SDX` | `I2C_SDA` | I2C data. |

### User Interface And Drivers

| Ref | Pin | Pin name | Connect to | Instruction |
| --- | --- | --- | --- | --- |
| `SW1` | `1`, `2` | `A` | `PWR_SW_N` | Button side connected to raw active-low power switch net. |
| `SW1` | `3`, `4` | `B` | `GND` | Button side connected to ground. |
| `SW2` | `1`, `2` | `A` | `BOOT_USER_BTN_N` | Hidden service BOOT button side connected to ESP32-S3 GPIO0 strap. |
| `SW2` | `3`, `4` | `B` | `GND` | BOOT button pulls GPIO0 low for ROM bootloader recovery entry. |
| `SW3` | `1`, `2` | `A` | `EN` | Hidden service RESET/RST button side connected to ESP32-S3 enable/reset net. |
| `SW3` | `3`, `4` | `B` | `GND` | RST button pulls `EN` low. |
| `BZ1` | `1` | `+` | `SYS` | Buzzer positive terminal. Keep current path local to `C3`. |
| `BZ1` | `2` | `-` | `BUZZER_NEG` | Buzzer switched return to `Q1.3`. |
| `Q1` | `1` | `G` | `BUZZER_GATE` | Gate drive from `R8`, pulldown by `R7`. |
| `Q1` | `2` | `S` | `GND` | Low-side switch source. |
| `Q1` | `3` | `D` | `BUZZER_NEG` | Low-side switch drain to buzzer negative terminal. |
| `Q2` | `1` | `G` | `BLE_LED_GATE` | Gate drive from `R4`, pulldown by `R3`. |
| `Q2` | `2` | `S` | `GND` | Low-side switch source. |
| `Q2` | `3` | `D` | `BLE_LED_K` | Low-side switch drain to blue BLE pairing LED cathode. |
| `Q3` | `1` | `G` | `PWR_HOLD_GATE` | Gate drive from the hardware hold node. |
| `Q3` | `2` | `S` | `GND` | Low-side switch source. |
| `Q3` | `3` | `D` | `CHG_SYSOFF` | Pulls BQ24075 `SYSOFF` low while the power latch is active. |
| `D2` | `1` | `K` | `PWR_SW_N` | Isolates the raw power switch node from the MCU button input. |
| `D2` | `2` | `A` | `PWR_BTN_N` | Lets `SW1` pull the MCU button input low when the board is on. |
| `D3` | `1` | `K` | `PWR_SW_N` | Lets `SW1` pull `BAT_SWITCH_GATE` low during power-on. |
| `D3` | `2` | `A` | `BAT_SWITCH_GATE` | Diode-isolated start path for `Q4` gate. |
| `D4` | `1` | `K` | `PWR_SW_N` | Lets `SW1` pull `CHG_SYSOFF` low during power-on. |
| `D4` | `2` | `A` | `CHG_SYSOFF` | Diode-isolated start path for BQ24075 `SYSOFF`. |
| `LED1` | `1` | `K` | `BLE_LED_K` | Blue BLE pairing LED cathode to `Q2.3`. |
| `LED1` | `2` | `A` | `BLE_LED_A` | Blue BLE pairing LED anode through `R5` to `SYS`. |
| `LED2` | `1` | `-` | `GND` | Always-on green power LED cathode. |
| `LED2` | `2` | `+` | `POWER_LED_A` | Always-on green power LED anode through `R20` to `+3V3`. |

### Resistors And Capacitors

| Ref | Pin 1 connects to | Pin 2 connects to | Instruction |
| --- | --- | --- | --- |
| `R9` | `CC1` | `GND` | USB-C CC1 sink pulldown. |
| `R10` | `CC2` | `GND` | USB-C CC2 sink pulldown. |
| `R15` | `CHG_TS` | `GND` | Charger TS fixed bias. |
| `R12` | `CHG_ISET` | `GND` | Charger current-set resistor. |
| `R11` | `CHG_ILIM` | `GND` | Charger input-current limit resistor. |
| `R14` | `CHG_TMR` | `GND` | Charger timer resistor. |
| `R13` | `nCHG` | `+3V3` | Pull-up for charger `nCHG`. |
| `R19` | `nPGOOD` | `+3V3` | Pull-up for charger `nPGOOD`. |
| `R16` | `EN` | `+3V3` | ESP32 enable pull-up. |
| `R6` | `BOOT_USER_BTN_N` | `+3V3` | ESP32 boot strap pull-up. |
| `R23` | `CHG_SYSOFF` | `BAT` | Pulls `SYSOFF` high after the switched battery rail is present. |
| `R24` | `PWR_HOLD_GATE` | `+3V3` | Pulls the latch gate high after `+3V3` starts, so bootloader mode stays powered without firmware. |
| `R25` | `PWR_HOLD` | `PWR_HOLD_GATE` | Power-hold MOSFET gate series resistor. |
| `R26` | `PWR_HOLD_GATE` | `GND` | Keeps `Q3`/`Q5` off while `+3V3` is absent. |
| `R27` | `PWR_BTN_N` | `+3V3` | Pull-up for the active-low power/user button input. |
| `R28` | `BAT_SWITCH_GATE` | `BAT_RAW` | Pulls the P-channel battery switch gate high so the raw battery is disconnected by default. |
| `R2` | `BAT` | `BAT_SENSE` | Battery divider top resistor. |
| `R1` | `BAT_SENSE` | `GND` | Battery divider bottom resistor. |
| `R22` | `USB_VBUS` | `USB_VBUS_SENSE` | USB VBUS divider top resistor. |
| `R21` | `USB_VBUS_SENSE` | `GND` | USB VBUS divider bottom resistor. |
| `R17` | `I2C_SCL` | `+3V3` | I2C SCL pull-up. |
| `R18` | `I2C_SDA` | `+3V3` | I2C SDA pull-up. |
| `R8` | `BUZZER_PWM` | `BUZZER_GATE` | Buzzer MOSFET gate series resistor. |
| `R7` | `BUZZER_GATE` | `GND` | Buzzer MOSFET gate pulldown. |
| `R5` | `SYS` | `BLE_LED_A` | Blue BLE pairing LED current limit resistor. |
| `R4` | `BLE_LED_PWM` | `BLE_LED_GATE` | BLE pairing LED MOSFET gate series resistor. |
| `R3` | `BLE_LED_GATE` | `GND` | BLE pairing LED MOSFET gate pulldown. |
| `R20` | `+3V3` | `POWER_LED_A` | Always-on green power LED current limit resistor. |
| `C14` | `USB_VBUS` | `GND` | USB input capacitor. |
| `C1` | `BAT` | `GND` | Switched battery bulk capacitor. |
| `C13` | `SYS` | `GND` | System rail bulk capacitor. |
| `C7` | `SYS` | `GND` | LDO input capacitor. |
| `C8` | `+3V3` | `GND` | LDO output capacitor. |
| `C9` | `+3V3` | `GND` | ESP32 local bulk capacitor. |
| `C10` | `+3V3` | `GND` | ESP32 high-frequency decoupling capacitor. |
| `C12` | `+3V3` | `GND` | BMP581 VDD decoupling capacitor. |
| `C11` | `+3V3` | `GND` | BMP581 VDDIO decoupling capacitor. |
| `C6` | `+3V3` | `GND` | BMI323 VDD decoupling capacitor. |
| `C5` | `+3V3` | `GND` | BMI323 VDDIO decoupling capacitor. |
| `C3` | `SYS` | `GND` | Local buzzer bulk capacitor. |
| `C4` | `EN` | `GND` | ESP32 enable/reset capacitor. |
| `C2` | `BAT_SENSE` | `GND` | Battery ADC filter capacitor. |

## Connection And Layout Constraints

- Do not route USB data directly to the MCU before `D1`; the ESD device must be
  first in line after the connector.
- Keep `USB_OTG_DP` and `USB_OTG_DM` short, parallel, and length-similar. Avoid
  stubs around the ESD part.
- Keep `USB_VBUS`, `BAT`, and `SYS` wider than normal signal nets. These nets
  carry charging, regulator, and buzzer current.
- Do not feed ESP32 GPIO pull-ups from `SYS`; use `+3V3` only.
- Keep `C7` and `C8` tight to `U3`; moving them away can make the LDO unstable.
- Keep each 100 nF sensor capacitor tight to its target sensor pin. Do not group
  all capacitors in one corner of the board.
- Keep the ESP32 antenna area at the board edge clear of copper, vias, battery,
  buzzer metal, enclosure metal, and tall components.
- Keep `U5` away from heat sources, airflow from the buzzer, adhesive stress,
  and board edges that flex. Pressure sensors are sensitive to thermal and
  mechanical disturbance.
- Keep `U2` near the mechanical center of the board if orientation/acceleration
  data matters. Record final axis orientation in firmware.
- Keep `BZ1`, `Q1`, `R8`, `R7`, and `C3` together. The buzzer switching loop
  should not run under `U5`, `U2`, or the I2C pull-ups.
- `SW1`, `D2`, `D3`, `D4`, `Q3`, `Q4`, `Q5`, `R23`, `R24`, `R26`, and `R28`
  form the hard-off latch. Keep `CHG_SYSOFF` and `BAT_SWITCH_GATE` short and
  away from noisy switching nodes.
- Firmware must leave `PWR_HOLD` high-Z/high for normal operation and drive it
  low only when intentionally shutting down from battery power.
- Firmware must use `USB_VBUS_SENSE` and `PWR_BTN_N` to keep USB attach from an
  off state in USB-attached idle mode until the user presses `POWER` or a
  supported start command is received.
- `SW2` and `SW3` provide hidden service ESP32-S3 ROM bootloader recovery
  without debug pads. PCB/enclosure access should be pinhole/service-only and
  labeled `BOOT` and `RST`.
- `J1` polarity must be checked against the intended LiPo connector and pack
  wiring. JST PH-compatible parts are often assembled with opposite cable
  conventions.
- The local footprints for `J1`, `BZ1`, `Q1`, `Q2`, `Q3`, `Q4`, `Q5`,
  `D2`-`D4`, and `SW1`-`SW3` should be checked against manufacturer
  land-pattern drawings before production.
