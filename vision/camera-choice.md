# Overhead camera choice (2026-11-14)

## TL;DR
- **Decision (D-026):** buy the **Raspberry Pi Camera Module 3 Wide (SC0874)**: 2BTrading, 275 TND, in stock
  on 2026-11-14. It is the only camera sold in Tunisia that is both wide enough and fast enough for the overhead station.
- **Setup:** camera → Raspberry Pi (4 or 5) → **Ethernet cable** → laptop. The Pi only grabs and sends frames;
  **all processing (ArUco, tracking) runs on the laptop**. Only the laptop ↔ robot link is wireless (D-008).
- **To test first:** a printed 70 mm marker in the far corners. At 56 fps it is only ~24 × 12 px there (borderline).
- Imported alternatives (not chosen): Arducam B0433 12MP USB, 110° H, 4K30 (~€69); Arducam USB version of the
  Camera Module 3 Wide (~$72). Both plug straight into the laptop.

## What the camera must do
- Station position [GR G.4]: platform on the central axis of the bottom long edge, 70 mm above the table, 22 mm
  thick; device up to 1.6 m above the platform → camera at most **~1.69 m above the table**, roughly above the edge,
  on our colour's half of the platform.
- To see the whole table plus robot markers at 430 mm from there: about **100° horizontal × 70° vertical**
  (pinhole estimate; it grows fast if the camera is lower: ~117° × 88° at 1.4 m).
- Must read the robot markers (70 mm ArUco 4×4 [GR G.6]) at the far corners at ≥ 30 fps. Aerobotix's 10 Hz was
  too slow for an opponent at 1 m/s.

## Candidates found in Tunisia (2026-11-14)
Shops searched: SELI, Little Son, 2BTrading, Didactico, Celectronix, Tunisianet, Spacenet, Zoom (Mytek and Wiki
blocked automated search; both are general IT shops like Tunisianet).
Coverage and marker size are simulated with the camera at 1.69 m on the inner edge of our half of the platform.

| Camera | Shop · price | Table covered | 70 mm marker at far corner | Verdict |
|---|---|---|---|---|
| **Pi Camera Module 3 Wide** (IMX708, 102° H × 67° V, 120° D) | 2BTrading · 275 TND | ~100 % | ~24 × 12 px @ 56 fps (2304×1296), ~49 × 23 px @ 14 fps (4608×2592) | **Chosen** |
| IMX219 8MP, 120° D | 2BTrading 148 TND (stock unclear), Didactico 185 TND | ~100 % (FOV estimated) | ~18 × 9 px @ 41 fps, ~36 × 17 px @ 21 fps | Backup: too few pixels at speed |
| IMX219 8MP, 160° D | SELI 75 TND, 2BTrading 70 TND | 100 % | ~10 × 5 px | Too few pixels; fine as a cheap camera to start calibration code |
| ArduCam 64MP Hawkeye (autofocus) | 2BTrading 440 TND | 65–75 % | 35–42 px | No: too narrow (~84° D) |
| Pi HQ camera (IMX477) | 2BTrading 350, Little Son 348, Didactico M12 version 390 TND | depends on lens | — | No: only local lens is 6 mm (too narrow); fast mode (2028×1520) not sharper than the Camera Module 3 Wide |
| Arducam 16MP IMX519 / Camera Module 3 standard | 2BTrading 195 / 210 TND | ~80° D | — | Too narrow |
| 4K webcams (Logitech MX Brio, Jabra PanaCast 20, Trust Teza) | Tunisianet (MX Brio 799 DT), Spacenet | ~83 % | ~58 px | Sharp but too narrow (≤ 90° D), most expensive |
| Cheap "8MP" USB webcams | 2BTrading / Didactico ~26 TND | — | — | No: narrow, fake 8MP |

No local shop sells an M12 wide lens or a wide USB camera module.

## Trade-offs we accept with the Camera Module 3 Wide
1. **A Raspberry Pi sits between the camera and the laptop** (the camera uses a ribbon cable, not USB).
2. **Resolution vs speed:** 2304×1296 @ 56 fps (markers small at far corners) or 4608×2592 @ 14 fps (sharp but slow).
   The imported B0433 gives ~35 × 17 px at 30 fps, a better balance.
3. **Autofocus:** lock the lens position in software (libcamera manual focus) and calibrate at that exact position
   and at the runtime resolution (2026 post-mortem: wrong calibration resolution broke everything).

## Pi → laptop link (processing on the laptop)
- **Pi 4 or Pi 5:** both work. Pi 4 is enough for grab + send (~30 fps with JPEG). Pi 5 has more headroom
  (~50+ fps JPEG) but needs the **Pi 5 camera cable** (smaller 22-pin connector; Didactico sells 200/300 mm ones).
  Use whichever the club already has.
- **Link:** direct **Gigabit Ethernet cable** Pi ↔ laptop, fixed IPs, no router. USB-to-Gigabit-Ethernet adapter
  if the laptop has no port.
- **Format:**
  - Recommended: **JPEG per frame**, quality ~90 (~300–500 KB/frame, ~15–30 MB/s, ~40–50 ms end to end).
    Picamera2 can do it in a few lines.
  - Fallback: **raw greyscale** (Y plane only): ~90 MB/s at 2304×1296 @ 30 fps, no compression artefacts.
    Limited to ~30 fps on Gigabit; no colour.
  - Avoid H.264 and other video codecs: extra delay, smeared small markers, and the Pi 5 has no hardware encoder.
- **USB gadget mode** (Pi pretending to be a webcam) is possible but not worth it: USB 2.0 only, and powering the Pi
  from the laptop is unreliable.

## Open points
- Pi 4 or Pi 5 (check what the club has).
- Far-corner detection test at 56 fps; if too weak, compare with 14 fps full resolution or fall back to importing the B0433.
- Weight budget of the station (laptop + Pi + mast + camera < 5 kg [GR G.4]).
