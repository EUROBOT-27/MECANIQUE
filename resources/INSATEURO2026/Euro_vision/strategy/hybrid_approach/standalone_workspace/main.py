"""
Standalone Hybrid Supervisor - Visualization & Testing

This workspace allows you to test the hybrid supervisor without ROS2/DDS.
Perfect for development, debugging, and visualizing the decision flow.

Features:
- Interactive CV windows showing world state
- Simulated waypoint input (keyboard or predefined)
- Real-time enemy tracking with Kalman filter
- Visual threat zones and path planning
- No ROS dependencies

Usage:
    python main.py --camera 1
    python main.py --mock  # Use simulated data instead of camera
"""

import cv2
import numpy as np
import sys
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import time

# Add parent paths for imports
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root / "kalman_filter" / "src"))
sys.path.insert(0, str(repo_root / "path_planning" / "utils"))
sys.path.insert(0, str(repo_root / "full_pipeline" / "scripts" / "utils"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import core modules
from src.crate_flip_manager import CrateFlipManager
from utils.config import StrategyConfig, DEFAULT_CONFIG
from utils.world_state import WorldState, CrateInfo, EnemyInfo, RobotPose
from utils.world_state import CrateOwnership, CrateContainer
from utils.crate_id_tracker import CrateIDTracker
from kalman_filter.src.kalman_filter.tracker import MultiMarkerTracker
from path_planning.utils.rrt_connect import rrt_connect_plan
from path_planning.utils.path_smoothing import smooth_path


class StandaloneHybridSupervisor:
    """
    Standalone hybrid supervisor for visualization and testing.
    
    Simulates the ROS2 workflow:
    1. Receive destination waypoint (keyboard input or mock)
    2. Analyze enemy threat using Kalman predictions
    3. If safe: Compute RRT path, display waypoints
    4. If unsafe: Display rejection reason
    5. Continuous enemy monitoring
    """
    
    def __init__(self, config=None, team_color="blue", use_mock_data=False):
        self.config = config or DEFAULT_CONFIG
        self.team_color = team_color
        self.use_mock_data = use_mock_data
        
        # Core components
        self.flip_manager = CrateFlipManager(self.config, team_color)
        self.crate_tracker = CrateIDTracker()
        self.kalman_tracker = MultiMarkerTracker(
            process_noise=0.01,
            measurement_noise=0.1,
            max_frames_without_detection=30
        )
        
        # State
        self.world_state = WorldState()
        self.current_destination = None
        self.last_decision = None
        self.enemy_threat_level = "NONE"
        
        # Visualization
        self.vis_frame = None
        
    def receive_destination(self, waypoint: Tuple[float, float]) -> None:
        """Simulate receiving destination from Raspberry Pi."""
        self.current_destination = waypoint
        print(f"\n📍 RECEIVED DESTINATION: {waypoint}")
        
    def analyze_waypoint(self) -> Dict:
        """
        Analyze current waypoint for safety and feasibility.
        
        Returns:
            {
                'status': 'ACCEPT' or 'REJECT',
                'reason': str,
                'waypoints': List[Tuple[float, float]] or None,
                'threat_level': str
            }
        """
        if not self.current_destination:
            return {'status': 'REJECT', 'reason': 'No destination set', 
                    'waypoints': None, 'threat_level': 'NONE'}
        
        # Get enemy state from Kalman
        enemy_state = self._get_enemy_state()
        
        if not enemy_state:
            # No enemy detected - safe to proceed
            path = self._compute_optimized_path(self.current_destination)
            return {
                'status': 'ACCEPT',
                'reason': 'No enemy threat detected',
                'waypoints': path,
                'threat_level': 'NONE'
            }
        
        # Predict enemy position in 3 seconds
        predicted_pos = (
            enemy_state.x + enemy_state.vx * 3.0,
            enemy_state.y + enemy_state.vy * 3.0
        )
        
        # Check if destination is near predicted enemy position
        dest_x, dest_y = self.current_destination
        threat_distance = np.sqrt(
            (dest_x - predicted_pos[0])**2 + 
            (dest_y - predicted_pos[1])**2
        )
        
        threat_threshold = self.config.enemy_danger_radius
        
        if threat_distance < threat_threshold:
            # REJECT - enemy too close to destination
            return {
                'status': 'REJECT',
                'reason': f'Enemy predicted at {predicted_pos} (distance: {threat_distance:.2f}m)',
                'waypoints': None,
                'threat_level': 'HIGH'
            }
        
        # ACCEPT - compute path avoiding enemy
        obstacles = [predicted_pos] if enemy_state else []
        path = self._compute_optimized_path(self.current_destination, obstacles)
        
        return {
            'status': 'ACCEPT',
            'reason': f'Path clear (enemy distance: {threat_distance:.2f}m)',
            'waypoints': path,
            'threat_level': 'LOW' if threat_distance < threat_threshold * 2 else 'NONE'
        }
    
    def _get_enemy_state(self):
        """Get enemy state from Kalman tracker."""
        # Assuming enemy is marker ID 30
        enemy_id = 30
        if hasattr(self.kalman_tracker, 'trackers') and enemy_id in self.kalman_tracker.trackers:
            return self.kalman_tracker.trackers[enemy_id].get_state()
        return None
    
    def _compute_optimized_path(self, goal: Tuple[float, float], 
                                obstacles: List = None) -> List[Tuple[float, float]]:
        """Compute RRT-Connect path and smooth it."""
        start = (self.world_state.robot_pose.x, self.world_state.robot_pose.y)
        
        # Simple straight path if no obstacles
        if not obstacles:
            return [start, goal]
        
        # RRT-Connect planning
        try:
            path = rrt_connect_plan(
                start, goal, obstacles,
                step_size=self.config.path_planning_step_size,
                max_iter=self.config.path_planning_max_iter
            )
            
            if path:
                # Smooth the path
                return smooth_path(path)
            else:
                # Fallback to direct path
                return [start, goal]
        except:
            # If planning fails, return direct path
            return [start, goal]
    
    def update_world_state(self, detections: Dict) -> None:
        """Update world state from vision detections."""
        # Update Kalman tracker
        kalman_detections = {}
        for marker_id, (x, y, theta) in detections.items():
            kalman_detections[marker_id] = (x, y, theta)
        
        self.kalman_tracker.update(kalman_detections, dt=1/30)
        
        # Update crate tracking
        crate_detections = [
            {'id': mid, 'pos': (x, y, theta), 
             'ownership': 'ours' if mid == 36 else 'opponent',
             'container': 'free', 'confidence': 1.0}
            for mid, (x, y, theta) in detections.items()
            if mid in [36, 47]
        ]
        
        unique_crates = self.crate_tracker.assign_unique_ids(crate_detections)
        
        # Update world state
        self.world_state.crates = [
            CrateInfo(
                unique_id=c['unique_id'],
                id=c['id'],
                pos=c['pos'],
                ownership=CrateOwnership.OURS if c['ownership'] == 'ours' else CrateOwnership.OPPONENT,
                container=CrateContainer.FREE,
                confidence=c['confidence']
            )
            for c in unique_crates
        ]
        
        # Update enemy info
        enemy_state = self._get_enemy_state()
        if enemy_state:
            self.world_state.enemy = EnemyInfo(
                id=30,
                pos=(enemy_state.x, enemy_state.y, enemy_state.theta),
                velocity=(enemy_state.vx, enemy_state.vy),
                confidence=enemy_state.confidence
            )
    
    def visualize(self, frame: np.ndarray) -> np.ndarray:
        """Draw world state and decisions on frame."""
        vis = frame.copy()
        h, w = vis.shape[:2]
        
        # Draw field boundaries
        field_w_px = int(self.config.field_width * 200)  # 200 px/meter
        field_h_px = int(self.config.field_length * 200)
        
        # Draw destination
        if self.current_destination:
            dest_x = int(self.current_destination[0] * 200)
            dest_y = h - int(self.current_destination[1] * 200)
            cv2.circle(vis, (dest_x, dest_y), 10, (0, 255, 0), -1)
            cv2.putText(vis, "DEST", (dest_x + 15, dest_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw enemy with threat zone
        if self.world_state.enemy:
            enemy_x = int(self.world_state.enemy.pos[0] * 200)
            enemy_y = h - int(self.world_state.enemy.pos[1] * 200)
            
            # Threat radius
            threat_radius = int(self.config.enemy_danger_radius * 200)
            cv2.circle(vis, (enemy_x, enemy_y), threat_radius, (0, 0, 255), 2)
            
            # Enemy position
            cv2.circle(vis, (enemy_x, enemy_y), 8, (0, 0, 255), -1)
            
            # Velocity arrow
            vx, vy = self.world_state.enemy.velocity
            end_x = int((self.world_state.enemy.pos[0] + vx * 3) * 200)
            end_y = h - int((self.world_state.enemy.pos[1] + vy * 3) * 200)
            cv2.arrowedLine(vis, (enemy_x, enemy_y), (end_x, end_y), 
                           (0, 165, 255), 2, tipLength=0.3)
        
        # Draw decision status
        if self.last_decision:
            status_color = (0, 255, 0) if self.last_decision['status'] == 'ACCEPT' else (0, 0, 255)
            cv2.putText(vis, f"STATUS: {self.last_decision['status']}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
            cv2.putText(vis, f"Threat: {self.last_decision['threat_level']}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            
            # Draw waypoints if accepted
            if self.last_decision['waypoints']:
                for i, (wx, wy) in enumerate(self.last_decision['waypoints']):
                    wp_x = int(wx * 200)
                    wp_y = h - int(wy * 200)
                    cv2.circle(vis, (wp_x, wp_y), 4, (255, 255, 0), -1)
                    if i > 0:
                        prev_x = int(self.last_decision['waypoints'][i-1][0] * 200)
                        prev_y = h - int(self.last_decision['waypoints'][i-1][1] * 200)
                        cv2.line(vis, (prev_x, prev_y), (wp_x, wp_y), (255, 255, 0), 2)
        
        return vis
    
    def run(self):
        """Main loop for standalone testing."""
        print("🚀 Standalone Hybrid Supervisor")
        print("Controls:")
        print("  - Click on frame to set destination")
        print("  - SPACE: Analyze current destination")
        print("  - R: Request new destination (simulate REPLAN)")
        print("  - ESC: Quit")
        
        if self.use_mock_data:
            self._run_mock_mode()
        else:
            self._run_camera_mode()
    
    def _run_mock_mode(self):
        """Run with simulated data."""
        print("\n📊 MOCK MODE - Using simulated data")
        
        # Simulate some scenarios
        scenarios = [
            {
                'name': 'Safe waypoint - no enemy',
                'destination': (1.5, 1.0),
                'enemy': None
            },
            {
                'name': 'Threatened waypoint - enemy nearby',
                'destination': (1.2, 0.8),
                'enemy': {'pos': (1.3, 0.9, 0.0), 'vel': (0.1, -0.05)}
            },
            {
                'name': 'Safe waypoint - enemy far',
                'destination': (2.5, 1.5),
                'enemy': {'pos': (0.5, 0.5, 0.0), 'vel': (0.0, 0.0)}
            }
        ]
        
        for scenario in scenarios:
            print(f"\n{'='*60}")
            print(f"Scenario: {scenario['name']}")
            print(f"{'='*60}")
            
            # Set destination
            self.receive_destination(scenario['destination'])
            
            # Mock enemy if present
            if scenario['enemy']:
                enemy_data = scenario['enemy']
                # Directly set world state enemy
                self.world_state.enemy = EnemyInfo(
                    id=30,
                    pos=enemy_data['pos'],
                    velocity=enemy_data['vel'],
                    confidence=0.95
                )
                
                # Also update Kalman tracker manually
                self.kalman_tracker.update({30: enemy_data['pos']}, dt=1/30)
            else:
                self.world_state.enemy = None
            
            # Analyze
            decision = self.analyze_waypoint()
            self.last_decision = decision
            
            # Print results
            print(f"\n🎯 DECISION: {decision['status']}")
            print(f"   Reason: {decision['reason']}")
            print(f"   Threat Level: {decision['threat_level']}")
            if decision['waypoints']:
                print(f"   Waypoints ({len(decision['waypoints'])}):")
                for i, wp in enumerate(decision['waypoints']):
                    print(f"      {i+1}. ({wp[0]:.2f}, {wp[1]:.2f})")
            
            time.sleep(1)
    
    def _run_camera_mode(self):
        """Run with live camera feed (placeholder for full integration)."""
        print("\n📹 CAMERA MODE - Would integrate with full_pipeline here")
        print("   For now, falling back to mock mode...")
        self._run_mock_mode()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Standalone Hybrid Supervisor")
    parser.add_argument('--camera', type=int, default=1, help='Camera ID')
    parser.add_argument('--mock', action='store_true', help='Use mock data')
    parser.add_argument('--team', choices=['blue', 'yellow'], default='blue')
    args = parser.parse_args()
    
    supervisor = StandaloneHybridSupervisor(
        team_color=args.team,
        use_mock_data=args.mock
    )
    
    supervisor.run()


if __name__ == "__main__":
    main()
