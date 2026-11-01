# Caisses de Noisettes Detection Module

## 📦 Overview

This module handles the detection and tracking of the 48 **caisses de noisettes** (hazelnut boxes) on the Eurobot 2026 playing field.

## 🎯 Box Specifications

### Physical Properties
- **Dimensions**: 150mm (L) × 50mm (W) × 30mm (H)
- **Material**: Wood
- **Quantity**: 48 boxes total
- **Painted faces**: 2 large opposing faces
  - One face: **Blue** (team color)
  - Opposite face: **Yellow** (team color)
  - 4 other faces: **Unpainted** (natural wood)

### ArUco Markers
- **Location**: Vinyl band wrapped around each box (centered)
- **Marker size**: 40mm × 40mm
- **Marker IDs**:
  - **Blue team zone**: ID = **36**
  - **Yellow team zone**: ID = **47**
- **Configuration**: 2 colored zones per box, each containing one ArUco marker

## 📁 Module Structure

```
caisses_detection/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config/
│   ├── caisse_config.yaml      # Box specifications
│   └── detection_params.yaml   # Detection parameters
├── scripts/
│   ├── detect_caisses.py       # Real-time detection
│   ├── track_caisses.py        # Multi-box tracking
│   ├── analyze_distribution.py # Box distribution analysis
│   └── calibrate_colors.py     # Color calibration tool
└── src/
    ├── caisse_detector.py      # Core detection class
    ├── caisse_tracker.py       # Tracking algorithms
    └── color_classifier.py     # Team color identification
```

## 🚀 Quick Start

### 1. Installation

```bash
pip install -r caisses_detection/requirements.txt
```

### 2. Basic Detection

```bash
# Detect caisses from camera feed
python caisses_detection/scripts/detect_caisses.py --camera 0 --visualize
```

### 3. Track All Boxes

```bash
# Track all 48 boxes and log positions
python caisses_detection/scripts/track_caisses.py \
    --camera 0 \
    --output logs/caisses_log.json \
    --duration 300
```

### 4. Analyze Distribution

```bash
# Analyze box positions and team distribution
python caisses_detection/scripts/analyze_distribution.py \
    --input logs/caisses_log.json \
    --output reports/distribution.html
```

## 🔧 Configuration

### caisse_config.yaml

```yaml
box_dimensions:
  length_mm: 150
  width_mm: 50
  height_mm: 30

aruco_markers:
  blue_team_id: 36
  yellow_team_id: 47
  marker_size_mm: 40
  dictionary: DICT_4X4_50

colors:
  blue_team:
    h_range: [100, 130]
    s_range: [100, 255]
    v_range: [50, 255]
  yellow_team:
    h_range: [20, 40]
    s_range: [100, 255]
    v_range: [100, 255]

detection:
  min_marker_area: 1000  # pixels²
  max_marker_area: 10000
  confidence_threshold: 0.7
```

## 📊 Detection Pipeline

1. **ArUco Detection**
   - Detect markers with IDs 36 and 47
   - Extract pose (rvec, tvec) for each marker

2. **Transform to World Coordinates**
   - Apply camera extrinsics: `T_world_caisse = T_world_cam * T_cam_marker`
   - Compute box center position (x, y)

3. **Orientation Estimation**
   - Use marker pose to determine box orientation
   - Account for vinyl band position around box

4. **Color Classification**
   - Identify visible face color (blue/yellow)
   - Determine which team "owns" the box based on visible face

5. **Tracking**
   - Associate detections across frames
   - Handle occlusions and temporary disappearances
   - Maintain unique ID for each of 48 boxes

## 🎨 Color Detection

The module uses HSV color space for robust team color identification:

```python
# Blue team detection
blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

# Yellow team detection
yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

# Determine visible face
if blue_area > yellow_area:
    team = "BLUE"
else:
    team = "YELLOW"
```

## 📡 Output Format

### JSON Log Format

```json
{
  "timestamp": 1234567890.123,
  "caisses": [
    {
      "id": 1,
      "aruco_id": 36,
      "team": "BLUE",
      "position": {
        "x": 0.450,
        "y": 0.650,
        "theta": 1.57
      },
      "visible_face": "blue",
      "confidence": 0.95
    }
  ]
}
```

### LoRa Packet Format

```
[CAISSE:id=1,team=B,x=0.45,y=0.65,θ=1.57][CAISSE:id=2,team=Y,x=0.80,y=0.30,θ=0.78]
```

## 🧪 Testing & Validation

### Test Detection Accuracy

```bash
python caisses_detection/scripts/test_accuracy.py \
    --ground-truth data/test_positions.json \
    --output results/accuracy_report.json
```

### Validate Color Classification

```bash
python caisses_detection/scripts/validate_colors.py \
    --camera 0 \
    --samples 100
```

## 🐛 Troubleshooting

### Markers Not Detected
- Check lighting conditions (avoid glare on vinyl bands)
- Verify marker size matches configuration (40mm)
- Ensure camera is properly calibrated

### Wrong Color Classification
- Run color calibration tool: `python scripts/calibrate_colors.py`
- Adjust HSV ranges in `caisse_config.yaml`
- Check for shadows and uneven lighting

### Tracking Failures
- Reduce occlusions between boxes
- Increase camera frame rate
- Tune tracking parameters in `detection_params.yaml`

## 📚 Technical Details

### Box Geometry

```
Top view of box with vinyl band:
┌─────────────────────┐
│  [BLUE ArUco 36]   │ ← Vinyl band (blue zone)
│                     │
│   150mm × 50mm     │ ← Box top surface
│                     │
│ [YELLOW ArUco 47]  │ ← Vinyl band (yellow zone)
└─────────────────────┘
```

### Coordinate System
- **Origin**: Marker 0 (bottom-left corner of field)
- **X-axis**: Along field length
- **Y-axis**: Along field width
- **Units**: Meters

## 🔗 Integration

This module integrates with:
- **map_anchors**: Uses world coordinate system
- **enemy_detection**: Shares ArUco detection pipeline
- **communication**: Sends caisse data via LoRa

## 📖 References

- OpenCV ArUco: https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
- HSV Color Space: https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html
- Eurobot 2026 Rules: Official Cahier des Charges
