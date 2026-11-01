# Eurobot 2026 – Computer Vision (Consolidated)

> **Note**: This repository has been consolidated. The `full_pipeline/` folder contains the active, unified implementation of the entire vision system. The `map_anchors/` folder remains **actively maintained** and contains essential camera extrinsics computation tools. Other folders (`caisses_detection/`, `camera_calibration_folder/`) remain available for reference and isolated testing.

## 📁 Repository Structure (Updated Jan 15, 2026)

> **🔄 REORGANIZED**: Major modules now follow a consistent `utils/` + `main/` structure. See [REORGANIZATION.md](REORGANIZATION.md) for details.

```
Euro_vision/
├── strategy/               # 🎯 ACTIVE - Utility-based decision making
│   ├── utils/              # Reusable components
│   │   ├── config.py       # Configuration classes
│   │   ├── world_state.py  # World representation
│   │   ├── task_models.py  # Task definitions
│   │   └── crate_id_tracker.py  # Unique ID tracking
│   ├── main/               # Main execution scripts
│   │   ├── strategy_manager.py  # Decision engine
│   │   ├── visualize_strategy.py  # Live visualization
│   │   └── example_usage.py  # Usage examples
│   └── README.md
│
├── path_planning/          # 🎯 ACTIVE - Path planning algorithms
│   ├── utils/              # Algorithm implementations
│   │   ├── rrt.py          # RRT algorithm
│   │   ├── rrt_connect.py  # RRT-Connect (faster)
│   │   ├── A_star.py       # A* grid-based
│   │   └── path_smoothing.py  # Path optimization
│   ├── main/               # Main scripts (future)
│   └── README.md
│
├── orientation/            # 🎯 ACTIVE - Crate orientation estimation
│   ├── utils/              # Estimation methods
│   │   ├── vision_bbox.py  # Bounding box method
│   │   ├── vision_minrect.py  # Min rectangle
│   │   ├── vision_pca.py   # PCA method
│   │   └── vision_fusion.py  # Fusion (recommended)
│   ├── main/               # Main scripts
│   │   └── aruco_orientation.py
│   └── README.md
│
├── full_pipeline/          # 🎯 ACTIVE - Unified vision system
│   ├── scripts/
│   │   ├── utils/          # Utility modules
│   │   │   ├── crate_id_tracker.py
│   │   │   ├── crate_obstacle_manager.py
│   │   │   └── lidar_path_planning.py
│   │   └── main/           # Main pipelines
│   │       ├── main.py     # Standard pipeline
│   │       ├── main_connect.py  # RRT-Connect
│   │       └── multi_threaded_pipeline.py
│   ├── config/             # Configuration files
│   └── README.md
│
├── kalman_filter/          # 🎯 ACTIVE - Multi-marker tracking
│   ├── src/
│   │   ├── kalman_filter/  # Kalman implementations
│   │   └── occlusion_handler/  # Occlusion strategies
│   ├── examples/           # Demos and tuning
│   └── README.md
│
├── map_anchors/            # 🎯 ACTIVE - Camera extrinsics tools
│   ├── scripts/            
│   │   ├── compute_extrinsics.py  # Primary PnP method
│   │   ├── compute_extrinsics_gui.py  # Interactive GUI
│   │   └── validate_pose.py  # Stability testing
│   └── README.md
│
├── camera_calibration_folder/  # Camera intrinsics
├── ros_ready_pipeline/     # ROS2 integration (WIP)
├── Documentation/          # Project documentation
│   ├── PROGRESS.md         # Current status & roadmap
│   ├── QUICK_START.md      # Getting started guide
│   └── THEORETICAL_UNDERSTANDING.md
├── REORGANIZATION.md       # 📝 Reorganization guide
└── requirements.txt
```

**Active Development Areas**:
- ✅ `map_anchors/scripts/` - Camera extrinsics computation (PnP, Kabsch, GUI, visualization)
- ✅ `camera_calibration_folder/` - Camera intrinsics (iPhone XR calibrated)
- 🟡 `full_pipeline/` - Integrated detection and tracking system
- 🟡 `mini_path_planning/` - WiFi communication testing

## 📌 Overview
This repository documents the **Computer Vision (CV) system** for our Eurobot 2026 robot.
The goal of this module is to provide real-time information about:
- The **global map reference system** (via fixed ArUco markers on the board).
- The **position of the caisse de noisettes** (wooden boxes, tagged with ArUco).
- The **enemy robot’s position** (detected via its ArUco marker).
- Communication of this information to the **master Raspberry Pi** that drives robot strategy.

This vision system uses an **overhead camera** placed above the playfield. All detections and coordinates will be computed in the **world (map) reference frame**, and then broadcast to the master controller.

---

## 🗺️ Tasks Breakdown

### 1. ArUco Marker Detection (Consolidated)
- **Fixed map anchors**: 4 ArUco tags placed on the field (Eurobot 2026).
  - Define the global coordinate system.
  - IDs: `20–23` (DICT_4X4_50) ✅ Implemented in `full_pipeline/`
- **Caisse de noisettes**: each box has its own unique ArUco ID.  
  - IDs reserved: `36, 47, 41` (Blue team, Yellow team, Black rotten box) ✅ **Implemented**
- **Enemy robot**: equipped with its own ArUco marker.
  - IDs: `30+` ✅ Implemented in `full_pipeline/`
  - Requires Kalman filtering for smooth tracking
  - Must handle temporary occlusion periods

Libraries/tools:
- OpenCV `cv2.aruco` for marker detection.
- Custom logic to separate **map tags** vs **object tags**.
- FilterPy for Kalman filtering (enemy tracking).

---

### 2. Camera Calibration ✅ Implemented
- Perform **intrinsic calibration** of the overhead camera:
  - Estimate focal length, principal point, distortion coefficients.
  - Required for accurate pose estimation (`rvec, tvec`).
- Perform **extrinsic calibration** from map anchors (online):
  - Use anchors visible in the first frames to compute `T_world_cam`.
  - Field: 3.0 m × 2.0 m; anchors inset at 0.6 m (IDs 20–23).

Outcome:  
- Any detected marker `(rvec, tvec)` can be transformed into **world coordinates (x, y, θ)**.

---

### 3. Caisses de Noisettes Detection ✅ Implemented
- Detect hazelnut boxes using ArUco markers on vinyl bands.
- Identify team ownership (Blue/Yellow) via color detection.
- Track the special black "caisse pourrie" (rotten box).
- Real-time position tracking with world coordinates.
- Expected total: 48 boxes on the field.

Now part of the consolidated `full_pipeline/` implementation.

---

### 4. Enemy Detection
- Detect enemy’s ArUco marker.
- Compute:
  - **Absolute position** `(x, y)` in meters.
  - **Orientation** `θ` (yaw).
- Apply smoothing (Kalman filter or exponential moving average) to reduce jitter.
- Handle cases where the enemy marker is temporarily occluded (prediction step).

---

### 5. Communication ✅ **TEST IMPLEMENTATION AVAILABLE**

**Status**: 🟡 **PARTIALLY IMPLEMENTED** - Mini path planning test module ready, full system pending

> **NEW**: See **[mini_path_planning/README.md](mini_path_planning/README.md)** for the test implementation of PC-to-Raspberry Pi communication using sockets.

#### System Architecture

The vision system communicates wirelessly to the robot:

```
┌─────────────────────────────────────────┐
│  Overhead Camera (Fixed)                │
└────────────┬────────────────────────────┘
             │
             │ USB Cable (Wired)
             │
┌────────────▼────────────────────────────┐
│  Vision PC (Off-field, stationary)      │
│  - Process camera frames                │
│  - Detect markers & compute coordinates │
│  - Track objects (enemy, caisses)       │
└────────────┬────────────────────────────┘
             │
             │ WiFi/Wireless Communication
             │ (WebSockets/MQTT/UDP)
             │
┌────────────▼────────────────────────────┐
│  Robot (Mobile on field)                │
│  - Raspberry Pi (Master Controller)     │
│  - Receives vision data wirelessly      │
│  - Controls robot movement               │
└──────────────────────────────────────────┘
```

#### 🚀 Mini Path Planning Test Module

A working implementation of the communication system is available in the `mini_path_planning/` folder. This test module:

**Features**:
- ✅ Detects ArUco markers for our robot (ID 1-5) and enemy robot (ID 6-10)
- ✅ Calculates 3D distance using camera calibration
- ✅ Sends alerts to Raspberry Pi via UDP/TCP sockets
- ✅ Configurable distance threshold (default: 0.5m)
- ✅ Real-time visualization with distance display
- ✅ Alert cooldown to prevent spam
- ✅ JSON message format with timestamps and positions

**Quick Start**:
```bash
# On Vision PC
cd mini_path_planning
python3 pc_sender/path_monitor.py --ip 192.168.1.100 --port 5000

# On Raspberry Pi
python3 rpi_receiver/receiver.py --port 5000
```

**Use Cases**:
- Test socket communication between PC and Raspberry Pi
- Verify distance calculations and pose estimation
- Prototype path replanning triggers based on enemy proximity
- Validate network performance under competition conditions

See **[mini_path_planning/README.md](mini_path_planning/README.md)** for complete documentation.

---

#### ⚠️ Competition Environment Challenges

Competition venues present **severe wireless interference**:
- **20-30 teams** operating simultaneously
- **Hundreds of spectator devices** (phones, laptops, tablets)
- **2.4GHz WiFi congestion** is extreme
- **Expected packet loss**: 10-30% during peak times
- **Latency spikes**: 100-1000ms common
- **Connection dropouts**: Multi-second outages possible

#### Recommended Communication Methods

**Option 1: WebSockets** ✅ **RECOMMENDED FOR REAL-TIME**
```python
# Server on Vision PC
import asyncio
import websockets
import json

async def vision_server(websocket, path):
    while True:
        # Send vision data
        data = {
            "timestamp": time.time(),
            "enemy": {"x": 1.23, "y": 0.85, "theta": 1.57},
            "caisses": [{"id": 36, "x": 0.45, "y": 0.65}]
        }
        await websocket.send(json.dumps(data))
        await asyncio.sleep(0.033)  # ~30 Hz

# Client on Robot
async def robot_client():
    async with websockets.connect('ws://VISION_PC_IP:8765') as ws:
        async for message in ws:
            data = json.loads(message)
            # Use vision data for navigation
```

**Advantages**:
- ✅ Real-time bidirectional communication
- ✅ Low latency when network is good (~5-20ms)
- ✅ Built-in reconnection handling
- ✅ Easy to debug (JSON format)

**Challenges**:
- ⚠️ Vulnerable to WiFi interference
- ⚠️ Requires robust error handling
- ⚠️ May need fallback mechanism

**Option 2: MQTT** ✅ **GOOD FOR PUB/SUB**
```python
# Publisher on Vision PC
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("BROKER_IP", 1883)

def publish_vision_data(enemy, caisses):
    client.publish("vision/enemy", json.dumps(enemy))
    client.publish("vision/caisses", json.dumps(caisses))

# Subscriber on Robot
def on_message(client, userdata, message):
    data = json.loads(message.payload)
    # Process vision data
```

**Advantages**:
- ✅ Lightweight protocol
- ✅ Quality of Service (QoS) levels
- ✅ Publish/Subscribe pattern
- ✅ Good for distributed systems

**Option 3: UDP Broadcast** ✅ **LOWEST LATENCY**
```python
# Vision PC - Send
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data = msgpack.packb({"enemy": {...}, "caisses": [...]})
sock.sendto(data, ("ROBOT_IP", 5000))

# Robot - Receive
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5000))
data, addr = sock.recvfrom(4096)
vision_data = msgpack.unpackb(data)
```

**Advantages**:
- ✅ Lowest possible latency (~1-5ms)
- ✅ No connection overhead
- ✅ Simple implementation

**Challenges**:
- ⚠️ No delivery guarantee
- ⚠️ No automatic reconnection
- ⚠️ Packets may be lost

#### Data Format

**JSON format** (debugging & development):
```json
{
  "timestamp": 1234567890.123,
  "seq": 1234,
  "enemy": {
    "x": 1.23,
    "y": 0.85,
    "theta": 1.57,
    "confidence": 0.95,
    "visible": true
  },
  "caisses": [
    {"id": 36, "team": "BLUE", "x": 0.45, "y": 0.65, "theta": 0.0},
    {"id": 47, "team": "YELLOW", "x": -0.32, "y": 1.12, "theta": 1.57}
  ]
}
```

**Binary format** (production - more efficient):
```python
import msgpack

# Pack data efficiently
data = msgpack.packb({
    "ts": time.time(),
    "enemy": [x, y, theta, confidence],
    "caisses": [[id, x, y, theta], ...]
})
# ~50-100 bytes per packet vs ~300-500 bytes for JSON
```

#### Robust Communication Implementation

**Must implement these features**:

1. **Automatic Reconnection**
```python
while True:
    try:
        # Establish connection
        await connect_to_robot()
        # Send data
        await send_vision_data()
    except ConnectionError:
        print("Connection lost, reconnecting...")
        await asyncio.sleep(1)  # Wait before retry
```

2. **Connection Quality Monitoring**
```python
class ConnectionMonitor:
    def __init__(self):
        self.packet_count = 0
        self.packet_loss = 0
        self.latency_avg = 0
    
    def update(self, packet_sent, ack_received, latency):
        self.packet_count += 1
        if not ack_received:
            self.packet_loss += 1
        self.latency_avg = 0.9 * self.latency_avg + 0.1 * latency
```

3. **Adaptive Rate Limiting**
```python
def should_send_update(connection_quality):
    if connection_quality < 50:
        return frame_count % 3 == 0  # Send every 3rd frame
    return True  # Send every frame
```

4. **Heartbeat/Keepalive**
```python
async def heartbeat():
    while True:
        await websocket.ping()
        await asyncio.sleep(1.0)  # Ping every second
```

#### Implementation Requirements

**Must implement**:
- [ ] Choose communication method (WebSocket/MQTT/UDP)
- [ ] Implement sender module (vision PC)
- [ ] Implement receiver module (robot)
- [ ] Connection monitoring and health checks
- [ ] Automatic reconnection logic
- [ ] Handle packet loss gracefully
- [ ] Latency measurement and logging
- [ ] Sequence numbers to detect lost packets

**Testing required**:
- [ ] Test with multiple WiFi networks active (simulate interference)
- [ ] Measure packet loss rates in realistic conditions
- [ ] Test range limits (5m, 10m, 15m)
- [ ] Simulate competition interference (microwave on = 2.4GHz noise)
- [ ] Verify latency under load
- [ ] Test reconnection after dropouts

#### Libraries Needed

```bash
# For WebSocket communication
pip install websockets>=12.0

# For MQTT communication
pip install paho-mqtt>=1.6

# For efficient binary serialization
pip install msgpack>=1.0

# For network diagnostics
pip install psutil  # Monitor network stats
```

**See `communication/` folder for implementation** (to be created)

---
            └─────────────────────────────────────┘
```

**Why this works:**
- ✅ Only ONE cable (camera to PC) - simple stationary setup
- ✅ Vision computer is OFF the field (no movement constraints)
- ✅ Camera stays fixed overhead
- ✅ Lower system complexity than on-robot vision
- ✅ Better computational resources available on PC
- ✅ Robot has full mobility (wireless communication)

#### **Implementation Requirements**

**Must implement**:
- [ ] Choose communication protocol:
  - [ ] WebSocket (real-time bidirectional)
  - [ ] MQTT (pub/sub with QoS)
  - [ ] UDP (lowest latency, no reliability)
- [ ] Implement sender module (vision PC)
- [ ] Implement receiver module (robot)
- [ ] Add packet numbering/timestamps
- [ ] Handle packet loss gracefully (interpolation/extrapolation)
- [ ] Implement connection monitoring and reconnection

**Testing required**:
- [ ] Test latency under various WiFi conditions (target < 50ms)
- [ ] Measure packet loss rates (expect 10-30% in competition)
- [ ] Test with 20+ WiFi networks active (competition simulation)
- [ ] Verify graceful degradation when connection quality drops
- [ ] Test reconnection after WiFi dropout

#### **Data Format**

**Binary format for efficiency** (recommended for WiFi with high packet loss):
```python
# Compact binary protocol (MessagePack or custom)
# Header: 0xAA 0x55 (2 bytes)
# Sequence number: 4 bytes (to detect packet loss)
# Timestamp: 8 bytes (double)
# Enemy: x, y, theta (12 bytes - 3 floats)
# Num caisses: 1 byte
# Each caisse: id (1 byte) + x, y, theta (12 bytes)
# CRC16: 2 bytes (error detection)
```

**JSON format** (easier debugging, but larger packet size):
```json
{
  "seq": 1234,
  "timestamp": 1234567890.123,
  "enemy": {"x": 1.23, "y": 0.85, "theta": 1.57, "confidence": 0.95},
  "caisses": [
    {"id": 36, "team": "BLUE", "x": 0.45, "y": 0.65, "theta": 0.0}
  ]
}
```

#### **Libraries Needed**

```bash
# For WebSocket communication
pip install websockets>=12.0

# For MQTT communication  
pip install paho-mqtt>=1.6

# For UDP communication
# (Built-in Python socket library - no install needed)

# For efficient data serialization
pip install msgpack>=1.0  # Binary format (smaller packets than JSON)
```

**See `communication/` folder for implementation** (to be created)

---

## 🎯 Map Anchors Module (Implemented)

The **Map Anchors** module establishes the global coordinate system for the vision pipeline.

### Quick Start

```bash
# Install dependencies
pip install -r map_anchors/requirements.txt

# Generate ArUco markers for printing
python map_anchors/scripts/generate_markers.py --output markers/ --size 200

# Detect map anchors
python map_anchors/scripts/detect_anchors.py --camera 0 --visualize

# Compute camera extrinsics (after placing markers)
python map_anchors/scripts/compute_extrinsics.py --camera 0 --config map_anchors/config/marker_config.yaml

# Validate camera pose stability
python map_anchors/scripts/validate_pose.py --camera 0 --duration 30
```

### Features
- ✅ **4 Fixed ArUco markers** placed at table corners (IDs: 20, 21, 22, 23)
- ✅ **Camera extrinsics computation** using PnP algorithm (primary method)
- ✅ **Alternative Kabsch pose fusion** method for comparison
- ✅ **Interactive GUI** for extrinsics computation with live preview
- ✅ **Pose validation** to ensure stability (variance < 2mm)
- ✅ **World coordinate system** definition (origin at field corner)
- ✅ **3D visualization tools** for debugging camera pose
- ✅ **OpenCV API compatibility layer** for 4.7+ versions
- ✅ **Comprehensive documentation** with step-by-step guides

### Recent Tools & Improvements (November 2025)

**Extrinsics Computation Methods**:
- `compute_extrinsics.py` - **Primary method** (PnP RANSAC on marker centers)
  - ✅ Bug fix: Corrected transformation matrix extraction (Y-axis sign, Z-height)
  - ✅ Excellent stability: 0.2-2mm std dev over 60 frames
  - ✅ Validated against physical measurements
- `compute_extrinsics_kabsch.py` - Alternative pose fusion method
  - Uses `estimatePoseSingleMarkers()` + Kabsch algorithm
  - Higher variance: 6-16cm std dev (1000× less stable than PnP)
  - Useful for comparison and research

**Interactive Tools**:
- `compute_extrinsics_gui.py` - Tkinter GUI with live camera preview
  - Color-coded marker visualization (Green, Yellow, Magenta, Blue)
  - One-click extrinsics computation with progress updates
  - Configurable: camera index, marker size, frame averaging

**Debugging & Validation**:
- `visualize_camera_pose.py` - 3D matplotlib visualization
  - Shows camera position, orientation, and viewing direction
  - Plots field, markers, and coordinate axes
  - Critical for diagnosing transformation bugs
- `validate_pose.py` - Long-term stability testing

**Compatibility**:
- `opencv_aruco_compat.py` - OpenCV 4.7+ API compatibility layer
  - Handles `DetectorParameters()` vs `DetectorParameters_create()` changes
  - Works with both old and new ArUco detector APIs

**Comparison Results** (60-frame test):
- PnP method: Position std dev 0.2-2mm, rotation std dev 0.001-0.002 rad
- Kabsch method: Position std dev 6-16cm, rotation std dev 0.002-0.006 rad
- **Recommendation**: Use PnP method for production (1000× better stability)
- Reprojection error: ~16 pixels (expected for 4-point centers-only method)

See **[map_anchors/README.md](map_anchors/README.md)** for detailed documentation and **[map_anchors/scripts/COMPARISON_KABSCH_VS_PNP.md](map_anchors/scripts/COMPARISON_KABSCH_VS_PNP.md)** for full comparison analysis.

---

## 🎁 Caisses Detection Module (Implemented)

The **Caisses Detection** module identifies and tracks hazelnut boxes (caisses de noisettes) on the playing field.

### Quick Start

```bash
# Install dependencies
pip install -r caisses_detection/requirements.txt

# Generate ArUco markers for testing
python caisses_detection/scripts/generate_aruco_markers.py --all

# Detect unknown marker IDs (useful for testing)
python caisses_detection/scripts/detect_aruco_ids.py --camera 0

# Run real-time caisse detection
python caisses_detection/scripts/detect_caisses.py --camera 0 --visualize

# Save detection results to video
python caisses_detection/scripts/detect_caisses.py --camera 0 --visualize --output results.mp4
```

### Features
- ✅ **ArUco marker detection** for box identification (IDs: 36, 47, 41)
- ✅ **Team identification** via HSV color detection (Blue/Yellow)
- ✅ **Special rotten box** detection (black caisse with ID 41)
- ✅ **World coordinate transformation** for accurate positioning
- ✅ **Real-time tracking** with confidence scoring
- ✅ **Visualization tools** for debugging
- ✅ **Marker generation** for testing purposes

### Box Specifications
- **Dimensions**: 150mm × 50mm × 30mm
- **Total count**: 48 boxes on field
- **Marker size**: 40mm × 40mm ArUco tags
- **Dictionary**: DICT_4X4_50
- **Teams**: 
  - Blue team → ArUco ID 36
  - Yellow team → ArUco ID 47
  - Rotten box (black) → ArUco ID 41

See **[caisses_detection/README.md](caisses_detection/README.md)** for detailed documentation.

---

## ⚙️ Pipeline (High-Level)

1. **Capture frame** from overhead camera. ✅
2. **Detect ArUco markers** → extract `(rvec, tvec)`. ✅  
3. **Build transforms**: 
   - `T_world_cam = T_world_map * inv(T_cam_map)` ✅ (from map anchors - implemented)
   - `T_world_caisse = T_world_cam * T_cam_caisse` ✅ (implemented)
   - `T_world_enemy = T_world_cam * T_cam_enemy` ⏸️ (planned)
4. **Classify markers**:
   - Map anchors (0-3) → update world reference ✅ (implemented)
   - Caisse (36, 47, 41) → store box position ✅ (implemented)
   - Enemy (30+) → update enemy coordinates ⏸️ (planned)
5. **Smooth results** (Kalman filter) ⏸️ (planned - FilterPy required)
6. **Send data** to master Raspberry Pi 🔴 **CRITICAL - NOT IMPLEMENTED**
   - Choose communication method (WebSocket/MQTT/UDP over WiFi)
   - Implement sender/receiver modules
   - Add packet loss handling and reconnection logic

---

## 📚 Challenges & What to Expect

### Vision Challenges
- **Marker occlusion**: enemy may cover its marker; need prediction.  
- **Lighting variations**: test under competition conditions (bright/uneven lights).  
- **Lens distortion**: especially with wide-angle cameras. Correct via calibration.  
- **Detection dropouts**: frames without detection; handle gracefully.  
- **Real-time constraints**: must process at ~20–30 FPS on vision PC.

### Communication Challenges ⚠️ **CRITICAL**

**Wireless Communication Reliability**:
- **WiFi interference**: 20-30 teams + spectators = severe congestion
  - **Expected packet loss**: 10-30% in competition environment
  - **Latency spikes**: 100-1000ms during peak usage
  - **Connection dropouts**: Multi-second outages are common
- **Network reliability**: DO NOT assume stable WiFi connection
  - Implement robust reconnection and fallback logic
  - Test in crowded WiFi environments before competition
  - Monitor connection quality in real-time
  - Use 5GHz WiFi if possible (less congested than 2.4GHz)

**Latency Optimization**: Total system latency must stay < 100ms
- Vision processing: ~30-50ms (at 20-30 FPS)
- Communication: 5-50ms (depends on network conditions)
- Robot processing: ~10-20ms

### Recommendations
1. **Test early**: Validate communication in realistic interference scenarios
2. **Plan fallbacks**: Robot should function with degraded/lost vision link
3. **Monitor quality**: Log latency, packet loss, connection uptime
4. **Use 5GHz WiFi**: Less congested than 2.4GHz (if available)
5. **Implement reconnection**: Auto-reconnect when connection drops
6. **Consider UDP**: Lower latency than TCP, acceptable packet loss

---

## 🛠️ Tools & Dependencies

### Core Vision Stack ✅
- **Python 3.10+**
- **OpenCV (cv2 + cv2.aruco)** - ArUco detection and pose estimation
- **NumPy** - Matrix operations and coordinate transforms

### Additional Requirements ⏸️ (To be installed)
- **FilterPy** - Kalman filtering for enemy tracking
- **PyYAML** - Configuration file management

### Communication Stack 🔴 (WIRELESS - Not yet implemented)

Choose one wireless communication method:

- **websockets>=12.0** - WebSocket client/server (real-time bidirectional)
- **paho-mqtt>=1.6** - MQTT pub/sub protocol (reliable messaging)
- **msgpack>=1.0** - Efficient binary serialization (optional, reduces bandwidth)
- **socket** (built-in) - Raw UDP for lowest latency

### Hardware Requirements

**Vision PC** (Off-field):
- Laptop or desktop computer (Windows/Linux/Mac)
- USB port for camera connection
- WiFi adapter (5GHz preferred for less interference)
- Recommended: i5/Ryzen 5 or better, 8GB+ RAM

**Robot** (On-field):
- Raspberry Pi 4/5 (4GB+ RAM) - $45-80
- WiFi dongle (5GHz recommended for better performance in crowded environments)
- ArUco marker mounted on robot (for enemy detection)

**Camera System**:
- USB webcam or IP camera
- USB cable (sufficient length to reach PC from overhead position)
- Camera mount (overhead positioning above field)

### Optional Tools
- **Flask/FastAPI** - HTTP endpoints for debugging/monitoring
- **matplotlib** - Data visualization and performance plotting
- **psutil** - Network statistics and monitoring

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/INSATEURO2026/Euro_vision.git
cd Euro_vision

# Install dependencies
pip install -r requirements.txt

# Install module-specific dependencies
pip install -r map_anchors/requirements.txt
pip install -r caisses_detection/requirements.txt
```

## 🎯 Quick Start Guide

### 1. Camera Calibration ✅ (Completed)

Camera calibration is the first step in the vision pipeline. Intrinsic parameters (fx, fy, cx, cy) and distortion coefficients have been computed for the iPhone XR camera.

See [camera_calibration_folder/README.md](camera_calibration_folder/README.md) for detailed instructions.

```bash
# Generate and print the chessboard pattern
python camera_calibration_folder/generate_chessboard.py

# Calibrate your camera (live mode)
python camera_calibration_folder/calibrate_camera.py --camera 0

# Test the calibration
python camera_calibration_folder/test_calibration.py
```

**Current calibration**: iPhone XR (1280×720) - `fx=1637.0, fy=1612.9, cx=555.4, cy=367.7`

### 2. Map Anchors Setup ✅ (Completed)

Establish the global coordinate system using 4 fixed ArUco markers:

```bash
# Generate map markers (IDs 20, 21, 22, 23)
python map_anchors/scripts/generate_markers.py --output markers/ --size 200

# Compute camera extrinsics (PnP method - recommended)
python map_anchors/scripts/compute_extrinsics.py --camera 1 --average 60

# Alternative: Use interactive GUI
python map_anchors/scripts/compute_extrinsics_gui.py

# Validate pose stability
python map_anchors/scripts/validate_pose.py --camera 1 --duration 30

# Visualize camera pose in 3D (for debugging)
python map_anchors/scripts/visualize_camera_pose.py
```

**Current setup**: 
- Camera: iPhone XR via Camo (index 1)
- Markers: IDs 20-23 at verified positions (0.6m inset from field edges)
- Extrinsics: Computed and validated (camera at 0.777m, 2.768m, 2.429m)

### 3. Caisses Detection (Third Step)

Detect and track hazelnut boxes:

```bash
# Generate test markers (IDs 36, 47, 41)
python caisses_detection/scripts/generate_aruco_markers.py --all

## 🚀 Implementation Status
- [x] **Implement ArUco detection + classification (map vs caisse vs enemy)** ✓
- [x] **Build transform pipeline (camera → world)** ✓
- [x] **Implement Kalman filter for enemy tracking** ✓
- [x] **Create 2D map visualization with enemy trajectory** ✓
- [x] **Calibrate overhead camera (intrinsics & distortion)** ✓ (iPhone XR calibrated)
- [x] **Compute camera extrinsics (camera → world transformation)** ✓ (PnP method validated)
- [x] **Define exact world coordinates of the 4 map markers** ✓ (IDs 20-23 at verified positions)
- [ ] **Implement WiFi communication with robot** 🔴 CRITICAL - Choose method (WebSocket/MQTT/UDP)
- [ ] **Test wireless communication reliability** (WiFi interference, packet loss handling)
- [ ] Test on full map with mock enemy + caisses - *requires physical setup*
- [ ] **Integrate full pipeline** (camera → detection → tracking → communication)

## 📦 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run Demo
```bash
# Test with simulated markers
python examples/demo_detection.py

# Run with live camera
python main.py --camera 0

# Run with video file
python main.py --video path/to/video.mp4
```

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for detailed documentation.  

---

## 📖 References
- OpenCV ArUco module: https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html  
- OpenCV Camera Calibration: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html  
- Kalman Filter Theory: Welch & Bishop, "An Introduction to the Kalman Filter" (UNC-Chapel Hill)
- Eurobot official rules (Cahier des Charges).  

