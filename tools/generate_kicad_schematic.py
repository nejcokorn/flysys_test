#!/usr/bin/env python3
"""Generate the FlySys KiCad schematic from the hardware net plan."""

from __future__ import annotations

import csv
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "parts"
KICAD = ROOT / "kicad"
PROJECT = "flysys_vario"
SHEET_UUID = uuid.uuid5(uuid.NAMESPACE_URL, "flysys-vario/root-sheet")
GRID_MM = 1.27


@dataclass(frozen=True)
class Kind:
    lib: str
    symbol: str
    symfile: str
    footprint: str


@dataclass(frozen=True)
class Pin:
    number: str
    name: str
    x: float
    y: float
    angle: int


@dataclass(frozen=True)
class Component:
    ref: str
    value: str
    kind: str
    x: float
    y: float
    pins: dict[str, str | None]


@dataclass(frozen=True)
class SupplierPart:
    manufacturer: str
    mpn: str
    digikey_pn: str
    digikey_url: str
    description: str
    supplier: str = "DigiKey"
    in_bom: bool = True


KINDS: dict[str, Kind] = {
    "USB4105": Kind("GCT_USB4105_GF_A", "USB4105-GF-A", "USB4105-GF-A.kicad_sym", "GCT_USB4105_GF_A:TYPE-C-SMD_SBC-160S1A-20-S412"),
    "USBLC6": Kind("STMicroelectronics_USBLC6_2SC6", "USBLC6-2SC6", "USBLC6-2SC6.kicad_sym", "STMicroelectronics_USBLC6_2SC6:SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BL"),
    "DIODE_1N4148W": Kind("Diodes_Inc_1N4148W", "1N4148W", "1N4148W.kicad_sym", "Diodes_Inc_1N4148W:1N4148W"),
    "BQ24075": Kind("Texas_Instruments_BQ24075RGTR", "BQ24075RGTR", "BQ24075RGTR.kicad_sym", "Texas_Instruments_BQ24075RGTR:QFN-16_L3.0-W3.0-P0.50-TL-EP1.7"),
    "TLV75533": Kind("Texas_Instruments_TLV75533PDBVR", "TLV75533PDBVR", "TLV75533PDBVR.kicad_sym", "Texas_Instruments_TLV75533PDBVR:SOT-23-5_L3.0-W1.7-P0.95-LS2.8-BR"),
    "JST_PH_2": Kind("JST_S2B_PH_SM4_TB", "S2B-PH-SM4-TB", "S2B-PH-SM4-TB.kicad_sym", "JST_S2B_PH_SM4_TB:S2B-PH-SM4-TB"),
    "ESP32S3": Kind("Espressif_Systems_ESP32_S3_MINI_1_N8", "ESP32-S3-MINI-1-N8", "ESP32-S3-MINI-1-N8.kicad_sym", "Espressif_Systems_ESP32_S3_MINI_1_N8:BULETM-SMD_ESP32-S3-MINI-1-N8"),
    "BMP581": Kind("Bosch_Sensortec_BMP581", "BMP581", "BMP581.kicad_sym", "Bosch_Sensortec_BMP581:BMP581_LGA10_2x2mm"),
    "BMI323": Kind("Bosch_Sensortec_BMI323", "BMI323", "BMI323.kicad_sym", "Bosch_Sensortec_BMI323:LGA-14_L3.0-W2.5-P0.50-TL_QMI8658A"),
    "BUZZER": Kind("Same_Sky_CSS_J4D20_SMT_TR", "CSS-J4D20-SMT-TR", "CSS-J4D20-SMT-TR.kicad_sym", "Same_Sky_CSS_J4D20_SMT_TR:CSS-J4D20-SMT-TR"),
    "AO3400A": Kind("Alpha_Omega_AO3400A", "AO3400A", "AO3400A.kicad_sym", "Alpha_Omega_AO3400A:AO3400A"),
    "DMP3098L": Kind("Diodes_Inc_DMP3098L", "DMP3098L", "DMP3098L.kicad_sym", "Diodes_Inc_DMP3098L:DMP3098L"),
    "BUTTON": Kind("CK_KMR211NG_LFS", "KMR211NG_LFS", "KMR211NG_LFS.kicad_sym", "CK_KMR211NG_LFS:KMR211NG_LFS"),
    "LED_GREEN": Kind("Lite_On_LTST_C190GKT", "LTST-C190GKT", "LTST-C190GKT.kicad_sym", "Lite_On_LTST_C190GKT:LED0603-RD"),
    "LED_BLUE": Kind("Lite_On_LTST_C190TBKT", "LTST-C190TBKT", "LTST-C190TBKT.kicad_sym", "Lite_On_LTST_C190TBKT:LED0603-RD"),
    "R100": Kind("UNI_ROYAL_0603WAF1000T5E", "0603WAF1000T5E", "0603WAF1000T5E.kicad_sym", "UNI_ROYAL_0603WAF1000T5E:R0603"),
    "R1K": Kind("UNI_ROYAL_0603WAF1001T5E", "0603WAF1001T5E", "0603WAF1001T5E.kicad_sym", "UNI_ROYAL_0603WAF1001T5E:R0603"),
    "R2K": Kind("UNI_ROYAL_0603WAF2001T5E", "0603WAF2001T5E", "0603WAF2001T5E.kicad_sym", "UNI_ROYAL_0603WAF2001T5E:R0603"),
    "R5K1": Kind("UNI_ROYAL_0603WAF5101T5E", "0603WAF5101T5E", "0603WAF5101T5E.kicad_sym", "UNI_ROYAL_0603WAF5101T5E:R0603"),
    "R10K": Kind("UNI_ROYAL_0603WAF1002T5E", "0603WAF1002T5E", "0603WAF1002T5E.kicad_sym", "UNI_ROYAL_0603WAF1002T5E:R0603"),
    "R47K": Kind("UNI_ROYAL_0603WAF4702T5E", "0603WAF4702T5E", "0603WAF4702T5E.kicad_sym", "UNI_ROYAL_0603WAF4702T5E:R0603"),
    "R100K": Kind("UNI_ROYAL_0603WAF1003T5E", "0603WAF1003T5E", "0603WAF1003T5E.kicad_sym", "UNI_ROYAL_0603WAF1003T5E:R0603"),
    "R330K": Kind("UNI_ROYAL_0603WAF3303T5E", "0603WAF3303T5E", "0603WAF3303T5E.kicad_sym", "UNI_ROYAL_0603WAF3303T5E:R0603"),
    "R1M": Kind("UNI_ROYAL_0603WAF1004T5E", "0603WAF1004T5E", "0603WAF1004T5E.kicad_sym", "UNI_ROYAL_0603WAF1004T5E:R0603"),
    "R1K1": Kind("UNI_ROYAL_0603WAF1101T5E", "0603WAF1101T5E", "0603WAF1101T5E.kicad_sym", "UNI_ROYAL_0603WAF1101T5E:R0603"),
    "R4K7": Kind("UNI_ROYAL_0603WAF4701T5E", "0603WAF4701T5E", "0603WAF4701T5E.kicad_sym", "UNI_ROYAL_0603WAF4701T5E:R0603"),
    "C100N": Kind("YAGEO_CC0603KRX7R9BB104", "CC0603KRX7R9BB104", "CC0603KRX7R9BB104.kicad_sym", "YAGEO_CC0603KRX7R9BB104:C0603"),
    "C1U": Kind("Samsung_Electro_Mechanics_CL10A105KB8NNNC", "CL10A105KB8NNNC", "CL10A105KB8NNNC.kicad_sym", "Samsung_Electro_Mechanics_CL10A105KB8NNNC:C0603"),
    "C10U": Kind("Samsung_Electro_Mechanics_CL10A106KP8NNNC", "CL10A106KP8NNNC", "CL10A106KP8NNNC.kicad_sym", "Samsung_Electro_Mechanics_CL10A106KP8NNNC:C0603"),
}


DIGIKEY_PARTS: dict[str, SupplierPart] = {
    "USB4105": SupplierPart("GCT", "USB4105-GF-A", "2073-USB4105-GF-ACT-ND", "https://www.digikey.com/en/products/detail/gct/USB4105-GF-A/11198441", "USB-C receptacle, USB 2.0, right angle"),
    "USBLC6": SupplierPart("STMicroelectronics", "USBLC6-2SC6", "497-5235-1-ND", "https://www.digikey.com/en/products/detail/stmicroelectronics/USBLC6-2SC6/1040559", "USB ESD protection diode array"),
    "DIODE_1N4148W": SupplierPart("Diodes Incorporated", "1N4148W-7-F", "1N4148W-FDICT-ND", "https://www.digikey.com/en/products/detail/diodes-incorporated/1N4148W-7-F/815280", "Small-signal switching diode, SOD-123"),
    "BQ24075": SupplierPart("Texas Instruments", "BQ24075RGTR", "296-38874-1-ND", "https://www.digikey.com/en/products/detail/texas-instruments/BQ24075RGTR/2047273", "Li-ion charger and power-path controller"),
    "TLV75533": SupplierPart("Texas Instruments", "TLV75533PDBVR", "296-50411-1-ND", "https://www.digikey.com/en/products/detail/texas-instruments/TLV75533PDBVR/9356541", "3.3 V 500 mA LDO regulator"),
    "JST_PH_2": SupplierPart("JST Sales America Inc.", "S2B-PH-SM4-TB", "455-S2B-PH-SM4-TBCT-ND", "https://www.digikey.com/en/products/detail/jst-sales-america-inc/S2B-PH-SM4-TB/926655", "2-pin JST PH side-entry SMT header"),
    "ESP32S3": SupplierPart("Espressif Systems", "ESP32-S3-MINI-1-N8", "5407-ESP32-S3-MINI-1-N8CT-ND", "https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-MINI-1-N8/15295890", "ESP32-S3 module with PCB antenna and 8 MB flash"),
    "BMP581": SupplierPart("Bosch Sensortec", "BMP581", "828-BMP581CT-ND", "https://www.digikey.com/en/products/detail/bosch-sensortec/BMP581/16036134", "Barometric pressure sensor"),
    "BMI323": SupplierPart("Bosch Sensortec", "BMI323", "828-BMI323CT-ND", "https://www.digikey.com/en/products/detail/bosch-sensortec/BMI323/16719593", "6-axis IMU"),
    "BUZZER": SupplierPart("Same Sky (Formerly CUI Devices)", "CSS-J4D20-SMT-TR", "102-1198-1-ND", "https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CSS-J4D20-SMT-TR/504819", "Externally driven magnetic buzzer"),
    "AO3400A": SupplierPart("Alpha & Omega Semiconductor Inc.", "AO3400A", "785-1000-1-ND", "https://www.digikey.com/en/products/detail/alpha-omega-semiconductor-inc/AO3400A/1855772", "N-channel MOSFET, SOT-23"),
    "DMP3098L": SupplierPart("Diodes Incorporated", "DMP3098L-7", "DMP3098L-7DICT-ND", "https://www.digikey.com/en/products/detail/diodes-incorporated/DMP3098L-7/1964698", "P-channel MOSFET, SOT-23"),
    "BUTTON": SupplierPart("C&K", "KMR211NG LFS", "CKN10243CT-ND", "https://www.digikey.com/en/products/detail/c-k/KMR211NG-LFS/2176482", "Low-profile tactile switch"),
    "LED_GREEN": SupplierPart("Lite-On Inc.", "LTST-C190GKT", "160-LTST-C190GKTCT-ND", "https://www.digikey.com/en/products/detail/lite-on-inc/LTST-C190GKT/269255", "Green 0603 LED"),
    "LED_BLUE": SupplierPart("Lite-On Inc.", "LTST-C190TBKT", "160-1646-1-ND", "https://www.digikey.com/en/products/detail/lite-on-inc/LTST-C190TBKT/388529", "Blue 0603 LED"),
    "R100": SupplierPart("YAGEO", "RC0603FR-07100RL", "311-100HRCT-ND", "https://www.digikey.com/en/products/detail/yageo/RC0603FR-07100RL/726888", "100 ohm, 1%, 0.1 W, 0603 resistor"),
    "R1K": SupplierPart("YAGEO", "RC0603FR-071KL", "311-1.00KHRCT-ND", "https://www.digikey.com/en/products/detail/yageo/RC0603FR-071KL/726843", "1 kohm, 1%, 0.1 W, 0603 resistor"),
    "R2K": SupplierPart("YAGEO", "RC0603FR-072KL", "311-2.00KHRCT-ND", "https://www.digikey.com/en/products/detail/yageo/RC0603FR-072KL/727009", "2 kohm, 1%, 0.1 W, 0603 resistor"),
    "R5K1": SupplierPart("YAGEO", "RC0603FR-075K1L", "311-5.10KHRCT-ND", "https://www.digikey.com/en/products/detail/yageo/RC0603FR-075K1L/727268", "5.1 kohm, 1%, 0.1 W, 0603 resistor"),
    "R10K": SupplierPart("YAGEO", "RC0603FR-0710KL", "311-10.0KHRCT-ND", "https://www.digikey.com/en/products/detail/yageo/RC0603FR-0710KL/726880", "10 kohm, 1%, 0.1 W, 0603 resistor"),
    "R47K": SupplierPart("YAGEO", "RC0603FR-0747KL", "311-47.0KHRCT-ND", "https://www.digikey.com/en/products/detail/yageo/RC0603FR-0747KL/727253", "47 kohm, 1%, 0.1 W, 0603 resistor"),
    "R100K": SupplierPart("YAGEO", "RC0603FR-07100KL", "311-100KHRCT-ND", "https://www.digikey.com/en/products/detail/yageo/RC0603FR-07100KL/726889", "100 kohm, 1%, 0.1 W, 0603 resistor"),
    "R330K": SupplierPart("YAGEO", "RC0603FR-07330KL", "311-330KHRCT-ND", "https://www.digikey.com/en/products/detail/yageo/RC0603FR-07330KL/727163", "330 kohm, 1%, 0.1 W, 0603 resistor"),
    "R1M": SupplierPart("YAGEO", "RC0603FR-071ML", "311-1.00MHRCT-ND", "https://www.digikey.com/en/products/detail/yageo/RC0603FR-071ML/729791", "1 Mohm, 1%, 0.1 W, 0603 resistor"),
    "R1K1": SupplierPart("YAGEO", "RC0603FR-071K1L", "311-1.10KHRCT-ND", "https://www.digikey.com/en/products/detail/yageo/RC0603FR-071K1L/726848", "1.1 kohm, 1%, 0.1 W, 0603 resistor"),
    "R4K7": SupplierPart("YAGEO", "RC0603FR-074K7L", "311-4.70KHRCT-ND", "https://www.digikey.com/en/products/detail/yageo/RC0603FR-074K7L/727212", "4.7 kohm, 1%, 0.1 W, 0603 resistor"),
    "C100N": SupplierPart("YAGEO", "CC0603KRX7R9BB104", "311-1344-1-ND", "https://www.digikey.com/en/products/detail/yageo/CC0603KRX7R9BB104/2103082", "100 nF, 50 V, X7R, 0603 capacitor"),
    "C1U": SupplierPart("Samsung Electro-Mechanics", "CL10A105KB8NNNC", "1276-1860-1-ND", "https://www.digikey.com/en/products/detail/samsung-electro-mechanics/CL10A105KB8NNNC/3887518", "1 uF, 50 V, X5R, 0603 capacitor"),
    "C10U": SupplierPart("Samsung Electro-Mechanics", "CL10A106KP8NNNC", "1276-1192-1-ND", "https://www.digikey.com/en/products/detail/samsung-electro-mechanics/CL10A106KP8NNNC/3886850", "10 uF, 10 V, X5R, 0603 capacitor"),
}


COMPONENTS: list[Component] = [
    Component("USB1", "USB4105-GF-A", "USB4105", 65.0, 75.0, {
        "1": "GND", "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND",
        "A4": "USB_VBUS", "A9": "USB_VBUS", "B4": "USB_VBUS", "B9": "USB_VBUS",
        "A5": "CC1", "B5": "CC2",
        "A6": "USB_DP_CONN", "B6": "USB_DP_CONN",
        "A7": "USB_DM_CONN", "B7": "USB_DM_CONN",
        "A8": None, "B8": None,
    }),
    Component("D1", "USBLC6-2SC6", "USBLC6", 145.0, 75.0, {
        "1": "USB_DP_CONN", "2": "GND", "3": "USB_DM_CONN",
        "4": "USB_OTG_DM", "5": "USB_VBUS", "6": "USB_OTG_DP",
    }),
    Component("U1", "BQ24075RGTR", "BQ24075", 95.0, 185.0, {
        "1": "CHG_TS", "2": "BAT", "3": "BAT", "4": "GND", "5": "SYS", "6": "GND",
        "7": "nPGOOD", "8": "GND", "9": "nCHG", "10": "SYS", "11": "SYS",
        "12": "CHG_ILIM", "13": "USB_VBUS", "14": "CHG_TMR", "15": "CHG_SYSOFF",
        "16": "CHG_ISET", "17": "GND",
    }),
    Component("J1", "S2B-PH-SM4-TB", "JST_PH_2", 35.0, 185.0, {"1": "BAT_RAW", "2": "GND"}),
    Component("U3", "TLV75533PDBVR", "TLV75533", 185.0, 185.0, {
        "1": "SYS", "2": "GND", "3": "SYS", "4": None, "5": "+3V3",
    }),
    Component("U4", "ESP32-S3-MINI-1-N8", "ESP32S3", 315.0, 180.0, {
        "1": "GND", "2": "GND", "3": "+3V3", "4": "BOOT_USER_BTN_N",
        "5": "BAT_SENSE", "6": "USB_VBUS_SENSE", "7": None,
        "8": "BMP581_INT", "9": "BMI323_INT1", "10": "BMI323_INT2",
        "11": "PWR_BTN_N", "12": "I2C_SCL", "13": "I2C_SDA",
        "14": "PWR_HOLD", "15": None, "16": None, "17": None, "18": None, "19": None,
        "20": None, "21": "BUZZER_PWM", "22": "BLE_LED_PWM",
        "23": "USB_OTG_DM", "24": "USB_OTG_DP", "25": None, "26": None,
        "27": None, "28": None, "29": None, "30": None, "31": None, "32": None,
        "33": "nCHG", "34": "nPGOOD", "35": None, "36": None, "37": None, "38": None,
        "39": None, "40": None, "41": None, "42": "GND", "43": "GND",
        "44": None, "45": "EN", "46": "GND", "47": "GND", "48": "GND",
        "49": "GND", "50": "GND", "51": "GND", "52": "GND", "53": "GND",
        "54": "GND", "55": "GND", "56": "GND", "57": "GND", "58": "GND",
        "59": "GND", "60": "GND", "GND": "GND",
    }),
    Component("SW1", "KMR211NG LFS", "BUTTON", 430.0, 135.0, {
        "1": "PWR_SW_N", "2": "PWR_SW_N", "3": "GND", "4": "GND",
    }),
    Component("SW2", "KMR211NG LFS", "BUTTON", 430.0, 78.0, {
        "1": "BOOT_USER_BTN_N", "2": "BOOT_USER_BTN_N", "3": "GND", "4": "GND",
    }),
    Component("SW3", "KMR211NG LFS", "BUTTON", 430.0, 105.0, {
        "1": "EN", "2": "EN", "3": "GND", "4": "GND",
    }),
    Component("U5", "BMP581", "BMP581", 520.0, 80.0, {
        "1": "+3V3", "2": "I2C_SCL", "3": "GND", "4": "I2C_SDA", "5": "GND",
        "6": "+3V3", "7": "BMP581_INT", "8": "GND", "9": "GND", "10": "+3V3",
    }),
    Component("U2", "BMI323", "BMI323", 520.0, 175.0, {
        "1": "GND", "2": None, "3": None, "4": "BMI323_INT1", "5": "+3V3",
        "6": "GND", "7": "GND", "8": "+3V3", "9": "BMI323_INT2",
        "10": None, "11": None, "12": "+3V3", "13": "I2C_SCL", "14": "I2C_SDA",
    }),
    Component("BZ1", "CSS-J4D20-SMT-TR", "BUZZER", 680.0, 80.0, {"1": "SYS", "2": "BUZZER_NEG"}),
    Component("Q1", "AO3400A", "AO3400A", 760.0, 80.0, {"1": "BUZZER_GATE", "2": "GND", "3": "BUZZER_NEG"}),
    Component("Q2", "AO3400A", "AO3400A", 760.0, 155.0, {"1": "BLE_LED_GATE", "2": "GND", "3": "BLE_LED_K"}),
    Component("Q3", "AO3400A", "AO3400A", 760.0, 210.0, {"1": "PWR_HOLD_GATE", "2": "GND", "3": "CHG_SYSOFF"}),
    Component("Q4", "DMP3098L", "DMP3098L", 760.0, 265.0, {"1": "BAT_SWITCH_GATE", "2": "BAT_RAW", "3": "BAT"}),
    Component("Q5", "AO3400A", "AO3400A", 760.0, 320.0, {"1": "PWR_HOLD_GATE", "2": "GND", "3": "BAT_SWITCH_GATE"}),
    Component("LED2", "LTST-C190GKT", "LED_GREEN", 680.0, 230.0, {"1": "GND", "2": "POWER_LED_A"}),
    Component("LED1", "LTST-C190TBKT", "LED_BLUE", 680.0, 155.0, {"1": "BLE_LED_K", "2": "BLE_LED_A"}),
    Component("D2", "1N4148W", "DIODE_1N4148W", 545.0, 315.0, {"1": "PWR_SW_N", "2": "PWR_BTN_N"}),
    Component("D3", "1N4148W", "DIODE_1N4148W", 595.0, 315.0, {"1": "PWR_SW_N", "2": "BAT_SWITCH_GATE"}),
    Component("D4", "1N4148W", "DIODE_1N4148W", 645.0, 315.0, {"1": "PWR_SW_N", "2": "CHG_SYSOFF"}),

    Component("C14", "1uF", "C1U", 55.0, 128.0, {"1": "USB_VBUS", "2": "GND"}),
    Component("R9", "5.1k", "R5K1", 115.0, 126.0, {"1": "CC1", "2": "GND"}),
    Component("R10", "5.1k", "R5K1", 115.0, 142.0, {"1": "CC2", "2": "GND"}),

    Component("C1", "10uF", "C10U", 35.0, 232.0, {"1": "BAT", "2": "GND"}),
    Component("C13", "10uF", "C10U", 150.0, 232.0, {"1": "SYS", "2": "GND"}),
    Component("C7", "1uF", "C1U", 200.0, 220.0, {"1": "SYS", "2": "GND"}),
    Component("C8", "1uF", "C1U", 200.0, 238.0, {"1": "+3V3", "2": "GND"}),
    Component("R15", "10k", "R10K", 25.0, 285.0, {"1": "CHG_TS", "2": "GND"}),
    Component("R12", "2k", "R2K", 75.0, 285.0, {"1": "CHG_ISET", "2": "GND"}),
    Component("R11", "1.1k", "R1K1", 125.0, 285.0, {"1": "CHG_ILIM", "2": "GND"}),
    Component("R14", "47k", "R47K", 175.0, 285.0, {"1": "CHG_TMR", "2": "GND"}),
    Component("R13", "10k", "R10K", 225.0, 285.0, {"1": "nCHG", "2": "+3V3"}),
    Component("R19", "10k", "R10K", 275.0, 285.0, {"1": "nPGOOD", "2": "+3V3"}),
    Component("R23", "1M", "R1M", 325.0, 285.0, {"1": "CHG_SYSOFF", "2": "BAT"}),
    Component("R24", "100k", "R100K", 375.0, 285.0, {"1": "PWR_HOLD_GATE", "2": "+3V3"}),
    Component("R25", "100R", "R100", 425.0, 285.0, {"1": "PWR_HOLD", "2": "PWR_HOLD_GATE"}),
    Component("R26", "1M", "R1M", 475.0, 285.0, {"1": "PWR_HOLD_GATE", "2": "GND"}),
    Component("R28", "1M", "R1M", 525.0, 285.0, {"1": "BAT_SWITCH_GATE", "2": "BAT_RAW"}),

    Component("C9", "10uF", "C10U", 255.0, 255.0, {"1": "+3V3", "2": "GND"}),
    Component("C10", "100nF", "C100N", 305.0, 255.0, {"1": "+3V3", "2": "GND"}),
    Component("R16", "10k", "R10K", 365.0, 255.0, {"1": "EN", "2": "+3V3"}),
    Component("C4", "100nF", "C100N", 415.0, 255.0, {"1": "EN", "2": "GND"}),
    Component("R6", "10k", "R10K", 465.0, 255.0, {"1": "BOOT_USER_BTN_N", "2": "+3V3"}),
    Component("R27", "4.7k", "R4K7", 515.0, 255.0, {"1": "PWR_BTN_N", "2": "+3V3"}),
    Component("R2", "1M", "R1M", 260.0, 315.0, {"1": "BAT", "2": "BAT_SENSE"}),
    Component("R1", "1M", "R1M", 310.0, 315.0, {"1": "BAT_SENSE", "2": "GND"}),
    Component("C2", "100nF", "C100N", 360.0, 315.0, {"1": "BAT_SENSE", "2": "GND"}),
    Component("R22", "1M", "R1M", 410.0, 315.0, {"1": "USB_VBUS", "2": "USB_VBUS_SENSE"}),
    Component("R21", "330k", "R330K", 460.0, 315.0, {"1": "USB_VBUS_SENSE", "2": "GND"}),

    Component("C12", "100nF", "C100N", 575.0, 35.0, {"1": "+3V3", "2": "GND"}),
    Component("C11", "100nF", "C100N", 625.0, 35.0, {"1": "+3V3", "2": "GND"}),
    Component("C6", "100nF", "C100N", 575.0, 230.0, {"1": "+3V3", "2": "GND"}),
    Component("C5", "100nF", "C100N", 625.0, 230.0, {"1": "+3V3", "2": "GND"}),
    Component("R17", "4.7k", "R4K7", 575.0, 285.0, {"1": "I2C_SCL", "2": "+3V3"}),
    Component("R18", "4.7k", "R4K7", 625.0, 285.0, {"1": "I2C_SDA", "2": "+3V3"}),

    Component("C3", "10uF", "C10U", 680.0, 35.0, {"1": "SYS", "2": "GND"}),
    Component("R8", "100R", "R100", 830.0, 75.0, {"1": "BUZZER_PWM", "2": "BUZZER_GATE"}),
    Component("R7", "100k", "R100K", 830.0, 95.0, {"1": "BUZZER_GATE", "2": "GND"}),
    Component("R5", "1k", "R1K", 830.0, 150.0, {"1": "SYS", "2": "BLE_LED_A"}),
    Component("R4", "100R", "R100", 830.0, 170.0, {"1": "BLE_LED_PWM", "2": "BLE_LED_GATE"}),
    Component("R3", "100k", "R100K", 830.0, 190.0, {"1": "BLE_LED_GATE", "2": "GND"}),
    Component("R20", "1k", "R1K", 760.0, 230.0, {"1": "+3V3", "2": "POWER_LED_A"}),
]


def tokenize(text: str) -> list[str | tuple[str, str]]:
    tokens: list[str | tuple[str, str]] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "()":
            tokens.append(ch)
            i += 1
            continue
        if ch == '"':
            i += 1
            out = []
            while i < len(text):
                if text[i] == "\\" and i + 1 < len(text):
                    out.append(text[i + 1])
                    i += 2
                    continue
                if text[i] == '"':
                    i += 1
                    break
                out.append(text[i])
                i += 1
            tokens.append(("str", "".join(out)))
            continue
        j = i
        while j < len(text) and not text[j].isspace() and text[j] not in "()":
            j += 1
        tokens.append(text[i:j])
        i = j
    return tokens


def parse(tokens: list[str | tuple[str, str]]):
    i = 0

    def rec():
        nonlocal i
        if tokens[i] != "(":
            token = tokens[i]
            i += 1
            return token[1] if isinstance(token, tuple) else token
        i += 1
        items = []
        while tokens[i] != ")":
            items.append(rec())
        i += 1
        return items

    return rec()


def find_top_symbol(ast) -> list:
    for item in ast:
        if isinstance(item, list) and item and item[0] == "symbol":
            return item
    raise ValueError("symbol not found")


def pins_for_kind(kind: Kind) -> dict[str, Pin]:
    text = (PARTS / kind.lib / kind.symfile).read_text()
    ast = parse(tokenize(text))
    symbol = find_top_symbol(ast)
    pins: dict[str, Pin] = {}

    def walk(node):
        if not isinstance(node, list):
            return
        if node and node[0] == "pin":
            at = next(item for item in node if isinstance(item, list) and item and item[0] == "at")
            name = next(item for item in node if isinstance(item, list) and item and item[0] == "name")
            number = next(item for item in node if isinstance(item, list) and item and item[0] == "number")
            pins[str(number[1])] = Pin(str(number[1]), str(name[1]), float(at[1]), float(at[2]), int(float(at[3])))
        for item in node:
            walk(item)

    walk(symbol)
    return pins


def extract_symbol_block(kind: Kind) -> str:
    text = (PARTS / kind.lib / kind.symfile).read_text()
    match = re.search(r'\(symbol\s+"' + re.escape(kind.symbol) + r'"', text)
    if not match:
        raise ValueError(f"{kind.symbol} not found in {kind.symfile}")
    start = match.start()
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                block = text[start : i + 1]
                block = re.sub(
                    r"\(effects \(font \(size ([0-9.]+) ([0-9.]+)\)\) hide\)",
                    r"(effects (font (size \1 \2)) (hide yes))",
                    block,
                )
                return re.sub(r'\(symbol\s+"[^"]+"', f'(symbol "{kind.lib}:{kind.symbol}"', block, count=1)
    raise ValueError(f"unterminated symbol in {kind.symfile}")


def schematic_symbol_name(kind_key: str) -> str:
    if kind_key.startswith("R"):
        return "R"
    if kind_key.startswith("C"):
        return "C"
    return KINDS[kind_key].symbol


def ref_prefix(symbol_name: str) -> str:
    if symbol_name == "USB4105-GF-A":
        return "USB"
    if symbol_name == "USBLC6-2SC6":
        return "D"
    if symbol_name == "1N4148W":
        return "D"
    if symbol_name == "CSS-J4D20-SMT-TR":
        return "BZ"
    if symbol_name in {"AO3400A", "DMP3098L"}:
        return "Q"
    if symbol_name == "KMR211NG_LFS":
        return "SW"
    if symbol_name.startswith("LTST"):
        return "LED"
    if symbol_name.startswith("S2B") or symbol_name.startswith("Optional"):
        return "J"
    if symbol_name == "R":
        return "R"
    if symbol_name == "C":
        return "C"
    return "U"


def pin_inner_xy(pin: Pin, pin_length: float = 2.54) -> tuple[float, float]:
    if pin.angle == 0:
        return pin.x + pin_length, pin.y
    if pin.angle == 180:
        return pin.x - pin_length, pin.y
    if pin.angle == 90:
        return pin.x, pin.y + pin_length
    if pin.angle == 270:
        return pin.x, pin.y - pin_length
    return pin.x, pin.y


def custom_symbol_block(symbol_name: str, pins: dict[str, Pin], cached: bool) -> str:
    top_name = f"FlySys:{symbol_name}" if cached else symbol_name
    child_name = f"{symbol_name}_0_1"
    inner = [pin_inner_xy(pin) for pin in pins.values()]
    left = min(x for x, _ in inner) - 1.27
    right = max(x for x, _ in inner) + 1.27
    top = max(y for _, y in inner) + 1.27
    bottom = min(y for _, y in inner) - 1.27

    lines = [
        f'\t\t(symbol "{top_name}"' if cached else f'\t(symbol "{top_name}"',
        "\t\t\t(pin_names" if cached else "\t\t(pin_names",
        "\t\t\t\t(offset 0.508)" if cached else "\t\t\t(offset 0.508)",
        "\t\t\t)" if cached else "\t\t)",
        "\t\t\t(exclude_from_sim no)" if cached else "\t\t(exclude_from_sim no)",
        "\t\t\t(in_bom yes)" if cached else "\t\t(in_bom yes)",
        "\t\t\t(on_board yes)" if cached else "\t\t(on_board yes)",
        f'\t\t\t(property "Reference" "{ref_prefix(symbol_name)}"' if cached else f'\t\t(property "Reference" "{ref_prefix(symbol_name)}"',
        "\t\t\t\t(id 0)" if cached else "\t\t\t(id 0)",
        f"\t\t\t\t(at 0 {fmt(top + 5.0)} 0)" if cached else f"\t\t\t(at 0 {fmt(top + 5.0)} 0)",
        ("\t" + effects()).replace("\n", "\n\t") if cached else symbol_lib_effects(),
        "\t\t\t)" if cached else "\t\t)",
        f'\t\t\t(property "Value" "{symbol_name}"' if cached else f'\t\t(property "Value" "{symbol_name}"',
        "\t\t\t\t(id 1)" if cached else "\t\t\t(id 1)",
        f"\t\t\t\t(at 0 {fmt(bottom - 5.0)} 0)" if cached else f"\t\t\t(at 0 {fmt(bottom - 5.0)} 0)",
        ("\t" + effects()).replace("\n", "\n\t") if cached else symbol_lib_effects(),
        "\t\t\t)" if cached else "\t\t)",
        f'\t\t\t(property "Footprint" ""' if cached else f'\t\t(property "Footprint" ""',
        "\t\t\t\t(id 2)" if cached else "\t\t\t(id 2)",
        f"\t\t\t\t(at 0 {fmt(bottom - 8.0)} 0)" if cached else f"\t\t\t(at 0 {fmt(bottom - 8.0)} 0)",
        ("\t" + effects(hide=True)).replace("\n", "\n\t") if cached else symbol_lib_effects(hide=True),
        "\t\t\t)" if cached else "\t\t)",
        f'\t\t\t(property "Datasheet" ""' if cached else f'\t\t(property "Datasheet" ""',
        "\t\t\t\t(id 3)" if cached else "\t\t\t(id 3)",
        "\t\t\t\t(at 0 0 0)" if cached else "\t\t\t(at 0 0 0)",
        ("\t" + effects(hide=True)).replace("\n", "\n\t") if cached else symbol_lib_effects(hide=True),
        "\t\t\t)" if cached else "\t\t)",
        f'\t\t\t(property "Description" ""' if cached else f'\t\t(property "Description" ""',
        "\t\t\t\t(id 4)" if cached else "\t\t\t(id 4)",
        "\t\t\t\t(at 0 0 0)" if cached else "\t\t\t(at 0 0 0)",
        ("\t" + effects(hide=True)).replace("\n", "\n\t") if cached else symbol_lib_effects(hide=True),
        "\t\t\t)" if cached else "\t\t)",
        f'\t\t\t(symbol "{child_name}"' if cached else f'\t\t(symbol "{child_name}"',
        f"\t\t\t\t(rectangle" if cached else "\t\t\t(rectangle",
        f"\t\t\t\t\t(start {fmt(left)} {fmt(top)})" if cached else f"\t\t\t\t(start {fmt(left)} {fmt(top)})",
        f"\t\t\t\t\t(end {fmt(right)} {fmt(bottom)})" if cached else f"\t\t\t\t(end {fmt(right)} {fmt(bottom)})",
        "\t\t\t\t\t(stroke" if cached else "\t\t\t\t(stroke",
        "\t\t\t\t\t\t(width 0.254)" if cached else "\t\t\t\t\t(width 0.254)",
        "\t\t\t\t\t\t(type default)" if cached else "\t\t\t\t\t(type default)",
        "\t\t\t\t\t)" if cached else "\t\t\t\t)",
        "\t\t\t\t\t(fill" if cached else "\t\t\t\t(fill",
        "\t\t\t\t\t\t(type background)" if cached else "\t\t\t\t\t(type background)",
        "\t\t\t\t\t)" if cached else "\t\t\t\t)",
        "\t\t\t\t)" if cached else "\t\t\t)",
    ]
    for number in sorted(pins, key=lambda v: (len(v), v)):
        pin = pins[number]
        prefix = "\t\t\t\t" if cached else "\t\t\t"
        lines.extend([
            f'{prefix}(pin passive line',
            f'{prefix}\t(at {fmt(pin.x)} {fmt(pin.y)} {pin.angle})',
            f'{prefix}\t(length 2.54)',
            f'{prefix}\t(name "{pin.name}"',
            f'{prefix}\t\t(effects',
            f'{prefix}\t\t\t(font',
            f'{prefix}\t\t\t\t(size 1.00 1.00)',
            f'{prefix}\t\t\t)',
            f'{prefix}\t\t)',
            f'{prefix}\t)',
            f'{prefix}\t(number "{pin.number}"',
            f'{prefix}\t\t(effects',
            f'{prefix}\t\t\t(font',
            f'{prefix}\t\t\t\t(size 1.00 1.00)',
            f'{prefix}\t\t\t)',
            f'{prefix}\t\t)',
            f'{prefix}\t)',
            f'{prefix})',
        ])
    lines.extend([
        "\t\t\t)" if cached else "\t\t)",
        "\t\t)" if cached else "\t)",
    ])
    return "\n".join(lines)


def q(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def fmt(value: float) -> str:
    if abs(value) < 0.0005:
        value = 0.0
    return f"{value:.2f}"


def snap(value: float, grid: float = GRID_MM) -> float:
    return round(value / grid) * grid


def uid(*parts: object) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "flysys-vario/" + "/".join(map(str, parts))))


def effects(size: str = "1.27", hide: bool = False, justify: str | None = None) -> str:
    hide_line = "\n\t\t\t\t(hide yes)" if hide else ""
    justify_line = f"\n\t\t\t\t(justify {justify})" if justify else ""
    return (
        "\t\t\t(effects\n"
        "\t\t\t\t(font\n"
        f"\t\t\t\t\t(size {size} {size})\n"
        "\t\t\t\t)"
        f"{hide_line}{justify_line}\n"
        "\t\t\t)"
    )


def symbol_lib_effects(size: str = "1.27", hide: bool = False) -> str:
    hide_text = " hide" if hide else ""
    return f"\t\t\t(effects (font (size {size} {size})){hide_text})"


def label_justify(angle: int) -> str:
    if angle == 0:
        return "right bottom"
    if angle == 180:
        return "left bottom"
    if angle == 90:
        return "left bottom"
    return "right bottom"


def outward(angle: int, length: float = 5.08) -> tuple[float, float, int]:
    if angle == 0:
        return (-length, 0.0, 180)
    if angle == 180:
        return (length, 0.0, 0)
    if angle == 90:
        return (0.0, length, 90)
    if angle == 270:
        return (0.0, -length, 270)
    raise ValueError(f"unsupported pin angle {angle}")


def pin_sheet_xy(component: Component, pin: Pin) -> tuple[float, float]:
    # KiCad symbol library coordinates use positive Y upward; schematic sheet
    # coordinates use positive Y downward.
    return snap(component.x) + pin.x, snap(component.y) - pin.y


def component_symbol(component: Component, pins: dict[str, Pin]) -> str:
    kind = KINDS[component.kind]
    supplier = DIGIKEY_PARTS[component.kind]
    lib_id = f"FlySys:{schematic_symbol_name(component.kind)}"
    cx = snap(component.x)
    cy = snap(component.y)
    ys = [pin.y for pin in pins.values()]
    ref_y = cy - max(ys) - 5.0
    value_y = cy - min(ys) + 5.0
    lines = [
        "\t(symbol",
        f"\t\t(lib_id {q(lib_id)})",
        f"\t\t(at {fmt(cx)} {fmt(cy)} 0)",
        "\t\t(unit 1)",
        "\t\t(exclude_from_sim no)",
        f"\t\t(in_bom {'yes' if supplier.in_bom else 'no'})",
        "\t\t(on_board yes)",
        "\t\t(dnp no)",
        f"\t\t(uuid {q(uid(component.ref, 'symbol'))})",
        f"\t\t(property {q('Reference')} {q(component.ref)}",
        f"\t\t\t(at {fmt(cx)} {fmt(ref_y)} 0)",
        effects(),
        "\t\t)",
        f"\t\t(property {q('Value')} {q(component.value)}",
        f"\t\t\t(at {fmt(cx)} {fmt(value_y)} 0)",
        effects(),
        "\t\t)",
        f"\t\t(property {q('Footprint')} {q(kind.footprint)}",
        f"\t\t\t(at {fmt(cx)} {fmt(value_y + 3.0)} 0)",
        effects(hide=True),
        "\t\t)",
        f"\t\t(property {q('Datasheet')} {q('')}",
        f"\t\t\t(at {fmt(cx)} {fmt(cy)} 0)",
        effects(hide=True),
        "\t\t)",
        f"\t\t(property {q('Description')} {q(supplier.description)}",
        f"\t\t\t(at {fmt(cx)} {fmt(cy)} 0)",
        effects(hide=True),
        "\t\t)",
        f"\t\t(property {q('Manufacturer')} {q(supplier.manufacturer)}",
        f"\t\t\t(at {fmt(cx)} {fmt(cy)} 0)",
        effects(hide=True),
        "\t\t)",
        f"\t\t(property {q('MPN')} {q(supplier.mpn)}",
        f"\t\t\t(at {fmt(cx)} {fmt(cy)} 0)",
        effects(hide=True),
        "\t\t)",
        f"\t\t(property {q('Supplier')} {q(supplier.supplier)}",
        f"\t\t\t(at {fmt(cx)} {fmt(cy)} 0)",
        effects(hide=True),
        "\t\t)",
        f"\t\t(property {q('DigiKey Part Number')} {q(supplier.digikey_pn)}",
        f"\t\t\t(at {fmt(cx)} {fmt(cy)} 0)",
        effects(hide=True),
        "\t\t)",
        f"\t\t(property {q('DigiKey URL')} {q(supplier.digikey_url)}",
        f"\t\t\t(at {fmt(cx)} {fmt(cy)} 0)",
        effects(hide=True),
        "\t\t)",
    ]
    for number in sorted(pins, key=lambda v: (len(v), v)):
        lines.extend([
            f"\t\t(pin {q(number)}",
            f"\t\t\t(uuid {q(uid(component.ref, 'pin', number))})",
            "\t\t)",
        ])
    lines.extend([
        "\t\t(instances",
        f"\t\t\t(project {q(PROJECT)}",
        f"\t\t\t\t(path {q('/' + str(SHEET_UUID))}",
        f"\t\t\t\t\t(reference {q(component.ref)})",
        "\t\t\t\t\t(unit 1)",
        "\t\t\t\t)",
        "\t\t\t)",
        "\t\t)",
        "\t)",
    ])
    return "\n".join(lines)


def wire_item(key: tuple[object, ...], x1: float, y1: float, x2: float, y2: float) -> str | None:
    if abs(x1 - x2) < 0.001 and abs(y1 - y2) < 0.001:
        return None
    return (
        "\t(wire\n"
        "\t\t(pts\n"
        f"\t\t\t(xy {fmt(x1)} {fmt(y1)}) (xy {fmt(x2)} {fmt(y2)})\n"
        "\t\t)\n"
        "\t\t(stroke\n"
        "\t\t\t(width 0)\n"
        "\t\t\t(type solid)\n"
        "\t\t)\n"
        f"\t\t(uuid {q(uid(*key))})\n"
        "\t)"
    )


def junction_item(key: tuple[object, ...], x: float, y: float) -> str:
    return (
        "\t(junction\n"
        f"\t\t(at {fmt(x)} {fmt(y)})\n"
        "\t\t(diameter 0)\n"
        "\t\t(color 0 0 0 0)\n"
        f"\t\t(uuid {q(uid(*key))})\n"
        "\t)"
    )


def no_connect_item(component: Component, number: str, pin: Pin) -> str:
    x, y = pin_sheet_xy(component, pin)
    return (
        "\t(no_connect\n"
        f"\t\t(at {fmt(x)} {fmt(y)})\n"
        f"\t\t(uuid {q(uid(component.ref, 'nc', number))})\n"
        "\t)"
    )


def schematic_connection_items(pins_by_kind: dict[str, dict[str, Pin]]) -> list[str]:
    items: list[str] = []
    nodes_by_net: dict[str, list[tuple[Component, str, Pin, float, float, float, float]]] = {}

    for component in COMPONENTS:
        pins = pins_by_kind[component.kind]
        for number, net in component.pins.items():
            pin = pins[number]
            if net is None:
                items.append(no_connect_item(component, number, pin))
                continue
            pin_x, pin_y = pin_sheet_xy(component, pin)
            dx, dy, _ = outward(pin.angle)
            escape_x = pin_x + dx
            escape_y = pin_y + dy
            nodes_by_net.setdefault(net, []).append((component, number, pin, pin_x, pin_y, escape_x, escape_y))
            wire = wire_item((component.ref, "escape", number), pin_x, pin_y, escape_x, escape_y)
            if wire:
                items.append(wire)

    preferred_order = [
        "GND", "+3V3", "SYS", "BAT_RAW", "BAT", "USB_VBUS",
        "USB_DP_CONN", "USB_DM_CONN", "USB_OTG_DP", "USB_OTG_DM",
        "I2C_SCL", "I2C_SDA", "EN", "BOOT_USER_BTN_N",
        "PWR_SW_N", "PWR_BTN_N", "CHG_SYSOFF", "PWR_HOLD", "PWR_HOLD_GATE", "BAT_SWITCH_GATE",
        "BAT_SENSE", "USB_VBUS_SENSE", "nCHG", "nPGOOD",
        "BUZZER_PWM", "BUZZER_GATE", "BUZZER_NEG",
        "BLE_LED_PWM", "BLE_LED_GATE", "BLE_LED_A", "BLE_LED_K", "POWER_LED_A",
    ]
    ordered_nets = [net for net in preferred_order if net in nodes_by_net]
    ordered_nets.extend(sorted(net for net in nodes_by_net if net not in set(ordered_nets)))
    trunk_start_y = 365.76
    trunk_step = 5.08

    for index, net in enumerate(ordered_nets):
        nodes = nodes_by_net[net]
        trunk_y = trunk_start_y + index * trunk_step
        min_x = min(node[5] for node in nodes) - 5.08
        max_x = max(node[5] for node in nodes) + 5.08

        if len(nodes) > 1:
            wire = wire_item((net, "trunk"), min_x, trunk_y, max_x, trunk_y)
            if wire:
                items.append(wire)

        items.append(
            f"\t(label {q(net)}\n"
            f"\t\t(at {fmt(min_x)} {fmt(trunk_y)} 180)\n"
            f"{effects('1.00', justify='right bottom')}\n"
            f"\t\t(uuid {q(uid(net, 'trunk-label'))})\n"
            "\t)"
        )

        for component, number, _pin, _pin_x, _pin_y, escape_x, escape_y in nodes:
            wire = wire_item((component.ref, "drop", number, net), escape_x, escape_y, escape_x, trunk_y)
            if wire:
                items.append(wire)
            items.append(junction_item((component.ref, "junction", number, net), escape_x, trunk_y))

    return items


def label_connection_items(pins_by_kind: dict[str, dict[str, Pin]]) -> list[str]:
    items: list[str] = []
    for component in COMPONENTS:
        pins = pins_by_kind[component.kind]
        for number, net in component.pins.items():
            pin = pins[number]
            x1, y1 = pin_sheet_xy(component, pin)
            if net is None:
                items.append(no_connect_item(component, number, pin))
                continue
            dx, dy, label_angle = outward(pin.angle)
            x2, y2 = x1 + dx, y1 + dy
            wire = wire_item((component.ref, "wire", number), x1, y1, x2, y2)
            if wire:
                items.append(wire)
            items.append(
                f"\t(label {q(net)}\n"
                f"\t\t(at {fmt(x2)} {fmt(y2)} {label_angle})\n"
                f"{effects('1.00', justify=label_justify(label_angle))}\n"
                f"\t\t(uuid {q(uid(component.ref, 'label', number))})\n"
                "\t)"
            )
    return items


def validate() -> dict[str, dict[str, Pin]]:
    pins_by_kind = {key: pins_for_kind(kind) for key, kind in KINDS.items()}
    refs = set()
    for component in COMPONENTS:
        if component.ref in refs:
            raise ValueError(f"duplicate reference {component.ref}")
        refs.add(component.ref)
        available = set(pins_by_kind[component.kind])
        configured = set(component.pins)
        if available != configured:
            missing = sorted(available - configured)
            extra = sorted(configured - available)
            raise ValueError(f"{component.ref} pin mismatch: missing={missing}, extra={extra}")
    missing_supplier = sorted(
        {
            component.kind
            for component in COMPONENTS
            if component.kind not in DIGIKEY_PARTS
            or (DIGIKEY_PARTS[component.kind].in_bom and not DIGIKEY_PARTS[component.kind].digikey_pn)
        }
    )
    if missing_supplier:
        raise ValueError(f"missing DigiKey supplier mapping: {missing_supplier}")
    return pins_by_kind


def write_tables(used_kinds: list[Kind]) -> None:
    libs = sorted({kind.lib for kind in used_kinds})
    sym_entries = [
        "(sym_lib_table",
        "\t(version 7)",
        "\t(lib",
        "\t\t(name \"FlySys\")",
        "\t\t(type \"KiCad\")",
        "\t\t(uri \"${KIPRJMOD}/flysys_symbols.kicad_sym\")",
        "\t\t(options \"\")",
        "\t\t(descr \"FlySys generated schematic symbols\")",
        "\t)",
    ]
    fp_entries = ["(fp_lib_table", "\t(version 7)"]
    for lib in libs:
        fp_entries.extend([
            "\t(lib",
            f"\t\t(name {q(lib)})",
            "\t\t(type \"KiCad\")",
            f"\t\t(uri {q('${KIPRJMOD}/../parts/' + lib)})",
            "\t\t(options \"\")",
            "\t\t(descr \"FlySys local footprint library\")",
            "\t)",
        ])
    sym_entries.append(")")
    fp_entries.append(")")
    (KICAD / "sym-lib-table").write_text("\n".join(sym_entries) + "\n")
    (KICAD / "fp-lib-table").write_text("\n".join(fp_entries) + "\n")


def write_symbol_library(symbols: dict[str, dict[str, Pin]]) -> None:
    lines = [
        "(kicad_symbol_lib",
        "\t(version 20220914)",
        "\t(generator codex)",
    ]
    for symbol_name in sorted(symbols):
        lines.append(custom_symbol_block(symbol_name, symbols[symbol_name], cached=False))
    lines.append(")")
    (KICAD / "flysys_symbols.kicad_sym").write_text("\n".join(lines) + "\n")


def write_project() -> None:
    pro = KICAD / f"{PROJECT}.kicad_pro"
    if pro.exists():
        return
    pro.write_text('{\n  "meta": {\n    "version": 1\n  },\n  "project": {\n    "files": []\n  }\n}\n')


def split_ref(ref: str) -> tuple[str, int]:
    match = re.match(r"([A-Za-z]+)(\d+)$", ref)
    if not match:
        return ref, 0
    return match.group(1), int(match.group(2))


def grouped_digikey_bom() -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[Component]] = defaultdict(list)
    for component in COMPONENTS:
        supplier = DIGIKEY_PARTS[component.kind]
        if not supplier.in_bom:
            continue
        grouped[(supplier.manufacturer, supplier.mpn)].append(component)

    rows: list[dict[str, str]] = []
    for (_manufacturer, _mpn), components in sorted(grouped.items()):
        first = components[0]
        supplier = DIGIKEY_PARTS[first.kind]
        refs = sorted((component.ref for component in components), key=split_ref)
        values = sorted({component.value for component in components})
        rows.append(
            {
                "References": ", ".join(refs),
                "Quantity": str(len(components)),
                "Value": ", ".join(values),
                "Manufacturer": supplier.manufacturer,
                "MPN": supplier.mpn,
                "DigiKey Part Number": supplier.digikey_pn,
                "Supplier": supplier.supplier,
                "DigiKey URL": supplier.digikey_url,
                "Description": supplier.description,
            }
        )
    return rows


def write_digikey_bom() -> None:
    rows = grouped_digikey_bom()
    fields = [
        "References",
        "Quantity",
        "Value",
        "Manufacturer",
        "MPN",
        "DigiKey Part Number",
        "Supplier",
        "DigiKey URL",
        "Description",
    ]

    csv_path = KICAD / f"{PROJECT}_digikey_bom.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    md_lines = [
        "# FlySys DigiKey BOM",
        "",
        "Updated: 2026-06-02",
        "",
        "All purchased components in the KiCad schematic use DigiKey order lines. Debug pads are not fitted; ESP32-S3 bootloader entry uses USB plus the BOOT and RESET buttons.",
        "",
        "| References | Qty | Value | Manufacturer | MPN | DigiKey PN | Description |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        md_lines.append(
            "| {References} | {Quantity} | {Value} | {Manufacturer} | {MPN} | [{DigiKey Part Number}]({DigiKey URL}) | {Description} |".format(**row)
        )
    md_lines.extend(
        [
            "",
            "Note: Atopile 0.15.7 currently supports only LCSC in its built-in `has_part_picked` BOM path. The DigiKey BOM above is therefore generated by this project script and is the procurement source of truth.",
            "",
        ]
    )
    (docs / "digikey-bom.md").write_text("\n".join(md_lines), encoding="utf-8")


def main() -> None:
    KICAD.mkdir(exist_ok=True)
    pins_by_kind = validate()
    used_kinds = [KINDS[key] for key in sorted({component.kind for component in COMPONENTS})]
    write_tables(used_kinds)
    write_project()

    schematic_symbols: dict[str, dict[str, Pin]] = {}
    for component in COMPONENTS:
        symbol_name = schematic_symbol_name(component.kind)
        schematic_symbols.setdefault(symbol_name, pins_by_kind[component.kind])
    write_symbol_library(schematic_symbols)
    write_digikey_bom()

    lib_blocks = [
        custom_symbol_block(symbol_name, schematic_symbols[symbol_name], cached=True)
        for symbol_name in sorted(schematic_symbols)
    ]
    symbols = [component_symbol(component, pins_by_kind[component.kind]) for component in COMPONENTS]
    graphics = label_connection_items(pins_by_kind)

    schematic = [
        "(kicad_sch",
        "\t(version 20250114)",
        "\t(generator \"codex\")",
        "\t(generator_version \"1.0\")",
        f"\t(uuid {q(str(SHEET_UUID))})",
        "\t(paper \"A0\")",
        "\t(title_block",
        "\t\t(title \"FlySys Vario\")",
        "\t\t(date \"2026-06-01\")",
        "\t\t(rev \"A\")",
        "\t\t(company \"FlySys\")",
        "\t\t(comment 1 \"KiCad schematic generated from main.ato net plan\")",
        "\t)",
        "\t(lib_symbols",
    ]
    schematic.extend("\n".join("\t\t" + line if line else "" for line in block.splitlines()) for block in lib_blocks)
    schematic.append("\t)")
    schematic.extend(graphics)
    schematic.extend(symbols)
    schematic.extend([
        "\t(sheet_instances",
        "\t\t(path \"/\"",
        "\t\t\t(page \"1\")",
        "\t\t)",
        "\t)",
        ")",
        "",
    ])
    (KICAD / f"{PROJECT}.kicad_sch").write_text("\n".join(schematic))


if __name__ == "__main__":
    main()
