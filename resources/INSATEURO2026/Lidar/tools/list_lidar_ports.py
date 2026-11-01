#!/usr/bin/env python3
"""
List serial ports and try to identify the YDLIDAR X2 device.

Usage (Windows PowerShell):
  python tools/list_lidar_ports.py
"""
from __future__ import annotations
import sys

try:
    from serial.tools import list_ports
except Exception as e:
    print("pyserial is required. Install with: pip install pyserial", file=sys.stderr)
    sys.exit(1)

KNOWN_VID_PID = [
    (0x10C4, 0xEA60),  # Silicon Labs CP210x (common with YDLidar)
    (0x1A86, 0x7523),  # CH340/CH341
]

def main():
    ports = list_ports.comports()
    if not ports:
        print("No serial ports found.")
        return

    print("Detected serial ports:\n")
    for p in ports:
        vid = f"0x{p.vid:04X}" if p.vid is not None else "None"
        pid = f"0x{p.pid:04X}" if p.pid is not None else "None"
        hint = ""
        if p.vid is not None and p.pid is not None and (p.vid, p.pid) in KNOWN_VID_PID:
            hint = "  <-- possible YDLIDAR adapter"
        print(f"- {p.device:>8} : {p.description}  [VID={vid} PID={pid}]" + hint)
    
    # Best guess
    for p in ports:
        if p.vid is not None and p.pid is not None and (p.vid, p.pid) in KNOWN_VID_PID:
            print(f"\nSuggestion: try --port {p.device}")
            break

if __name__ == "__main__":
    main()
