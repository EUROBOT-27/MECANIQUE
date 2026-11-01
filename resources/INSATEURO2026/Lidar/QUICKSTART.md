# Quick Start Guide - YDLidar X2

## For First-Time Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test Without Hardware (Simulator Mode)
```bash
python3 test_lidar_visualization.py --simulator
```

This will open a visualization window showing simulated LiDAR data.

### 3. Connect Real Hardware

1. **Physical Connection:**
   - Connect YDLidar X2 USB cable to your computer
   - Ensure the device is powered (5V)

2. **Find Serial Port:**
   ```bash
   # Linux/macOS
   ls /dev/ttyUSB*
   # or
   ls /dev/tty.usb*
   
   # Windows
   # Check Device Manager for COM port
   ```

3. **Set Permissions (Linux only):**
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   # OR add yourself to dialout group
   sudo usermod -a -G dialout $USER
   # Then logout and login
   ```

### 4. Run with Real Hardware
```bash
python3 test_lidar_visualization.py --port /dev/ttyUSB0
```

If connection fails, the script will automatically fall back to simulator mode.

## Usage Examples

### Basic Visualization
```bash
python3 test_lidar_visualization.py --simulator
```

### Custom Serial Port
```bash
python3 test_lidar_visualization.py --port /dev/ttyUSB1
```

### Save Scan Data
```bash
python3 test_lidar_visualization.py --simulator --save-data my_scan.csv
```

### Adjust Scan Rate
```bash
python3 test_lidar_visualization.py --simulator --scan-rate 5
```

## Keyboard Controls (During Visualization)

- **Space** - Pause/Resume scanning
- **S** - Save current scan snapshot to CSV
- **R** - Reset statistics
- **Q** or **ESC** - Quit application

## Troubleshooting

### "Permission denied" on Serial Port
```bash
# Quick fix
sudo chmod 666 /dev/ttyUSB0

# Permanent fix
sudo usermod -a -G dialout $USER
# Then logout and login
```

### "No module named 'XXX'"
```bash
pip install -r requirements.txt
```

### LiDAR Not Detected
The script will automatically fall back to simulator mode. Check:
- USB cable connection
- Power supply (5V)
- Serial port permissions
- Correct port specified

## Integration with Robot Code

To use the YDLidar in your robot code:

```python
from test_lidar_visualization import YDLidarX2

# Initialize
lidar = YDLidarX2(port='/dev/ttyUSB0')
lidar.connect()
lidar.start_scan()

# Get scan data
while True:
    scan = lidar.get_scan()
    if scan:
        for angle, distance, quality in scan:
            # Process each point
            print(f"{angle}°: {distance}mm")

# Cleanup
lidar.stop_scan()
lidar.disconnect()
```

## For Eurobot Competition

The LiDAR should be mounted:
- Horizontally on the robot
- With 360° clear field of view
- At a height appropriate for detecting obstacles (typically 10-30cm from ground)
- Securely to avoid vibration

Typical applications:
1. **Real-time obstacle detection** - Detect opponent robots
2. **SLAM** - Build map of playing field
3. **Navigation** - Plan collision-free paths
4. **Safety** - Emergency stop when obstacles too close

## Need Help?

- Check the main README.md for detailed documentation
- Report issues on GitHub: https://github.com/INSATEURO2026/Lidar/issues
- Contact the INSA Eurobot 2026 team

---

Happy scanning! 🤖 🏆
