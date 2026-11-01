"""
Stress tests for multiple ArUco marker detection and tracking.

This module tests the vision system under heavy load:
- Multiple map markers (IDs 20-23)
- Multiple caisse markers (IDs 36, 47, 41 - competition spec)
- Multiple enemy markers (IDs 30+)
- Occlusion scenarios
- Frame drops
"""

import numpy as np
import time
from typing import Dict, List, Tuple
import json
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.kalman_filter.tracker import MultiMarkerTracker, MarkerType
from src.occlusion_handler.handler import OcclusionHandler, DetectionQuality


@dataclass
class StressTestConfig:
    """Configuration for stress tests."""
    num_map_markers: int = 4
    num_caisse_markers: int = 3  # Fixed: IDs 36, 47, 41 (competition spec)
    num_enemy_markers: int = 2
    test_duration_frames: int = 300  # 10 seconds at 30 FPS
    frame_drop_probability: float = 0.1
    occlusion_probability: float = 0.15
    partial_occlusion_probability: float = 0.1
    fps: int = 30


@dataclass
class StressTestResults:
    """Results from a stress test."""
    config: StressTestConfig
    total_frames: int
    frames_processed: int
    frames_dropped: int
    total_detections: int
    successful_tracks: int
    lost_tracks: int
    occlusion_events: int
    partial_occlusion_events: int
    average_processing_time_ms: float
    max_processing_time_ms: float
    tracking_accuracy: float
    
    def to_dict(self):
        """Convert to dictionary."""
        result = asdict(self)
        result['config'] = asdict(self.config)
        return result
    
    def print_summary(self):
        """Print test results summary."""
        print("\n" + "="*60)
        print("STRESS TEST RESULTS")
        print("="*60)
        print(f"\nTest Configuration:")
        print(f"  Map markers: {self.config.num_map_markers}")
        print(f"  Caisse markers: {self.config.num_caisse_markers}")
        print(f"  Enemy markers: {self.config.num_enemy_markers}")
        print(f"  Total markers: {self.config.num_map_markers + self.config.num_caisse_markers + self.config.num_enemy_markers}")
        print(f"\nPerformance Metrics:")
        print(f"  Frames processed: {self.frames_processed}/{self.total_frames}")
        print(f"  Frames dropped: {self.frames_dropped} ({self.frames_dropped/self.total_frames*100:.1f}%)")
        print(f"  Average processing time: {self.average_processing_time_ms:.2f} ms")
        print(f"  Max processing time: {self.max_processing_time_ms:.2f} ms")
        print(f"\nTracking Metrics:")
        print(f"  Total detections: {self.total_detections}")
        print(f"  Successful tracks: {self.successful_tracks}")
        print(f"  Lost tracks: {self.lost_tracks}")
        print(f"  Tracking accuracy: {self.tracking_accuracy*100:.1f}%")
        print(f"\nOcclusion Handling:")
        print(f"  Full occlusion events: {self.occlusion_events}")
        print(f"  Partial occlusion events: {self.partial_occlusion_events}")
        print("="*60 + "\n")


class MarkerSimulator:
    """Simulates ArUco marker detections for testing."""
    
    def __init__(self, config: StressTestConfig):
        self.config = config
        
        # Initialize marker positions
        # Map anchors at corners (fixed) - Eurobot 2026 IDs 20-23
        self.map_markers = {
            20: (0.0, 0.0, 0.0),
            21: (2.0, 0.0, 0.0),
            22: (2.0, 1.5, 0.0),
            23: (0.0, 1.5, 0.0)
        }
        
        # Caisse markers randomly placed (competition IDs: 36, 47, 41)
        self.caisse_markers = {}
        caisse_ids = [36, 47, 41]  # Blue, Yellow, Black (competition spec)
        for i, marker_id in enumerate(caisse_ids):
            if i >= config.num_caisse_markers:
                break
            x = np.random.uniform(0.2, 1.8)
            y = np.random.uniform(0.2, 1.3)
            theta = np.random.uniform(-np.pi, np.pi)
            # Caisses have slow random motion
            vx = np.random.uniform(-0.01, 0.01)
            vy = np.random.uniform(-0.01, 0.01)
            vtheta = np.random.uniform(-0.05, 0.05)
            self.caisse_markers[marker_id] = {
                'pose': (x, y, theta),
                'velocity': (vx, vy, vtheta)
            }
        
        # Enemy markers with faster motion
        self.enemy_markers = {}
        for i in range(config.num_enemy_markers):
            marker_id = 30 + i
            x = np.random.uniform(0.3, 1.7)
            y = np.random.uniform(0.3, 1.2)
            theta = np.random.uniform(-np.pi, np.pi)
            vx = np.random.uniform(-0.1, 0.1)
            vy = np.random.uniform(-0.1, 0.1)
            vtheta = np.random.uniform(-0.2, 0.2)
            self.enemy_markers[marker_id] = {
                'pose': (x, y, theta),
                'velocity': (vx, vy, vtheta)
            }
    
    def update_positions(self, dt: float = 0.033):
        """Update marker positions based on velocities."""
        # Map markers are fixed
        
        # Update caisse markers
        for marker_id, data in self.caisse_markers.items():
            x, y, theta = data['pose']
            vx, vy, vtheta = data['velocity']
            
            x += vx * dt
            y += vy * dt
            theta += vtheta * dt
            
            # Keep within bounds
            x = np.clip(x, 0.1, 1.9)
            y = np.clip(y, 0.1, 1.4)
            
            # Normalize theta
            while theta > np.pi:
                theta -= 2 * np.pi
            while theta < -np.pi:
                theta += 2 * np.pi
            
            data['pose'] = (x, y, theta)
        
        # Update enemy markers
        for marker_id, data in self.enemy_markers.items():
            x, y, theta = data['pose']
            vx, vy, vtheta = data['velocity']
            
            x += vx * dt
            y += vy * dt
            theta += vtheta * dt
            
            # Keep within bounds
            x = np.clip(x, 0.2, 1.8)
            y = np.clip(y, 0.2, 1.3)
            
            # Normalize theta
            while theta > np.pi:
                theta -= 2 * np.pi
            while theta < -np.pi:
                theta += 2 * np.pi
            
            data['pose'] = (x, y, theta)
    
    def get_detections(self, frame_drop: bool = False,
                      occluded_markers: List[int] = None,
                      partial_occluded_markers: List[int] = None) -> Dict[int, Tuple[float, float, float]]:
        """
        Get current marker detections with noise.
        
        Args:
            frame_drop: If True, return empty detections
            occluded_markers: List of marker IDs that are fully occluded
            partial_occluded_markers: List of marker IDs that are partially occluded
            
        Returns:
            Dictionary of marker_id -> (x, y, theta)
        """
        if frame_drop:
            return {}
        
        occluded_markers = occluded_markers or []
        partial_occluded_markers = partial_occluded_markers or []
        
        detections = {}
        
        # Add map markers
        for marker_id, pose in self.map_markers.items():
            if marker_id not in occluded_markers:
                # Add small noise
                noise_x = np.random.normal(0, 0.001)
                noise_y = np.random.normal(0, 0.001)
                noise_theta = np.random.normal(0, 0.01)
                
                if marker_id in partial_occluded_markers:
                    # Larger noise for partial occlusion
                    noise_x *= 5
                    noise_y *= 5
                    noise_theta *= 5
                
                detections[marker_id] = (
                    pose[0] + noise_x,
                    pose[1] + noise_y,
                    pose[2] + noise_theta
                )
        
        # Add caisse markers
        for marker_id, data in self.caisse_markers.items():
            if marker_id not in occluded_markers:
                pose = data['pose']
                noise_x = np.random.normal(0, 0.005)
                noise_y = np.random.normal(0, 0.005)
                noise_theta = np.random.normal(0, 0.02)
                
                if marker_id in partial_occluded_markers:
                    noise_x *= 3
                    noise_y *= 3
                    noise_theta *= 3
                
                detections[marker_id] = (
                    pose[0] + noise_x,
                    pose[1] + noise_y,
                    pose[2] + noise_theta
                )
        
        # Add enemy markers
        for marker_id, data in self.enemy_markers.items():
            if marker_id not in occluded_markers:
                pose = data['pose']
                noise_x = np.random.normal(0, 0.01)
                noise_y = np.random.normal(0, 0.01)
                noise_theta = np.random.normal(0, 0.03)
                
                if marker_id in partial_occluded_markers:
                    noise_x *= 2
                    noise_y *= 2
                    noise_theta *= 2
                
                detections[marker_id] = (
                    pose[0] + noise_x,
                    pose[1] + noise_y,
                    pose[2] + noise_theta
                )
        
        return detections


def run_stress_test(config: StressTestConfig = None) -> StressTestResults:
    """
    Run a stress test on the tracking system.
    
    Args:
        config: Test configuration
        
    Returns:
        Test results
    """
    if config is None:
        config = StressTestConfig()
    
    print(f"\nStarting stress test with {config.num_map_markers + config.num_caisse_markers + config.num_enemy_markers} markers...")
    
    # Initialize systems
    tracker = MultiMarkerTracker(
        process_noise=0.01,
        measurement_noise=0.1,
        max_frames_without_detection=30
    )
    
    simulator = MarkerSimulator(config)
    
    # Test metrics
    dt = 1.0 / config.fps
    processing_times = []
    total_detections = 0
    frames_dropped = 0
    occlusion_events = 0
    partial_occlusion_events = 0
    
    all_marker_ids = (
        list(range(config.num_map_markers)) +
        [36, 47, 41][:config.num_caisse_markers] +  # Competition caisse IDs
        list(range(30, 30 + config.num_enemy_markers))
    )
    
    # Run test
    for frame in range(config.test_duration_frames):
        # Update simulator
        simulator.update_positions(dt)
        
        # Simulate frame drops
        frame_drop = np.random.random() < config.frame_drop_probability
        if frame_drop:
            frames_dropped += 1
        
        # Simulate occlusion
        occluded = []
        partial_occluded = []
        for marker_id in all_marker_ids:
            if np.random.random() < config.occlusion_probability:
                occluded.append(marker_id)
                occlusion_events += 1
            elif np.random.random() < config.partial_occlusion_probability:
                partial_occluded.append(marker_id)
                partial_occlusion_events += 1
        
        # Get detections
        detections = simulator.get_detections(
            frame_drop=frame_drop,
            occluded_markers=occluded,
            partial_occluded_markers=partial_occluded
        )
        
        total_detections += len(detections)
        
        # Process with tracker
        start_time = time.time()
        states = tracker.update(detections, dt)
        processing_time = (time.time() - start_time) * 1000  # ms
        processing_times.append(processing_time)
        
        # Progress indicator
        if (frame + 1) % 50 == 0:
            print(f"  Frame {frame + 1}/{config.test_duration_frames} - "
                  f"Tracking {len(states)} markers - "
                  f"Avg processing: {np.mean(processing_times[-50:]):.2f} ms")
    
    # Calculate results
    final_states = tracker.get_all_states()
    successful_tracks = len([s for s in final_states.values() if not s.is_occluded])
    lost_tracks = len(all_marker_ids) - len(final_states)
    
    tracking_accuracy = successful_tracks / len(all_marker_ids) if all_marker_ids else 0.0
    
    results = StressTestResults(
        config=config,
        total_frames=config.test_duration_frames,
        frames_processed=config.test_duration_frames - frames_dropped,
        frames_dropped=frames_dropped,
        total_detections=total_detections,
        successful_tracks=successful_tracks,
        lost_tracks=lost_tracks,
        occlusion_events=occlusion_events,
        partial_occlusion_events=partial_occlusion_events,
        average_processing_time_ms=np.mean(processing_times),
        max_processing_time_ms=np.max(processing_times),
        tracking_accuracy=tracking_accuracy
    )
    
    return results


def run_multiple_stress_tests():
    """Run multiple stress test scenarios."""
    print("\n" + "="*60)
    print("RUNNING MULTIPLE STRESS TEST SCENARIOS")
    print("="*60)
    
    scenarios = [
        ("Light Load", StressTestConfig(
            num_map_markers=4,
            num_caisse_markers=2,  # 2 of 3 caisses (36, 47)
            num_enemy_markers=1,
            frame_drop_probability=0.05,
            occlusion_probability=0.1
        )),
        ("Medium Load", StressTestConfig(
            num_map_markers=4,
            num_caisse_markers=3,  # All 3 caisses (36, 47, 41)
            num_enemy_markers=2,
            frame_drop_probability=0.1,
            occlusion_probability=0.15
        )),
        ("Heavy Load", StressTestConfig(
            num_map_markers=4,
            num_caisse_markers=3,  # All 3 caisses (fixed in competition)
            num_enemy_markers=3,
            frame_drop_probability=0.15,
            occlusion_probability=0.2
        )),
        ("Extreme Load", StressTestConfig(
            num_map_markers=4,
            num_caisse_markers=3,  # All 3 caisses (competition limit)
            num_enemy_markers=4,
            test_duration_frames=200,
            frame_drop_probability=0.2,
            occlusion_probability=0.25
        ))
    ]
    
    all_results = []
    
    for name, config in scenarios:
        print(f"\n{'='*60}")
        print(f"Scenario: {name}")
        print(f"{'='*60}")
        
        results = run_stress_test(config)
        results.print_summary()
        all_results.append((name, results))
    
    # Save all results to JSON
    output_file = "/tmp/stress_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(
            {name: results.to_dict() for name, results in all_results},
            f,
            indent=2
        )
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    # Run default stress test
    results = run_stress_test()
    results.print_summary()
    
    # Uncomment to run all scenarios
    # run_multiple_stress_tests()
