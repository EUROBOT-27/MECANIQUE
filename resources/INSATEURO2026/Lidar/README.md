# YDLidar X2 for Eurobot 2026

This repository contains configuration, documentation, and test scripts for the **YDLidar X2** laser range scanner used in our INSA Eurobot 2026 robot project.

## Table of Contents
- [About YDLidar X2](#about-ydlidar-x2)
- [How It Works](#how-it-works)
- [Technical Specifications](#technical-specifications)
- [Application in Eurobot](#application-in-eurobot)
- [Installation](#installation)
- [Usage](#usage)
- [Visualization](#visualization)
- [Troubleshooting](#troubleshooting)

## About YDLidar X2

The YDLidar X2 is a 360-degree 2D laser range scanner (LiDAR) that provides distance measurements in a planar scan. It's a cost-effective solution perfect for robotics applications like autonomous navigation, obstacle detection, and mapping.

## How It Works

### Operating Principle

The YDLidar X2 uses **triangulation ranging technology** combined with a rotating mechanism:

1. **Laser Emission**: An infrared laser diode emits a laser beam
2. **Reflection**: The laser beam hits objects in the environment and reflects back
3. **Detection**: A photodetector receives the reflected light
4. **Triangulation**: The system calculates distance based on the angle and position of the reflected light
5. **Rotation**: The entire measurement system rotates 360° at 5-10 Hz, providing a complete scan of the surroundings
6. **Data Output**: Distance and angle data are transmitted via UART serial communication

### Data Format

- **Scan Rate**: 5-10 Hz (configurable)
- **Sample Rate**: 3000-5000 samples per second
- **Output**: Distance measurements (in mm) with corresponding angles (in degrees)
- **Communication**: Serial UART at 115200 baud rate

## Technical Specifications

| Parameter | Specification |
|-----------|---------------|
| **Model** | YDLidar X2 |
| **Range** | 0.12m - 10m |
| **Scan Rate** | 5-10 Hz (adjustable) |
| **Angular Resolution** | ~0.48° - 0.52° |
| **Laser Wavelength** | 775-795nm (Infrared) |
| **Laser Power** | ~3-5mW |
| **Sample Frequency** | 3000-5000 Hz |
| **Communication** | UART (115200 bps) |
| **Voltage** | 5V DC |
| **Current** | 350-450mA (typical) |
| **Dimensions** | 67mm × 63mm × 46mm |
| **Weight** | ~122g |
| **FOV (Field of View)** | 360° |
| **Safety** | Class 1 Laser Product |

## Application in Eurobot

### Eurobot Competition Overview

Eurobot is an international amateur robotics contest where autonomous robots compete to complete tasks on a predefined playing field. The YDLidar X2 is crucial for several aspects of our robot's functionality:

### Key Applications

#### 1. **Obstacle Detection and Avoidance**
- Real-time detection of opponent robots
- Detection of static obstacles on the field
- Dynamic path planning to avoid collisions
- Safety zone monitoring

#### 2. **Localization and Mapping (SLAM)**
- Building a map of the competition field
- Simultaneous Localization and Mapping (SLAM) for position tracking
- Validating odometry data from wheel encoders
- Improving position accuracy throughout the match

#### 3. **Object Detection**
- Identifying game elements (pucks, towers, dispensers, etc.)
- Measuring distances to target objects
- Verifying successful object manipulation

#### 4. **Boundary Detection**
- Detecting table edges to prevent falling off
- Identifying the playing field boundaries
- Ensuring the robot stays within allowed zones

#### 5. **Strategy Optimization**
- Monitoring opponent positions for strategic decisions
- Finding optimal paths to objectives
- Adapting behavior based on field conditions

### Integration with Robot Systems

The LiDAR data is processed by our main control system and integrated with:
- **Navigation Stack**: For autonomous movement and pathfinding
- **Decision Layer**: For high-level strategy decisions
- **Safety System**: Emergency stop when obstacles are too close
- **Sensor Fusion**: Combined with cameras, ultrasonic sensors, and encoders

## Installation

### Hardware Setup

1. **Connect the YDLidar X2 to your system:**
   - Power: Connect 5V DC power supply
   - Data: Connect USB-UART adapter to your computer/robot controller
   - Ground: Ensure common ground connection

2. **Mount the LiDAR:**
   - Position it horizontally on your robot
   - Ensure 360° field of view (no obstructions)
   - Mount securely to avoid vibrations affecting measurements

### Software Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/INSATEURO2026/Lidar.git
   cd Lidar
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure serial port permissions (Linux):**
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   # Or add user to dialout group
   sudo usermod -a -G dialout $USER
   # Then logout and login again
   ```

### YDLidar SDK Installation (Optional)

For advanced features, you can install the official YDLidar SDK:
```bash
git clone https://github.com/YDLIDAR/YDLidar-SDK.git
cd YDLidar-SDK/build
cmake ..
make
sudo make install
```

## Usage

### Basic Data Collection

```python
from ydlidar import YDLidarX2

# Initialize the LiDAR
lidar = YDLidarX2(port='/dev/ttyUSB0', baudrate=115200)

# Start scanning
lidar.connect()
lidar.start_scan()

# Read scan data
scan_data = lidar.get_scan()
for angle, distance, quality in scan_data:
    print(f"Angle: {angle}°, Distance: {distance}mm, Quality: {quality}")

# Stop scanning
lidar.stop_scan()
lidar.disconnect()
```

### Running the Test Visualization

To visualize the LiDAR output in real-time:

```bash
python test_lidar_visualization.py
```

This will open a window showing:
- Polar plot of LiDAR measurements
- Real-time updates as the LiDAR scans
- Distance and angle information

### Command Line Options

```bash
# Specify custom serial port
python test_lidar_visualization.py --port /dev/ttyUSB0

# Adjust scan rate
python test_lidar_visualization.py --scan-rate 10

# Save scan data to file
python test_lidar_visualization.py --save-data output.csv
```

## Visualization

The `test_lidar_visualization.py` script provides several visualization modes:

1. **Polar View**: Shows LiDAR data in a circular radar-like display
2. **Cartesian View**: X-Y plot of detected points
3. **Distance Histogram**: Distribution of measured distances
4. **Real-time Monitoring**: Live updates at the LiDAR's scan rate

### Keyboard Controls

- `Space`: Pause/Resume scanning
- `S`: Save current scan snapshot
- `R`: Reset visualization
- `Q` or `ESC`: Quit

## Troubleshooting

### Common Issues

**Issue**: LiDAR not detected / Permission denied
```bash
# Solution: Check serial port permissions
ls -l /dev/ttyUSB*
sudo chmod 666 /dev/ttyUSB0
```

**Issue**: No data received
- Check power supply (5V, sufficient current)
- Verify UART connections
- Check baud rate setting (should be 115200)
- Ensure LiDAR motor is spinning

**Issue**: Noisy or inconsistent measurements
- Check for electromagnetic interference
- Ensure stable power supply
- Clean the LiDAR window/lens
- Verify mounting is secure (no vibrations)

**Issue**: Incorrect distance readings
- Verify target surfaces are not too reflective or absorptive
- Check if distance is within range (0.12m - 10m)
- Avoid direct sunlight or bright IR sources
- Ensure LiDAR window is clean

### Getting Help

- **Issues**: Report bugs on [GitHub Issues](https://github.com/INSATEURO2026/Lidar/issues)
- **Discussions**: Join our team discussions
- **Documentation**: Official YDLidar documentation at [YDLidar website](https://www.ydlidar.com/)

## Safety Notes

⚠️ **Laser Safety**:
- The YDLidar X2 is a Class 1 laser product
- Safe for normal use, but avoid staring directly into the laser aperture
- Do not disassemble the device

⚠️ **Electrical Safety**:
- Use proper 5V power supply
- Avoid short circuits
- Ensure proper grounding

## Contributing

This is a team project for Eurobot 2026. Team members can contribute by:
1. Forking the repository
2. Creating a feature branch
3. Submitting pull requests
4. Following code review process

## License

This project is licensed under the terms specified in the LICENSE file.

## Acknowledgments

- INSA Eurobot 2026 Team
- YDLidar for the excellent LiDAR hardware
- Eurobot competition organizers

---

**Project Status**: Active Development for Eurobot 2026

For more information about Eurobot: [https://www.eurobot.org/](https://www.eurobot.org/)
