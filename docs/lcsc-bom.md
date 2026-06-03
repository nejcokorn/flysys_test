# FlySys LCSC Component Set

Updated: 2026-06-03

This table lists the components that Atopile currently resolves through its
built-in LCSC picker path. It is generated from the active Atopile BOM at
`build/builds/default/default.bom.csv`.

The project also has parts that are not in this LCSC set: `D2`, `D3`, `D4`,
`Q1`, `Q2`, `Q3`, `Q4`, `Q5`, `U5`, `SW1`, `SW2`, `SW3`, `J1`, and `BZ1` are
handled in the DigiKey BOM. Debug pads are not fitted.

| References | Qty | Value | Manufacturer | MPN | LCSC Part |
| --- | ---: | --- | --- | --- | --- |
| `C1`, `C3`, `C9`, `C13` | 4 | 10 uF, 10 V, X5R | Samsung Electro-Mechanics | `CL10A106KP8NNNC` | `C19702` |
| `C2`, `C4`, `C5`, `C6`, `C10`, `C11`, `C12` | 7 | 100 nF, 50 V, X7R | YAGEO | `CC0603KRX7R9BB104` | `C14663` |
| `C7`, `C8`, `C14` | 3 | 1 uF, 50 V, X5R | Samsung Electro-Mechanics | `CL10A105KB8NNNC` | `C15849` |
| `D1` | 1 | Automotive USB ESD protection, SOT-23-6L | STMicroelectronics | `USBLC6-2SC6Y` | `C2969755` |
| `LED1` | 1 | Blue 0603 LED | Lite-On | `LTST-C190TBKT` | `C125096` |
| `LED2` | 1 | Green 0603 LED | Lite-On | `LTST-C190GKT` | `C125093` |
| `R1`, `R2`, `R22`, `R23`, `R26`, `R28` | 6 | 1 Mohm, 1%, 0603 | UNI-ROYAL | `0603WAF1004T5E` | `C22935` |
| `R3`, `R7`, `R24` | 3 | 100 kohm, 1%, 0603 | UNI-ROYAL | `0603WAF1003T5E` | `C25803` |
| `R4`, `R8`, `R25` | 3 | 100 ohm, 1%, 0603 | UNI-ROYAL | `0603WAF1000T5E` | `C22775` |
| `R5`, `R20` | 2 | 1 kohm, 1%, 0603 | UNI-ROYAL | `0603WAF1001T5E` | `C21190` |
| `R6`, `R13`, `R15`, `R16`, `R19` | 5 | 10 kohm, 1%, 0603 | UNI-ROYAL | `0603WAF1002T5E` | `C25804` |
| `R9`, `R10` | 2 | 5.1 kohm, 1%, 0603 | UNI-ROYAL | `0603WAF5101T5E` | `C23186` |
| `R11` | 1 | 1.1 kohm, 1%, 0603 | UNI-ROYAL | `0603WAF1101T5E` | `C22764` |
| `R12` | 1 | 2 kohm, 1%, 0603 | UNI-ROYAL | `0603WAF2001T5E` | `C22975` |
| `R14` | 1 | 47 kohm, 1%, 0603 | UNI-ROYAL | `0603WAF4702T5E` | `C25819` |
| `R17`, `R18`, `R27` | 3 | 4.7 kohm, 1%, 0603 | UNI-ROYAL | `0603WAF4701T5E` | `C23162` |
| `R21` | 1 | 330 kohm, 1%, 0603 | UNI-ROYAL | `0603WAF3303T5E` | `C23137` |
| `U1` | 1 | LiPo charger and power-path controller | Texas Instruments | `BQ24075RGTR` | `C15464` |
| `U2` | 1 | 6-axis IMU | Bosch Sensortec | `BMI323` | `C5368700` |
| `U3` | 1 | 3.3 V LDO regulator | Texas Instruments | `TLV75533PDBVR` | `C404027` |
| `U4` | 1 | ESP32-S3 module | Espressif Systems | `ESP32-S3-MINI-1-N8` | `C2913206` |
| `USB1` | 1 | USB-C receptacle | GCT | `USB4105-GF-A` | `C3020560` |

## Procurement Note

Use `docs/digikey-bom.md` or `kicad/flysys_vario_digikey_bom.csv` when the
order must be DigiKey-only. Use this LCSC table when checking what Atopile
currently knows how to pick through its built-in supplier flow.
