"""
Example: Competition-style ArUco tracking with Kalman filter and occlusion handling.

This example demonstrates a complete tracking pipeline for Eurobot 2026:
1. Multiple marker detection simulation
2. Kalman filtering for smooth tracking
3. Occlusion handling
4. Real-time performance monitoring
"""

import numpy as np
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.kalman_filter.tracker import MultiMarkerTracker, MarkerType, MarkerState
from src.occlusion_handler.handler import OcclusionHandler, DetectionQuality


class CompetitionVisionSystem:
    """
    Complete vision system for Eurobot 2026 competition.
    
    This system integrates:
    - Multi-marker tracking
    - Kalman filtering
    - Occlusion handling
    - Performance monitoring
    """
    
    def __init__(self):
        """Initialize the vision system."""
        self.tracker = MultiMarkerTracker(
            process_noise=0.01,
            measurement_noise=0.1,
            max_frames_without_detection=30
        )
        
        self.occlusion_handler = OcclusionHandler(
            history_length=30,
            partial_detection_threshold=0.5,
            occlusion_timeout=1.0
        )
        
        self.frame_count = 0
        self.start_time = time.time()
        
    def process_frame(self, detections: dict, dt: float = 0.033):
        """
        Process a single frame of detections.
        
        Args:
            detections: Dict mapping marker_id to (x, y, theta)
            dt: Time since last frame in seconds
            
        Returns:
            Dict of tracked marker states
        """
        # Update tracker with detections
        states = self.tracker.update(detections, dt)
        
        # Handle occlusion for each marker
        for marker_id, state in states.items():
            if state.is_occluded:
                # Marker is being predicted by Kalman filter
                self.occlusion_handler.add_to_history(
                    marker_id,
                    (state.x, state.y, state.theta)
                )
            elif marker_id in detections:
                # Good detection
                self.occlusion_handler.add_to_history(
                    marker_id,
                    detections[marker_id]
                )
        
        self.frame_count += 1
        
        return states
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics."""
        elapsed_time = time.time() - self.start_time
        fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
        
        tracking_summary = self.tracker.get_tracking_summary()
        occlusion_stats = self.occlusion_handler.get_occlusion_statistics()
        
        return {
            'fps': fps,
            'frames_processed': self.frame_count,
            'elapsed_time': elapsed_time,
            'tracking': tracking_summary,
            'occlusion': occlusion_stats
        }
    
    def print_status(self):
        """Print current system status."""
        stats = self.get_performance_stats()
        
        print(f"\n{'='*60}")
        print(f"Vision System Status - Frame {self.frame_count}")
        print(f"{'='*60}")
        print(f"Performance: {stats['fps']:.1f} FPS")
        print(f"\nTracked Markers:")
        print(f"  Total: {stats['tracking']['total_markers']}")
        print(f"  Map: {stats['tracking']['map_markers']}")
        print(f"  Caisse: {stats['tracking']['caisse_markers']}")
        print(f"  Enemy: {stats['tracking']['enemy_markers']}")
        print(f"  Occluded: {stats['tracking']['occluded_markers']}")
        print(f"\nOcclusion Events:")
        print(f"  Partial: {stats['occlusion']['partial_detections']}")
        print(f"  Full: {stats['occlusion']['full_occlusions']}")
        print(f"{'='*60}\n")


def simulate_competition_scenario():
    """
    Simulate a competition scenario with multiple markers and various challenges.
    """
    print("\n" + "="*60)
    print("COMPETITION SCENARIO SIMULATION")
    print("="*60)
    print("\nSimulating 10 seconds of competition with:")
    print("  - 4 map markers (IDs 20-23) at fixed positions")
    print("  - 3 caisse markers (IDs 36, 47, 41) moving slowly")
    print("  - 1 enemy marker (ID 30) moving fast")
    print("  - Random frame drops and occlusion")
    print()
    
    # Initialize system
    vision_system = CompetitionVisionSystem()
    
    # Simulation parameters
    fps = 30
    dt = 1.0 / fps
    duration = 10.0  # seconds
    total_frames = int(duration * fps)
    
    # Initialize marker positions
    # Map markers (fixed at corners)
    map_positions = {
        20: np.array([0.0, 0.0, 0.0]),
        21: np.array([2.0, 0.0, 0.0]),
        22: np.array([2.0, 1.5, 0.0]),
        23: np.array([0.0, 1.5, 0.0])
    }
    
    # Caisse markers (slow motion)
    caisse_positions = {
        36: {'pos': np.array([0.5, 0.5, 0.2]), 'vel': np.array([0.02, 0.01, 0.05])},
        47: {'pos': np.array([1.0, 0.8, -0.3]), 'vel': np.array([-0.01, 0.02, -0.03])},
        41: {'pos': np.array([1.5, 0.4, 0.5]), 'vel': np.array([0.01, -0.01, 0.02])}
    }
    
    # Enemy marker (fast motion)
    enemy_positions = {
        30: {'pos': np.array([1.0, 1.0, 0.0]), 'vel': np.array([0.1, 0.05, 0.3])}
    }
    
    # Run simulation
    for frame in range(total_frames):
        # Update positions
        for marker_id, data in caisse_positions.items():
            data['pos'] += data['vel'] * dt
            # Bounce off walls
            if data['pos'][0] < 0.1 or data['pos'][0] > 1.9:
                data['vel'][0] *= -1
            if data['pos'][1] < 0.1 or data['pos'][1] > 1.4:
                data['vel'][1] *= -1
        
        for marker_id, data in enemy_positions.items():
            data['pos'] += data['vel'] * dt
            # Bounce off walls
            if data['pos'][0] < 0.2 or data['pos'][0] > 1.8:
                data['vel'][0] *= -1
            if data['pos'][1] < 0.2 or data['pos'][1] > 1.3:
                data['vel'][1] *= -1
        
        # Simulate frame drop (10% probability)
        if np.random.random() < 0.1:
            detections = {}
        else:
            detections = {}
            
            # Add map markers (always visible unless occluded)
            for marker_id, pos in map_positions.items():
                if np.random.random() > 0.05:  # 5% occlusion
                    noise = np.random.normal(0, 0.001, 3)
                    detections[marker_id] = tuple(pos + noise)
            
            # Add caisse markers
            for marker_id, data in caisse_positions.items():
                if np.random.random() > 0.15:  # 15% occlusion
                    noise = np.random.normal(0, 0.005, 3)
                    detections[marker_id] = tuple(data['pos'] + noise)
            
            # Add enemy marker
            for marker_id, data in enemy_positions.items():
                if np.random.random() > 0.20:  # 20% occlusion (enemy more likely occluded)
                    noise = np.random.normal(0, 0.01, 3)
                    detections[marker_id] = tuple(data['pos'] + noise)
        
        # Process frame
        states = vision_system.process_frame(detections, dt)
        
        # Print status every 2 seconds
        if (frame + 1) % (fps * 2) == 0:
            vision_system.print_status()
            
            # Print detailed marker states
            print("Detailed Marker States:")
            for marker_id, state in sorted(states.items()):
                status = "OCCLUDED" if state.is_occluded else "TRACKED"
                print(f"  Marker {marker_id:2d} ({state.marker_type.value:6s}): "
                      f"x={state.x:5.2f}m, y={state.y:5.2f}m, θ={state.theta:5.2f}rad "
                      f"[{status}] conf={state.confidence:.2f}")
    
    # Final summary
    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)
    vision_system.print_status()
    
    final_stats = vision_system.get_performance_stats()
    print("\nFinal Performance:")
    print(f"  Average FPS: {final_stats['fps']:.1f}")
    print(f"  Frames processed: {final_stats['frames_processed']}")
    print(f"  Total time: {final_stats['elapsed_time']:.2f} seconds")


def demonstrate_occlusion_recovery():
    """
    Demonstrate occlusion handling and recovery.
    """
    print("\n" + "="*60)
    print("OCCLUSION RECOVERY DEMONSTRATION")
    print("="*60)
    print("\nDemonstrating Kalman filter prediction during occlusion")
    print()
    
    vision_system = CompetitionVisionSystem()
    
    # Simulate enemy marker with planned occlusion
    dt = 0.033
    enemy_pos = np.array([1.0, 1.0, 0.0])
    enemy_vel = np.array([0.1, 0.05, 0.2])
    
    for frame in range(150):  # 5 seconds
        enemy_pos += enemy_vel * dt
        
        # Simulate occlusion from frame 60 to 90 (1 second)
        is_occluded = 60 <= frame < 90
        
        if is_occluded:
            detections = {}  # No detection during occlusion
        else:
            noise = np.random.normal(0, 0.01, 3)
            detections = {30: tuple(enemy_pos + noise)}
        
        states = vision_system.process_frame(detections, dt)
        
        # Print every 15 frames
        if (frame + 1) % 15 == 0:
            if 30 in states:
                state = states[30]
                actual_pos = enemy_pos
                error = np.sqrt((state.x - actual_pos[0])**2 + 
                              (state.y - actual_pos[1])**2)
                
                status = "OCCLUDED - PREDICTING" if is_occluded else "TRACKING"
                print(f"Frame {frame+1:3d}: {status:25s} | "
                      f"Pos: ({state.x:.2f}, {state.y:.2f}) | "
                      f"Error: {error:.3f}m | "
                      f"Confidence: {state.confidence:.2f}")
    
    print("\nOcclusion recovery demonstration complete!")


if __name__ == "__main__":
    # Run competition scenario
    simulate_competition_scenario()
    
    # Demonstrate occlusion recovery
    demonstrate_occlusion_recovery()
