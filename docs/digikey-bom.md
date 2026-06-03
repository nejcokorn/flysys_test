# FlySys DigiKey BOM

Updated: 2026-06-03

All purchased components in the KiCad schematic use DigiKey order lines. Debug pads are not fitted; normal firmware update is software-first, and ESP32-S3 bootloader recovery uses USB plus hidden BOOT and RST service buttons.

| References | Qty | Value | Manufacturer | MPN | DigiKey PN | Description |
| --- | ---: | --- | --- | --- | --- | --- |
| Q1, Q2, Q3, Q5 | 4 | AO3400A | Alpha & Omega Semiconductor Inc. | AO3400A | [785-1000-1-ND](https://www.digikey.com/en/products/detail/alpha-omega-semiconductor-inc/AO3400A/1855772) | N-channel MOSFET, SOT-23 |
| U2 | 1 | BMI323 | Bosch Sensortec | BMI323 | [828-BMI323CT-ND](https://www.digikey.com/en/products/detail/bosch-sensortec/BMI323/16719593) | 6-axis IMU |
| U5 | 1 | BMP581 | Bosch Sensortec | BMP581 | [828-BMP581CT-ND](https://www.digikey.com/en/products/detail/bosch-sensortec/BMP581/16036134) | Barometric pressure sensor |
| SW1, SW2, SW3 | 3 | KMR211NG LFS | C&K | KMR211NG LFS | [CKN10243CT-ND](https://www.digikey.com/en/products/detail/c-k/KMR211NG-LFS/2176482) | Low-profile tactile switch |
| D2, D3, D4 | 3 | 1N4148W | Diodes Incorporated | 1N4148W-7-F | [1N4148W-FDICT-ND](https://www.digikey.com/en/products/detail/diodes-incorporated/1N4148W-7-F/815280) | Small-signal switching diode, SOD-123 |
| Q4 | 1 | DMP3098L | Diodes Incorporated | DMP3098L-7 | [DMP3098L-7DICT-ND](https://www.digikey.com/en/products/detail/diodes-incorporated/DMP3098L-7/1964698) | P-channel MOSFET, SOT-23 |
| U4 | 1 | ESP32-S3-MINI-1-N8 | Espressif Systems | ESP32-S3-MINI-1-N8 | [5407-ESP32-S3-MINI-1-N8CT-ND](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-MINI-1-N8/15295890) | ESP32-S3 module with PCB antenna and 8 MB flash |
| USB1 | 1 | USB4105-GF-A | GCT | USB4105-GF-A | [2073-USB4105-GF-ACT-ND](https://www.digikey.com/en/products/detail/gct/USB4105-GF-A/11198441) | USB-C receptacle, USB 2.0, right angle |
| J1 | 1 | S2B-PH-SM4-TB | JST Sales America Inc. | S2B-PH-SM4-TB | [455-S2B-PH-SM4-TBCT-ND](https://www.digikey.com/en/products/detail/jst-sales-america-inc/S2B-PH-SM4-TB/926655) | 2-pin JST PH side-entry SMT header |
| LED2 | 1 | LTST-C190GKT | Lite-On Inc. | LTST-C190GKT | [160-LTST-C190GKTCT-ND](https://www.digikey.com/en/products/detail/lite-on-inc/LTST-C190GKT/269255) | Green 0603 LED |
| LED1 | 1 | LTST-C190TBKT | Lite-On Inc. | LTST-C190TBKT | [160-1646-1-ND](https://www.digikey.com/en/products/detail/lite-on-inc/LTST-C190TBKT/388529) | Blue 0603 LED |
| D1 | 1 | USBLC6-2SC6Y | STMicroelectronics | USBLC6-2SC6Y | [497-11882-1-ND](https://www.digikey.com/en/products/detail/stmicroelectronics/USBLC6-2SC6Y/2819177) | Automotive USB ESD protection diode array, SOT-23-6 |
| BZ1 | 1 | CSS-J4D20-SMT-TR | Same Sky (Formerly CUI Devices) | CSS-J4D20-SMT-TR | [102-1198-1-ND](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CSS-J4D20-SMT-TR/504819) | Externally driven magnetic buzzer |
| C7, C8, C14 | 3 | 1uF | Samsung Electro-Mechanics | CL10A105KB8NNNC | [1276-1860-1-ND](https://www.digikey.com/en/products/detail/samsung-electro-mechanics/CL10A105KB8NNNC/3887518) | 1 uF, 50 V, X5R, 0603 capacitor |
| C1, C3, C9, C13 | 4 | 10uF | Samsung Electro-Mechanics | CL10A106KP8NNNC | [1276-1192-1-ND](https://www.digikey.com/en/products/detail/samsung-electro-mechanics/CL10A106KP8NNNC/3886850) | 10 uF, 10 V, X5R, 0603 capacitor |
| U1 | 1 | BQ24075RGTR | Texas Instruments | BQ24075RGTR | [296-38874-1-ND](https://www.digikey.com/en/products/detail/texas-instruments/BQ24075RGTR/2047273) | Li-ion charger and power-path controller |
| U3 | 1 | TLV75533PDBVR | Texas Instruments | TLV75533PDBVR | [296-50411-1-ND](https://www.digikey.com/en/products/detail/texas-instruments/TLV75533PDBVR/9356541) | 3.3 V 500 mA LDO regulator |
| C2, C4, C5, C6, C10, C11, C12 | 7 | 100nF | YAGEO | CC0603KRX7R9BB104 | [311-1344-1-ND](https://www.digikey.com/en/products/detail/yageo/CC0603KRX7R9BB104/2103082) | 100 nF, 50 V, X7R, 0603 capacitor |
| R3, R7, R24 | 3 | 100k | YAGEO | RC0603FR-07100KL | [311-100KHRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0603FR-07100KL/726889) | 100 kohm, 1%, 0.1 W, 0603 resistor |
| R4, R8, R25 | 3 | 100R | YAGEO | RC0603FR-07100RL | [311-100HRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0603FR-07100RL/726888) | 100 ohm, 1%, 0.1 W, 0603 resistor |
| R6, R13, R15, R16, R19 | 5 | 10k | YAGEO | RC0603FR-0710KL | [311-10.0KHRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0603FR-0710KL/726880) | 10 kohm, 1%, 0.1 W, 0603 resistor |
| R11 | 1 | 1.1k | YAGEO | RC0603FR-071K1L | [311-1.10KHRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0603FR-071K1L/726848) | 1.1 kohm, 1%, 0.1 W, 0603 resistor |
| R5, R20 | 2 | 1k | YAGEO | RC0603FR-071KL | [311-1.00KHRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0603FR-071KL/726843) | 1 kohm, 1%, 0.1 W, 0603 resistor |
| R1, R2, R22, R23, R26, R28 | 6 | 1M | YAGEO | RC0603FR-071ML | [311-1.00MHRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0603FR-071ML/729791) | 1 Mohm, 1%, 0.1 W, 0603 resistor |
| R12 | 1 | 2k | YAGEO | RC0603FR-072KL | [311-2.00KHRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0603FR-072KL/727009) | 2 kohm, 1%, 0.1 W, 0603 resistor |
| R21 | 1 | 330k | YAGEO | RC0603FR-07330KL | [311-330KHRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0603FR-07330KL/727163) | 330 kohm, 1%, 0.1 W, 0603 resistor |
| R14 | 1 | 47k | YAGEO | RC0603FR-0747KL | [311-47.0KHRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0603FR-0747KL/727253) | 47 kohm, 1%, 0.1 W, 0603 resistor |
| R17, R18, R27 | 3 | 4.7k | YAGEO | RC0603FR-074K7L | [311-4.70KHRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0603FR-074K7L/727212) | 4.7 kohm, 1%, 0.1 W, 0603 resistor |
| R9, R10 | 2 | 5.1k | YAGEO | RC0603FR-075K1L | [311-5.10KHRCT-ND](https://www.digikey.com/en/products/detail/yageo/RC0603FR-075K1L/727268) | 5.1 kohm, 1%, 0.1 W, 0603 resistor |

Note: Atopile 0.15.7 currently supports only LCSC in its built-in `has_part_picked` BOM path. The DigiKey BOM above is therefore generated by this project script and is the procurement source of truth.
