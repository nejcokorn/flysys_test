# FlySys Schematic Description

Updated: 2026-06-02

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
| `BAT` | LiPo battery positive terminal. Feeds charger battery pin and battery ADC divider. |
| `SYS` | Charger power-path output. Feeds 3.3 V regulator and high-current buzzer/blue LED loads. |
| `+3V3` | Regulated logic rail for ESP32-S3, sensors, pull-ups, and debug pads. |
| `GND` | Common ground and USB shield reference. |

## USB-C And ESD

`USB1` is the USB-C device connector. `CC1` and `CC2` are each pulled down to
ground by `R9` and `R10`, both 5.1 kohm, so the board presents itself as a USB
device/sink.

USB data exits the connector as `USB_DP_CONN` and `USB_DM_CONN`, passes through
`D1` (`USBLC6-2SC6`) for ESD protection, then continues to the ESP32-S3 as
`USB_OTG_DP` and `USB_OTG_DM`. `D1` must stay physically between `USB1` and
`U4`, close to the connector, so ESD current is shunted before it reaches the
MCU.

The USB-C shell/mechanical pads are tied to `GND`. The local USB footprint maps
all shell pads to the same symbol pin so KiCad does not leave shield pads
unconnected during PCB update.

## Charger And Power Path

`U1` (`BQ24075RGTR`) receives `USB_VBUS` on `IN`, connects the LiPo battery on
`BAT`, and produces the system rail on `OUT`/`SYS`. The charger is enabled by
tying `nCE` low. `EN1`, `EN2`, `SYSOFF`, `TS`, `ISET`, `ILIM`, and `TMR` are
configured with fixed resistors, so the current limits and timer behavior are
set in hardware.

`nCHG` and `nPGOOD` are open-drain charger status outputs. `R13` and `R19` pull
them up to `+3V3`, and the MCU reads them on GPIOs. These nets should not be
pulled to `SYS` because the ESP32-S3 GPIOs are 3.3 V only.

`J1` is the 2-pin LiPo connector. `BAT_POS` goes to `BAT`, and `BAT_NEG` goes to
`GND`. The final build must confirm connector polarity against the actual
battery harness before ordering or assembly.

## 3.3 V Regulation

`U3` (`TLV75533PDBVR`) converts `SYS` into `+3V3`. The regulator enable pin is
tied to `SYS`, so the 3.3 V rail is on whenever the charger power path has a
valid input from USB or battery.

`+3V3` powers the ESP32-S3 module, BMP581 pressure sensor, BMI323 IMU, I2C
pull-ups, charger status pull-ups, green power LED, and debug pads.

## ESP32-S3 MCU

`U4` is the main controller. It uses native USB through `USB_OTG_DP` and
`USB_OTG_DM`, reads battery and USB voltage dividers, reads charger status, runs
the I2C sensor bus, drives the buzzer PWM MOSFET, and drives the BLE status LED
MOSFET.

`EN` has a 10 kohm pull-up (`R16`) and 100 nF capacitor (`C4`) for a simple reset
RC network. `BOOT_USER_BTN_N` is pulled up by `R6` and pulled to ground by
`SW1`; this doubles as user input and ESP32 boot-mode control. Firmware and
mechanical design must avoid holding this button during reset unless USB boot
mode is intended.

`J2` exposes `GND`, `+3V3`, `EN`, `BOOT_USER_BTN_N`, `TXD0`, and `RXD0` as PCB
debug pads. It is not a purchase part.

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
returns directly to `GND`.

`LED1` is the blue BLE status LED. It is powered from `SYS` through `R5` and
switched by `Q2`, another low-side `AO3400A`. `R4` is the series gate resistor,
and `R3` is the gate pulldown. This keeps the LED off while the ESP32-S3 GPIO is
high impedance.

## Capacitors And Their Roles

| Ref | Value | Net | Role |
| --- | --- | --- | --- |
| `C14` | 1 uF | `USB_VBUS` to `GND` | USB input decoupling. It supplies short input-current pulses and should sit close to `USB1`/`U1 IN`. |
| `C1` | 10 uF | `BAT` to `GND` | Battery rail bulk capacitance. It stabilizes the charger battery pin and absorbs cable/connector transients. |
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
| `C2` | 100 nF | `BAT_SENSE` to `GND` | ADC filter for the battery divider midpoint. Place near `R1`/`R2` and the MCU ADC input. |

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
| `U4` | `7`, `11`, `14`, `15`, `16`, `17`, `18`, `19`, `20`, `25`, `26`, `27`, `28`, `29`, `30`, `31`, `32`, `35`, `36`, `37`, `38`, `41`, `44` | Unused ESP32-S3 GPIO/module pins. Leave floating and mark no-connect. Do not tie unused GPIOs to rails in hardware. |
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
| `J1` | `1` | `BAT+` | `BAT` | LiPo positive terminal. Confirm pack polarity before assembly. |
| `J1` | `2` | `BAT-` | `GND` | LiPo negative terminal. |
| `J2` | `1` | `GND` | `GND` | Debug pad ground reference. |
| `J2` | `2` | `+3V3` | `+3V3` | Debug pad logic supply reference. Do not use as a high-current external supply output. |
| `J2` | `3` | `EN` | `EN` | ESP32 reset/enable debug access. |
| `J2` | `4` | `BOOT` | `BOOT_USER_BTN_N` | ESP32 boot/user-button debug access. |
| `J2` | `5` | `TXD0` | `TXD0` | UART0 transmit from ESP32. |
| `J2` | `6` | `RXD0` | `RXD0` | UART0 receive into ESP32. |

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
| `U1` | `15` | `SYSOFF` | `GND` | System output remains enabled. |
| `U1` | `16` | `ISET` | `CHG_ISET` | Connect to `R12` then `GND`. |
| `U1` | `17` | `EP` | `GND` | Exposed pad. Stitch to ground plane for thermal and electrical return. |
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
| `U4` | `4` | `IO0` | `BOOT_USER_BTN_N` | Boot/user button net with pull-up `R6` and switch `SW1` to ground. |
| `U4` | `5` | `IO1` | `BAT_SENSE` | Battery ADC sense divider midpoint with filter `C2`. |
| `U4` | `6` | `IO2` | `USB_VBUS_SENSE` | USB VBUS ADC sense divider midpoint. |
| `U4` | `7` | `IO3` | `NC` | Leave floating and mark no-connect. |
| `U4` | `8` | `IO4` | `BMP581_INT` | Pressure sensor interrupt input. |
| `U4` | `9` | `IO5` | `BMI323_INT1` | IMU interrupt input 1. |
| `U4` | `10` | `IO6` | `BMI323_INT2` | IMU interrupt input 2. |
| `U4` | `11` | `IO7` | `NC` | Leave floating and mark no-connect. This was previously reserved for removed magnetometer pads. |
| `U4` | `12` | `IO8` | `I2C_SCL` | I2C clock with pull-up `R17`. |
| `U4` | `13` | `IO9` | `I2C_SDA` | I2C data with pull-up `R18`. |
| `U4` | `14`, `15`, `16`, `17`, `18`, `19`, `20` | `IO10` to `IO16` | `NC` | Leave floating and mark no-connect. |
| `U4` | `21` | `IO17` | `BUZZER_PWM` | PWM output to `Q1` through `R8`. |
| `U4` | `22` | `IO18` | `BLE_LED_PWM` | LED control output to `Q2` through `R4`. |
| `U4` | `23` | `IO19` | `USB_OTG_DM` | Native USB D-. Route as controlled short USB pair with pin 24. |
| `U4` | `24` | `IO20` | `USB_OTG_DP` | Native USB D+. Route as controlled short USB pair with pin 23. |
| `U4` | `25`, `26`, `27`, `28`, `29`, `30`, `31`, `32` | `IO21`, `IO26`, `IO47`, `IO33`, `IO34`, `IO48`, `IO35`, `IO36` | `NC` | Leave floating and mark no-connect. |
| `U4` | `33` | `IO37` | `nCHG` | Charger status input from `U1`, pulled up to `+3V3` by `R13`. |
| `U4` | `34` | `IO38` | `nPGOOD` | Charger power-good input from `U1`, pulled up to `+3V3` by `R19`. |
| `U4` | `35`, `36`, `37`, `38` | `IO39` to `IO42` | `NC` | Leave floating and mark no-connect. |
| `U4` | `39` | `TXD0` | `TXD0` | UART transmit to debug pad `J2.5`. |
| `U4` | `40` | `RXD0` | `RXD0` | UART receive from debug pad `J2.6`. |
| `U4` | `41` | `IO45` | `NC` | Leave floating and mark no-connect. |
| `U4` | `44` | `IO46` | `NC` | Leave floating and mark no-connect. |
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
| `SW1` | `1`, `2` | `A` | `BOOT_USER_BTN_N` | Button side connected to boot/user net. |
| `SW1` | `3`, `4` | `B` | `GND` | Button side connected to ground. |
| `BZ1` | `1` | `+` | `SYS` | Buzzer positive terminal. Keep current path local to `C3`. |
| `BZ1` | `2` | `-` | `BUZZER_NEG` | Buzzer switched return to `Q1.3`. |
| `Q1` | `1` | `G` | `BUZZER_GATE` | Gate drive from `R8`, pulldown by `R7`. |
| `Q1` | `2` | `S` | `GND` | Low-side switch source. |
| `Q1` | `3` | `D` | `BUZZER_NEG` | Low-side switch drain to buzzer negative terminal. |
| `Q2` | `1` | `G` | `BLE_LED_GATE` | Gate drive from `R4`, pulldown by `R3`. |
| `Q2` | `2` | `S` | `GND` | Low-side switch source. |
| `Q2` | `3` | `D` | `BLE_LED_K` | Low-side switch drain to blue LED cathode. |
| `LED1` | `1` | `K` | `BLE_LED_K` | Blue LED cathode to `Q2.3`. |
| `LED1` | `2` | `A` | `BLE_LED_A` | Blue LED anode through `R5` to `SYS`. |
| `LED2` | `1` | `-` | `GND` | Green power LED cathode. |
| `LED2` | `2` | `+` | `POWER_LED_A` | Green power LED anode through `R20` to `+3V3`. |

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
| `R6` | `BOOT_USER_BTN_N` | `+3V3` | ESP32 boot/user button pull-up. |
| `R2` | `BAT` | `BAT_SENSE` | Battery divider top resistor. |
| `R1` | `BAT_SENSE` | `GND` | Battery divider bottom resistor. |
| `R22` | `USB_VBUS` | `USB_VBUS_SENSE` | USB VBUS divider top resistor. |
| `R21` | `USB_VBUS_SENSE` | `GND` | USB VBUS divider bottom resistor. |
| `R17` | `I2C_SCL` | `+3V3` | I2C SCL pull-up. |
| `R18` | `I2C_SDA` | `+3V3` | I2C SDA pull-up. |
| `R8` | `BUZZER_PWM` | `BUZZER_GATE` | Buzzer MOSFET gate series resistor. |
| `R7` | `BUZZER_GATE` | `GND` | Buzzer MOSFET gate pulldown. |
| `R5` | `SYS` | `BLE_LED_A` | Blue LED current limit resistor. |
| `R4` | `BLE_LED_PWM` | `BLE_LED_GATE` | BLE LED MOSFET gate series resistor. |
| `R3` | `BLE_LED_GATE` | `GND` | BLE LED MOSFET gate pulldown. |
| `R20` | `+3V3` | `POWER_LED_A` | Green power LED current limit resistor. |
| `C14` | `USB_VBUS` | `GND` | USB input capacitor. |
| `C1` | `BAT` | `GND` | Battery bulk capacitor. |
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
- `BOOT_USER_BTN_N` is both a user button and ESP32 boot strap. The enclosure
  must not press `SW1` during power-up or reset unless flashing mode is desired.
- `J1` polarity must be checked against the intended LiPo connector and pack
  wiring. JST PH-compatible parts are often assembled with opposite cable
  conventions.
- The local footprints for `J1`, `BZ1`, `Q1`, `Q2`, `SW1`, and `J2` should be
  checked against manufacturer land-pattern drawings before production.
