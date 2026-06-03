# FlySys Firmware Update UX

Updated: 2026-06-03

Normal firmware update is handled by application firmware. The hidden physical
BOOT and RESET controls are retained only as a recovery fallback when the
application updater is unavailable or a broken image cannot boot.

## User-Facing Update Path

Primary update entry is software-controlled while USB or another supported link
is connected. The firmware implementation may use USB MSC drag-and-drop, a USB
CDC update tool, BLE DFU, or OTA, but it must validate the new image before
activating it.

Use ESP-IDF OTA partitions with rollback. After rebooting into a new image,
firmware must mark the image valid only after the normal boot checks pass. If
the new image fails those checks or cannot confirm itself, rollback should return
the device to the previous working image.

## USB-Attached Idle Mode

USB-C attach is allowed to power the ESP32-S3 electrically. Firmware must decide
whether the user asked for the vario application to run.

At boot:

1. Read `USB_VBUS_SENSE`.
2. Read the persisted/current user power-intent state.
3. If USB is present and the user has not pressed `POWER`, enter
   USB-attached idle mode.
4. If `POWER` has been pressed, record user intent and start normal mode.

In USB-attached idle mode, do not start:

- Vario sensing/filtering.
- BLE advertising or normal BLE telemetry.
- Buzzer output.
- Flight logging or log rotation.
- Any normal flight behavior.

Allowed idle functions are limited to charging/status indication, the firmware
update endpoint, and an optional command that records user intent and starts
normal mode.

## Hidden Recovery Controls

Keep the physical recovery controls on the PCB but place them behind service
pinholes or another non-user-facing access path:

| Control | Net | Electrical behavior | PCB/service label |
| --- | --- | --- | --- |
| BOOT | `BOOT_USER_BTN_N` / ESP32-S3 `GPIO0` | Momentary short to `GND`; `R6` pulls up to `+3V3` | `BOOT` |
| RESET | `EN` | Momentary short to `GND`; `R16` pulls up to `+3V3`, `C4` provides 100 nF reset RC | `RST` |

Document these controls as recovery-only in user and service material. They are
not the normal firmware update workflow.

## Recovery Sequence

1. Connect USB-C.
2. Hold hidden `BOOT`.
3. Press and release hidden `RST`.
4. Release `BOOT`.
5. Run the ESP32-S3 flashing/recovery tool against the native USB ROM
   bootloader.

If a service setup must keep the board powered from battery before USB is
attached, press `POWER` first to latch the board; recovery flashing still
requires USB.

## Verification

- USB attach from off state: ESP32-S3 may power up, but firmware remains in
  USB-attached idle mode. Vario sensing, buzzer, BLE normal operation, and
  logging stay inactive.
- Start normal mode: with USB connected, press `POWER`; firmware exits idle mode
  and starts the main application.
- Software update: update through the selected firmware endpoint; verify image
  validation, reboot, and rollback behavior.
- Physical recovery: hold `BOOT`, tap `RST`, release `BOOT`; confirm the host
  detects the ESP32-S3 native USB ROM bootloader and flashing works.
- Failure fallback: install intentionally broken application firmware and verify
  hidden `BOOT` + `RST` recovery still works.
