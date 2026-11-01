# Data Flow Architecture

## Complete Vision Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        CAMERA FRAME                              │
│                     (Future: OpenCV)                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ARUCO DETECTION                                │
│              (Future: cv2.aruco.detectMarkers)                   │
│                                                                  │
│  • Detect markers in frame                                      │
│  • Extract corners                                              │
│  • Estimate pose (rvec, tvec)                                   │
│  • Transform to world coordinates                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Raw detections:
                            │ {marker_id: (x, y, θ)}
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MULTI-MARKER TRACKER                            │
│              (src/kalman_filter/tracker.py)                      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  For each marker:                                         │  │
│  │                                                           │  │
│  │  IF detected:                                            │  │
│  │    • Update Kalman filter with measurement              │  │
│  │    • Update velocity estimates                          │  │
│  │    • Reset occlusion counter                            │  │
│  │                                                           │  │
│  │  ELSE (not detected):                                    │  │
│  │    • Predict using motion model                         │  │
│  │    • Increment occlusion counter                        │  │
│  │    • Decrease confidence                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Output: {marker_id: MarkerState}                               │
│    • position (x, y)                                            │
│    • orientation (θ)                                            │
│    • confidence (0.0-1.0)                                       │
│    • is_occluded (bool)                                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Tracked states
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   OCCLUSION HANDLER                              │
│             (src/occlusion_handler/handler.py)                   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  For each tracked marker:                                │  │
│  │                                                           │  │
│  │  Assess detection quality:                               │  │
│  │    • How many corners visible? (0-4)                     │  │
│  │    • Detection confidence                                │  │
│  │    • Is partial or full occlusion?                       │  │
│  │                                                           │  │
│  │  Select strategy:                                        │  │
│  │    • Full detection → Use directly                       │  │
│  │    • Partial detection → Fuse with Kalman               │  │
│  │    • No detection → Use Kalman prediction               │  │
│  │    • Extended occlusion → Use history                    │  │
│  │                                                           │  │
│  │  Apply confidence weighting                              │  │
│  │  Update detection history                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Output: {marker_id: (pose, confidence)}                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Final estimates
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLASSIFICATION                                │
│                                                                  │
│  Separate markers by type:                                      │
│    • Map anchors (IDs 20-23)                                   │
│    • Caisse markers (IDs 36, 47, 41)                           │
│    • Enemy markers (IDs 30+)                                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LORA COMMUNICATION                              │
│                  (Future: pyserial)                              │
│                                                                  │
│  • Format message (compact binary or JSON)                      │
│  • Include: enemy position, caisse positions, timestamp         │
│  • Send to master Raspberry Pi                                  │
│  • Handle transmission errors                                   │
└─────────────────────────────────────────────────────────────────┘
```

## State Machine: Per-Marker Tracking

```
                         ┌─────────────┐
                         │  UNTRACKED  │
                         └──────┬──────┘
                                │
                                │ First detection
                                ▼
                         ┌─────────────┐
                         │ INITIALIZED │
                         └──────┬──────┘
                                │
                                │ Subsequent detections
                                ▼
        ┌──────────────┬───────────────┬──────────────┐
        │              │               │              │
        ▼              ▼               ▼              ▼
   ┌────────┐    ┌─────────┐    ┌──────────┐   ┌─────────┐
   │ TRACKED│◄───│ PARTIAL │    │ OCCLUDED │   │  LOST   │
   │        │    │ OCCLUDED│    │          │   │         │
   └────┬───┘    └────┬────┘    └────┬─────┘   └─────────┘
        │             │              │               ▲
        │  Detection  │   Partial    │  No detection │
        │   good      │   detection  │   for N frames│
        └─────────────┴──────────────┴───────────────┘

States:
  • UNTRACKED: No tracker exists for this marker
  • INITIALIZED: Tracker created, single measurement
  • TRACKED: Good detection, high confidence
  • PARTIAL OCCLUDED: Some corners visible, medium confidence
  • OCCLUDED: No detection, prediction mode, decreasing confidence
  • LOST: No detection for > N frames, tracker removed
```

## Kalman Filter Update Cycle

```
                    ┌─────────────────────┐
                    │   Previous State    │
                    │  [x, y, θ, vx, vy, vθ]│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   PREDICTION STEP   │
                    │                     │
                    │  x' = F * x         │
                    │  P' = F*P*F^T + Q   │
                    └──────────┬──────────┘
                               │
                      ┌────────┴─────────┐
                      │                  │
          Detection   │                  │  No Detection
          Available   │                  │  (frame drop)
                      ▼                  ▼
         ┌─────────────────┐  ┌──────────────────┐
         │  UPDATE STEP    │  │  USE PREDICTION  │
         │                 │  │                  │
         │ y = z - H*x'    │  │ Output: x', P'   │
         │ K = P'*H^T/S    │  │ confidence -= δ  │
         │ x = x' + K*y    │  └──────────────────┘
         │ P = (I-K*H)*P'  │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Current State  │
         │ [x, y, θ, vx, vy, vθ]│
         └─────────────────┘
```

## Occlusion Strategy Selection

```
                    ┌────────────────┐
                    │  New Frame     │
                    └───────┬────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Marker Detected?     │
                 └──────┬───────────────┘
                        │
              ┌─────────┴──────────┐
              │                    │
           YES│                    │NO
              ▼                    ▼
    ┌──────────────────┐   ┌──────────────────┐
    │ All 4 corners?   │   │  FULL OCCLUSION  │
    └──────┬───────────┘   │                  │
           │               │ Strategy:        │
     ┌─────┴─────┐         │ • Kalman predict │
   YES│         │NO        │ • History-based  │
      ▼          ▼         └──────────────────┘
 ┌────────┐ ┌────────────┐
 │ FULL   │ │  PARTIAL   │
 │DETECTION│ │ OCCLUSION  │
 │        │ │            │
 │Strategy:│ │ Strategy:  │
 │• Direct │ │• Fuse with │
 │  use    │ │  Kalman   │
 │• Update │ │• Reduce    │
 │  history│ │  confidence│
 └────────┘ └────────────┘
```

## Example Frame Processing Timeline

```
Frame    Detection    Tracker Action              Confidence
-----    ---------    --------------              ----------
  1      ✓ Full       Initialize tracker          1.00
  2      ✓ Full       Update + velocity est.      1.00
  3      ✓ Full       Update                      1.00
  4      ✗ None       Predict (frame drop)        0.97
  5      ✓ Full       Update + correct            1.00
  6      ✓ Full       Update                      1.00
  7      ⚠ Partial    Fuse with Kalman           0.80
  8      ✗ None       Predict (occluded)          0.93
  9      ✗ None       Predict (occluded)          0.90
 10      ✗ None       Predict (occluded)          0.87
 11      ✓ Full       Update + recover            1.00
 12      ✓ Full       Update                      1.00
```

## Performance Monitoring

The system tracks these metrics in real-time:

```
┌─────────────────────────────────────────┐
│  Vision System Status                   │
├─────────────────────────────────────────┤
│  FPS:                    30.5           │
│  Processing time:        0.45 ms        │
│                                         │
│  Markers tracked:        8              │
│    - Map:                4              │
│    - Caisse:             3              │
│    - Enemy:              1              │
│                                         │
│  Occluded markers:       1              │
│  Tracking confidence:    0.92           │
│                                         │
│  Frame drops:            5              │
│  Occlusion events:       12             │
└─────────────────────────────────────────┘
```

## Integration Points

### Input Interface
```python
# Camera/ArUco detection provides:
detections: Dict[int, Tuple[float, float, float]]
# Where: marker_id -> (x, y, theta) in world coordinates
```

### Output Interface
```python
# Vision system provides:
states: Dict[int, MarkerState]
# Where each MarkerState contains:
#   - position (x, y)
#   - orientation (theta)
#   - confidence (0.0-1.0)
#   - velocity estimates
#   - occlusion status
```

### Configuration Interface
```python
# Tunable parameters:
tracker_config = {
    'process_noise': 0.01,        # Motion model uncertainty
    'measurement_noise': 0.1,     # Sensor uncertainty
    'max_frames_missing': 30      # Timeout threshold
}

occlusion_config = {
    'history_length': 30,         # Detection history size
    'partial_threshold': 0.5,     # Min quality for partial
    'timeout': 1.0                # Seconds before lost
}
```
