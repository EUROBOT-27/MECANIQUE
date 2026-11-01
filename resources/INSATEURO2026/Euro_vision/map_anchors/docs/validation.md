# Camera Pose Validation

## 🎯 Objective

Validate that the computed camera pose (extrinsics) is **stable and accurate** when the robot is absent from the field. This ensures reliable world coordinate transformations during operation.

## 📋 Why Validate?

Camera pose validation is critical because:
1. **Stability**: Camera should not move during operation
2. **Accuracy**: Pose estimation errors propagate to all object positions
3. **Reliability**: Unstable pose indicates hardware or calibration issues
4. **Trust**: Validated pose gives confidence in downstream pipeline

## 🧪 Validation Tests

### Test 1: Pose Stability Over Time

**Goal**: Verify camera pose doesn't drift when nothing moves.

**Procedure**:
1. Ensure robot is absent from field
2. Compute camera extrinsics from map anchors
3. Repeat computation every frame for N seconds (e.g., 30-60s)
4. Analyze variance in position and orientation

**Success Criteria**:
- Position variance < 1mm in X, Y, Z
- Rotation variance < 0.1 degrees in all axes

**Implementation**:
```python
import cv2
import numpy as np
from scipy.spatial.transform import Rotation

def test_pose_stability(video_source, duration_seconds=30, fps=30):
    """
    Test camera pose stability over time.
    
    Args:
        video_source: Camera index or video file
        duration_seconds: How long to test
        fps: Expected frame rate
    
    Returns:
        results: Dict with stability metrics
    """
    cap = cv2.VideoCapture(video_source)
    
    positions = []  # (x, y, z) in meters
    orientations = []  # (roll, pitch, yaw) in degrees
    
    n_frames = duration_seconds * fps
    
    for i in range(n_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Compute extrinsics
        success, rvec, tvec, T_world_cam = compute_camera_extrinsics(
            frame, camera_matrix, dist_coeffs, marker_config
        )
        
        if success:
            # Extract position
            camera_pos = -T_world_cam[:3, :3].T @ T_world_cam[:3, 3]
            positions.append(camera_pos)
            
            # Extract orientation (Euler angles)
            R = T_world_cam[:3, :3]
            euler = Rotation.from_matrix(R).as_euler('xyz', degrees=True)
            orientations.append(euler)
    
    cap.release()
    
    # Compute statistics
    positions = np.array(positions)
    orientations = np.array(orientations)
    
    results = {
        'n_samples': len(positions),
        'position_mean': positions.mean(axis=0),
        'position_std': positions.std(axis=0),
        'position_var': positions.var(axis=0),
        'orientation_mean': orientations.mean(axis=0),
        'orientation_std': orientations.std(axis=0),
        'orientation_var': orientations.var(axis=0),
        'max_position_deviation': np.abs(positions - positions.mean(axis=0)).max(axis=0),
        'max_orientation_deviation': np.abs(orientations - orientations.mean(axis=0)).max(axis=0),
    }
    
    # Check criteria
    position_stable = np.all(results['position_std'] < 0.001)  # 1mm
    orientation_stable = np.all(results['orientation_std'] < 0.1)  # 0.1 degrees
    
    results['position_stable'] = position_stable
    results['orientation_stable'] = orientation_stable
    results['overall_stable'] = position_stable and orientation_stable
    
    return results

# Usage
results = test_pose_stability(0, duration_seconds=30)

print(f"Position stability: {results['position_stable']}")
print(f"  Mean position: {results['position_mean']}")
print(f"  Std deviation: {results['position_std']} m")
print(f"  Max deviation: {results['max_position_deviation']} m")

print(f"\nOrientation stability: {results['orientation_stable']}")
print(f"  Mean orientation: {results['orientation_mean']} deg")
print(f"  Std deviation: {results['orientation_std']} deg")
print(f"  Max deviation: {results['max_orientation_deviation']} deg")

print(f"\nOverall stable: {results['overall_stable']}")
```

### Test 2: Reprojection Error Analysis

**Goal**: Verify computed pose accurately explains observations.

**Procedure**:
1. Compute camera extrinsics
2. Project known 3D marker corners back to image
3. Compare projected positions with detected positions
4. Compute mean and max reprojection error

**Success Criteria**:
- Mean reprojection error < 1.0 pixel
- Max reprojection error < 2.0 pixels
- 95% of points have error < 1.5 pixels

**Implementation**:
```python
def test_reprojection_error(image, rvec, tvec, camera_matrix, dist_coeffs, marker_config):
    """
    Test reprojection error for current pose estimate.
    
    Returns:
        results: Dict with error statistics
    """
    # Detect markers
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    corners, ids, _ = cv2.aruco.detectMarkers(image, aruco_dict, parameters=parameters)
    
    if ids is None:
        return None
    
    # Collect correspondences
    object_points = []
    image_points = []
    
    for i, marker_id in enumerate(ids.flatten()):
        if marker_id not in [0, 1, 2, 3]:
            continue
        
        marker_corners = marker_config['markers'][marker_id]['corners']
        for j in range(4):
            object_points.append(marker_corners[j])
            image_points.append(corners[i][0][j])
    
    object_points = np.array(object_points, dtype=np.float32)
    image_points = np.array(image_points, dtype=np.float32)
    
    # Project 3D points using current pose
    projected_points, _ = cv2.projectPoints(
        object_points, rvec, tvec, camera_matrix, dist_coeffs
    )
    projected_points = projected_points.reshape(-1, 2)
    
    # Compute errors
    errors = np.linalg.norm(image_points - projected_points, axis=1)
    
    results = {
        'n_points': len(errors),
        'mean_error': np.mean(errors),
        'std_error': np.std(errors),
        'max_error': np.max(errors),
        'min_error': np.min(errors),
        'percentile_95': np.percentile(errors, 95),
        'errors': errors,
    }
    
    # Check criteria
    results['passes_mean'] = results['mean_error'] < 1.0
    results['passes_max'] = results['max_error'] < 2.0
    results['passes_95th'] = results['percentile_95'] < 1.5
    results['passes_all'] = (results['passes_mean'] and 
                              results['passes_max'] and 
                              results['passes_95th'])
    
    return results

# Usage
ret, frame = cap.read()
success, rvec, tvec, _ = compute_camera_extrinsics(
    frame, camera_matrix, dist_coeffs, marker_config
)

if success:
    results = test_reprojection_error(
        frame, rvec, tvec, camera_matrix, dist_coeffs, marker_config
    )
    
    print(f"Reprojection Error Analysis:")
    print(f"  Mean: {results['mean_error']:.3f} px")
    print(f"  Std: {results['std_error']:.3f} px")
    print(f"  Max: {results['max_error']:.3f} px")
    print(f"  95th percentile: {results['percentile_95']:.3f} px")
    print(f"  Passes criteria: {results['passes_all']}")
```

### Test 3: Marker Detection Consistency

**Goal**: Verify all 4 map anchors are consistently detected.

**Procedure**:
1. Capture N frames (e.g., 100 frames)
2. Count how many frames detect all 4 markers
3. Check for intermittent detection failures

**Success Criteria**:
- Detection rate > 95% (all 4 markers detected in >95% of frames)
- No extended periods without detection (max gap < 5 frames)

**Implementation**:
```python
def test_marker_detection_consistency(video_source, n_frames=100):
    """
    Test consistency of marker detection.
    
    Returns:
        results: Dict with detection statistics
    """
    cap = cv2.VideoCapture(video_source)
    
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    
    detection_results = []
    
    for i in range(n_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
        
        if ids is not None:
            detected_ids = set(ids.flatten())
            all_detected = {0, 1, 2, 3}.issubset(detected_ids)
        else:
            all_detected = False
        
        detection_results.append(all_detected)
    
    cap.release()
    
    detection_results = np.array(detection_results)
    
    # Compute statistics
    detection_rate = np.mean(detection_results) * 100
    
    # Find max gap
    gaps = []
    current_gap = 0
    for detected in detection_results:
        if not detected:
            current_gap += 1
        else:
            if current_gap > 0:
                gaps.append(current_gap)
            current_gap = 0
    if current_gap > 0:
        gaps.append(current_gap)
    
    max_gap = max(gaps) if gaps else 0
    
    results = {
        'n_frames': len(detection_results),
        'detection_rate': detection_rate,
        'max_gap': max_gap,
        'passes_rate': detection_rate > 95,
        'passes_gap': max_gap < 5,
        'passes_all': detection_rate > 95 and max_gap < 5,
    }
    
    return results

# Usage
results = test_marker_detection_consistency(0, n_frames=100)

print(f"Detection Consistency:")
print(f"  Detection rate: {results['detection_rate']:.1f}%")
print(f"  Max detection gap: {results['max_gap']} frames")
print(f"  Passes criteria: {results['passes_all']}")
```

### Test 4: Cross-Validation with Known Distances

**Goal**: Verify world coordinate accuracy using known physical distances.

**Procedure**:
1. Measure actual distance between markers (e.g., diagonal distance)
2. Compute same distance using world coordinates from config
3. Use camera pose to measure distance between detected markers
4. Compare all three measurements

**Success Criteria**:
- Difference < 1% between measured and computed distances

**Implementation**:
```python
def test_distance_validation(rvec, tvec, camera_matrix, dist_coeffs, marker_config):
    """
    Validate pose by checking distances between markers.
    
    Returns:
        results: Dict with distance validation results
    """
    # Known distances from config (ground truth)
    marker_positions = {
        0: np.array(marker_config['markers'][0]['center']),
        1: np.array(marker_config['markers'][1]['center']),
        2: np.array(marker_config['markers'][2]['center']),
        3: np.array(marker_config['markers'][3]['center']),
    }
    
    # Compute expected distances
    expected_distances = {
        'diagonal_02': np.linalg.norm(marker_positions[0] - marker_positions[2]),
        'diagonal_13': np.linalg.norm(marker_positions[1] - marker_positions[3]),
        'edge_01': np.linalg.norm(marker_positions[0] - marker_positions[1]),
        'edge_23': np.linalg.norm(marker_positions[2] - marker_positions[3]),
    }
    
    # TODO: Measure distances from actual detections
    # This would require detecting markers and transforming to world coords
    
    return expected_distances

# Note: Full implementation would transform detected marker positions
# to world coordinates and compare distances
```

## 📊 Validation Report

After running all tests, generate a comprehensive report:

```python
def generate_validation_report(video_source, duration=30):
    """Generate complete validation report."""
    
    print("="*60)
    print("CAMERA POSE VALIDATION REPORT")
    print("="*60)
    
    # Test 1: Stability
    print("\n[Test 1] Pose Stability")
    stability_results = test_pose_stability(video_source, duration)
    print(f"  Status: {'PASS' if stability_results['overall_stable'] else 'FAIL'}")
    print(f"  Position std: {stability_results['position_std']}")
    print(f"  Orientation std: {stability_results['orientation_std']}")
    
    # Test 2: Reprojection Error
    print("\n[Test 2] Reprojection Error")
    cap = cv2.VideoCapture(video_source)
    ret, frame = cap.read()
    success, rvec, tvec, _ = compute_camera_extrinsics(
        frame, camera_matrix, dist_coeffs, marker_config
    )
    if success:
        reproj_results = test_reprojection_error(
            frame, rvec, tvec, camera_matrix, dist_coeffs, marker_config
        )
        print(f"  Status: {'PASS' if reproj_results['passes_all'] else 'FAIL'}")
        print(f"  Mean error: {reproj_results['mean_error']:.3f} px")
        print(f"  Max error: {reproj_results['max_error']:.3f} px")
    cap.release()
    
    # Test 3: Detection Consistency
    print("\n[Test 3] Detection Consistency")
    detection_results = test_marker_detection_consistency(video_source, n_frames=100)
    print(f"  Status: {'PASS' if detection_results['passes_all'] else 'FAIL'}")
    print(f"  Detection rate: {detection_results['detection_rate']:.1f}%")
    print(f"  Max gap: {detection_results['max_gap']} frames")
    
    # Overall result
    print("\n" + "="*60)
    all_pass = (stability_results['overall_stable'] and 
                reproj_results['passes_all'] and 
                detection_results['passes_all'])
    print(f"OVERALL RESULT: {'PASS ✓' if all_pass else 'FAIL ✗'}")
    print("="*60)
    
    return {
        'stability': stability_results,
        'reprojection': reproj_results,
        'detection': detection_results,
        'overall_pass': all_pass,
    }

# Run validation
report = generate_validation_report(0, duration=30)
```

## 🔄 Continuous Monitoring

During operation, continuously monitor pose:

```python
def monitor_pose_health(frame, rvec, tvec, baseline_pose):
    """
    Monitor if current pose deviates from baseline.
    
    Args:
        frame: Current frame
        rvec, tvec: Current pose estimate
        baseline_pose: Reference pose from calibration
    
    Returns:
        healthy: True if pose is within acceptable range
        deviation: Amount of deviation from baseline
    """
    # Compare current pose to baseline
    pos_deviation = np.linalg.norm(tvec - baseline_pose['tvec'])
    rot_deviation = np.linalg.norm(rvec - baseline_pose['rvec'])
    
    # Thresholds
    MAX_POS_DEVIATION = 0.005  # 5mm
    MAX_ROT_DEVIATION = 0.05   # ~3 degrees
    
    healthy = (pos_deviation < MAX_POS_DEVIATION and 
               rot_deviation < MAX_ROT_DEVIATION)
    
    return healthy, {'position': pos_deviation, 'rotation': rot_deviation}
```

## ⚠️ Troubleshooting

**Problem**: High pose variance over time
- **Cause**: Camera mounting is loose or vibrating
- **Solution**: Secure camera mount, add vibration damping

**Problem**: High reprojection error
- **Cause**: Incorrect intrinsic calibration or marker positions
- **Solution**: Re-calibrate camera, verify marker physical positions

**Problem**: Intermittent marker detection
- **Cause**: Lighting issues, reflections, or occlusions
- **Solution**: Improve lighting, check for obstructions, clean markers

**Problem**: Pose jumps between frames
- **Cause**: Ambiguous marker detection or multi-solution PnP
- **Solution**: Use RANSAC, increase marker size, ensure all 4 are visible

## ✅ Sign-Off Checklist

Before considering camera pose validated:

- [ ] Pose stability test passes (variance within limits)
- [ ] Reprojection error test passes (< 1 pixel mean)
- [ ] Detection consistency test passes (> 95% rate)
- [ ] Physical measurements match computed distances
- [ ] Camera mount is secure and vibration-free
- [ ] Validation report generated and saved
- [ ] Baseline pose saved for runtime monitoring

## 📁 Output Files

Save validation results:
```
calibration/
├── validation_report.yaml       # Full validation results
├── baseline_pose.npy           # Reference pose for monitoring
└── validation_plots/           # Visualizations
    ├── pose_stability.png
    ├── reprojection_errors.png
    └── detection_timeline.png
```

## 🔗 Next Steps

After successful validation:
1. Use validated pose in main vision pipeline
2. Enable continuous monitoring during operation
3. Set up alerts for pose degradation
4. Document validation date and conditions

## 📚 References

- Statistical Process Control: https://en.wikipedia.org/wiki/Statistical_process_control
- Camera Pose Estimation Accuracy: https://docs.opencv.org/4.x/d7/d53/tutorial_py_pose.html
