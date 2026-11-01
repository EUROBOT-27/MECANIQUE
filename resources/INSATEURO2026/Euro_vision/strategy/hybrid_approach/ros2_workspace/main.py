"""
ROS2 Hybrid Supervisor - Production Integration

This workspace integrates with ROS2/DDS for production deployment.
Receives destinations from Raspberry Pi, analyzes them, and sends back decisions.

ROS2 Topics:
- Subscribe: /navigation/destination (geometry_msgs/Point + std_msgs/String)
- Publish: /navigation/decision (custom NavigationDecision message)
- Publish: /navigation/waypoints (nav_msgs/Path)

Architecture:
1. DDS subscriber receives destination from Raspberry Pi
2. Supervisor analyzes waypoint with Kalman-based threat assessment
3. If ACCEPT: Compute RRT path, publish waypoints
4. If REJECT: Publish rejection flag + reason, wait for new destination
5. Continuous enemy monitoring at 30Hz

Usage (when ROS2 is configured):
    ros2 run hybrid_supervisor main.py --team blue
    
Testing without ROS2:
    python main.py --test  # Uses placeholders and mock data
"""


from pathlib import Path
from typing import Optional, Tuple, List, Dict
import time
import json



# Core imports
from src.crate_flip_manager import CrateFlipManager
from utils.config import StrategyConfig, DEFAULT_CONFIG
from utils.world_state import WorldState, CrateInfo, EnemyInfo, RobotPose
from utils.world_state import CrateOwnership, CrateContainer
from utils.crate_id_tracker import CrateIDTracker
from kalman_filter.src.kalman_filter.tracker import MultiMarkerTracker
from path_planning.utils.rrt_connect import rrt_connect_plan
from path_planning.utils.path_smoothing import smooth_path

# ROS2 imports (placeholders - will be replaced with actual imports)
try:
    # import rclpy
    # from rclpy.node import Node
    # from geometry_msgs.msg import Point, PoseStamped
    # from nav_msgs.msg import Path
    # from std_msgs.msg import String, Bool
    ROS2_AVAILABLE = False  # Set to True when ROS2 is installed
except ImportError:
    ROS2_AVAILABLE = False


class NavigationDecision:
    """
    Placeholder for custom ROS2 message.
    
    In production, this should be defined in a ROS2 package:
    
    # NavigationDecision.msg
    std_msgs/Header header
    string status          # "ACCEPT" or "REJECT"
    string reason          # Human-readable explanation
    string threat_level    # "NONE", "LOW", "MODERATE", "HIGH", "CRITICAL"
    float32 confidence     # 0.0 to 1.0
    geometry_msgs/Point[] waypoints
    string[] flip_positions  # Position flags: "farthest_left", "middle_left", "middle_right", "furthest_right"
    """
    def __init__(self):
        self.status = "PENDING"
        self.reason = ""
        self.threat_level = "NONE"
        self.confidence = 0.0
        self.waypoints = []
        self.flip_counts = {}  # Dict[str, int]: pantry_id -> number of crates to flip
        self.flip_positions = []  # List[str]: position flags for which crates to flip


class ROS2HybridSupervisor:
    """
    ROS2-integrated hybrid supervisor.
    
    Subscribes to destination requests, analyzes with CV+Kalman,
    publishes decisions and optimized paths.
    """
    
    def __init__(self, config=None, team_color="blue", test_mode=False):
        """
        Initialize ROS2 hybrid supervisor.
        
        Args:
            config: Strategy configuration
            team_color: Team color ("blue" or "yellow")
            test_mode: Run without ROS2 for testing
        """
        self.config = config or DEFAULT_CONFIG
        self.team_color = team_color
        self.test_mode = test_mode
        
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
        self.waiting_for_new_destination = False
        
        # Statistics
        self.total_waypoints_received = 0
        self.total_accepted = 0
        self.total_rejected = 0
        
        # ROS2 initialization (placeholder)
        if not test_mode and ROS2_AVAILABLE:
            self._init_ros2()
        else:
            print("⚠️  Running in TEST MODE - ROS2 disabled")
            self._init_test_mode()
    
    def _init_ros2(self):
        """Initialize ROS2 node and topics."""
        # PLACEHOLDER - Replace with actual ROS2 initialization
        # 
        # rclpy.init()
        # self.node = rclpy.create_node('hybrid_supervisor')
        # 
        # # Subscriber: destination from Raspberry Pi
        # self.dest_sub = self.node.create_subscription(
        #     Point,
        #     '/navigation/destination',
        #     self.destination_callback,
        #     10
        # )
        # 
        # # Publisher: decision (ACCEPT/REJECT)
        # self.decision_pub = self.node.create_publisher(
        #     NavigationDecision,
        #     '/navigation/decision',
        #     10
        # )
        # 
        # # Publisher: optimized waypoints
        # self.waypoint_pub = self.node.create_publisher(
        #     Path,
        #     '/navigation/waypoints',
        #     10
        # )
        # 
        # print("✅ ROS2 node initialized: hybrid_supervisor")
        pass
    
    def _init_test_mode(self):
        """Initialize test mode without ROS2."""
        print("🧪 Test mode active - using console I/O instead of ROS2")
        self.test_destinations = [
            (1.5, 1.0, "collect_crate"),
            (2.2, 0.7, "flip_pantry"),
            (0.3, 0.2, "return_to_nest")
        ]
        self.test_index = 0
    
    def destination_callback(self, msg):
        """
        ROS2 callback for receiving destination from Raspberry Pi.
        
        PLACEHOLDER - Will be called by ROS2 when message arrives.
        
        Args:
            msg: geometry_msgs/Point with destination coordinates
        """
        # Extract destination from message
        # x = msg.x
        # y = msg.y
        # 
        # self.current_destination = (x, y)
        # self.waiting_for_new_destination = False
        # self.total_waypoints_received += 1
        # 
        # print(f"\n📍 Received destination: ({x:.2f}, {y:.2f})")
        # 
        # # Immediately analyze and respond
        # self.analyze_and_respond()
        pass
    
    def analyze_and_respond(self):
        """
        Core decision logic:
        1. Check if destination matches pantry/fridge zone
        2. Get enemy state from Kalman
        3. Predict enemy position 3s ahead
        4. Check if destination is threatened
        5. If safe: Compute RRT path with obstacle avoidance, publish ACCEPT + waypoints
        6. If unsafe: Publish REJECT + reason
        7. Include flip counts ONLY if destination is a pantry/fridge with crates
        """
        if not self.current_destination:
            return

        # Check if destination is a pantry/fridge zone
        matched_zone = self._match_destination_to_zone(self.current_destination)
        
        # Get enemy state with velocity
        enemy_state = self._get_enemy_state()
        
        # Get crate obstacles for path planning
        crate_obstacles = self._get_crate_obstacles()

        # Decision structure
        decision = NavigationDecision()
        
        # Conditionally compute flip counts ONLY if destination is a pantry/fridge
        if matched_zone:
            flip_decisions = self.flip_manager.analyze_all_pantries(self.world_state)
            # Only include flip count for the matched zone
            if matched_zone in flip_decisions:
                flip_count = flip_decisions[matched_zone].recommended_flips
                decision.flip_counts = {matched_zone: flip_count}
                
                # Get crates in this zone and determine positions
                if matched_zone.startswith('pantry'):
                    pantry_zone = self.config.pantry_zones[matched_zone]
                    pantry_crates = [c for c in self.world_state.crates 
                                   if pantry_zone[0] <= c.pos[0] <= pantry_zone[1] and 
                                      pantry_zone[2] <= c.pos[1] <= pantry_zone[3] and
                                      c.ownership == CrateOwnership.OPPONENT]  # Only flip enemy crates
                    decision.flip_positions = self._get_crate_positions_relative_to_robot(
                        pantry_crates[:flip_count], pantry_zone
                    )
                elif 'fridge' in matched_zone:
                    fridge_zone = self.config.fridge_blue if self.team_color == "blue" else self.config.fridge_yellow
                    fridge_crates = [c for c in self.world_state.crates 
                                   if fridge_zone[0] <= c.pos[0] <= fridge_zone[1] and 
                                      fridge_zone[2] <= c.pos[1] <= fridge_zone[3] and
                                      c.ownership == CrateOwnership.OPPONENT]
                    decision.flip_positions = self._get_crate_positions_relative_to_robot(
                        fridge_crates[:flip_count], fridge_zone
                    )
            else:
                decision.flip_counts = {}
                decision.flip_positions = []
        else:
            decision.flip_counts = {}
            decision.flip_positions = []

        if not enemy_state:
            # No enemy - safe to proceed, avoid crate obstacles
            path = self._compute_path(self.current_destination, crate_obstacles)
            if path:
                decision.status = "ACCEPT"
                decision.reason = "No enemy detected - path clear"
                decision.threat_level = "NONE"
                decision.confidence = 1.0
                decision.waypoints = path
                self.total_accepted += 1
            else:
                decision.status = "REJECT"
                decision.reason = "Path would violate forbidden zone"
                decision.threat_level = "NONE"
                decision.confidence = 0.0
                decision.waypoints = []
                self.total_rejected += 1
                self.waiting_for_new_destination = True
        else:
            # Enemy present - check threat
            predicted_pos = self._predict_enemy_position(enemy_state, lookahead_time=3.0)
            threat_distance = self._distance_to_point(self.current_destination, predicted_pos)
            threat_threshold = self.config.enemy_danger_radius
            if threat_distance < threat_threshold:
                # REJECT - enemy too close
                decision.status = "REJECT"
                decision.reason = f"Enemy predicted at ({predicted_pos[0]:.2f}, {predicted_pos[1]:.2f}), distance: {threat_distance:.2f}m"
                decision.threat_level = self._assess_threat_level(threat_distance)
                decision.confidence = enemy_state.confidence
                decision.waypoints = []
                self.total_rejected += 1
                self.waiting_for_new_destination = True
            else:
                # ACCEPT with enemy + crate obstacle avoidance
                all_obstacles = [predicted_pos] + crate_obstacles
                path = self._compute_path(self.current_destination, all_obstacles)
                if path:
                    decision.status = "ACCEPT"
                    decision.reason = f"Path clear, enemy at safe distance ({threat_distance:.2f}m)"
                    decision.threat_level = "LOW" if threat_distance < threat_threshold * 2 else "NONE"
                    decision.confidence = 0.9
                    decision.waypoints = path
                    self.total_accepted += 1
                else:
                    decision.status = "REJECT"
                    decision.reason = "No valid path - forbidden zone or obstacles block all routes"
                    decision.threat_level = "LOW"
                    decision.confidence = 0.5
                    decision.waypoints = []
                    self.total_rejected += 1
                    self.waiting_for_new_destination = True

        # Publish decision
        self._publish_decision(decision)

        # Log
        self._log_decision(decision)
    
    def _get_enemy_state(self):
        """Get enemy state from Kalman tracker."""
        enemy_id = 30  # Enemy robot marker ID
        if hasattr(self.kalman_tracker, 'trackers') and enemy_id in self.kalman_tracker.trackers:
            return self.kalman_tracker.trackers[enemy_id].get_state()
        return None
    
    def _predict_enemy_position(self, enemy_state, lookahead_time: float) -> Tuple[float, float]:
        """Predict enemy position using Kalman velocity."""
        pred_x = enemy_state.x + enemy_state.vx * lookahead_time
        pred_y = enemy_state.y + enemy_state.vy * lookahead_time
        return (pred_x, pred_y)
    
    def _distance_to_point(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points."""
        return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5
    
    def _assess_threat_level(self, distance: float) -> str:
        """Assess threat level based on distance."""
        critical = self.config.enemy_critical_radius
        danger = self.config.enemy_danger_radius
        
        if distance < critical:
            return "CRITICAL"
        elif distance < danger:
            return "HIGH"
        elif distance < danger * 1.5:
            return "MODERATE"
        elif distance < danger * 2.5:
            return "LOW"
        else:
            return "NONE"
    
    def _match_destination_to_zone(self, destination: Tuple[float, float]) -> Optional[str]:
        """Check if destination matches a pantry or fridge zone.
        
        Args:
            destination: (x, y) coordinates
            
        Returns:
            Zone ID (e.g., 'pantry1', 'fridge_blue') if matched, None otherwise
        """
        dest_x, dest_y = destination
        tolerance = self.config.destination_zone_tolerance
        
        # Check pantries
        for pantry_id, (xmin, xmax, ymin, ymax) in self.config.pantry_zones.items():
            # Expand zone by tolerance
            if (xmin - tolerance <= dest_x <= xmax + tolerance and
                ymin - tolerance <= dest_y <= ymax + tolerance):
                # Check if this pantry has crates
                pantry_crates = [c for c in self.world_state.crates 
                                if xmin <= c.pos[0] <= xmax and ymin <= c.pos[1] <= ymax]
                if pantry_crates:
                    return pantry_id
        
        # Check fridges (if needed)
        fridge_zone = self.config.fridge_blue if self.team_color == "blue" else self.config.fridge_yellow
        xmin, xmax, ymin, ymax = fridge_zone
        if (xmin - tolerance <= dest_x <= xmax + tolerance and
            ymin - tolerance <= dest_y <= ymax + tolerance):
            # Check if fridge has crates
            fridge_crates = [c for c in self.world_state.crates 
                           if xmin <= c.pos[0] <= xmax and ymin <= c.pos[1] <= ymax]
            if fridge_crates:
                return f"fridge_{self.team_color}"
        
        return None
    
    def _get_crate_obstacles(self) -> List[Tuple[float, float]]:
        """Get crate positions as obstacles for path planning.
        
        Returns:
            List of (x, y) crate positions to avoid
        """
        obstacles = []
        for crate in self.world_state.crates:
            obstacles.append((crate.pos[0], crate.pos[1]))
        return obstacles
    
    def _is_in_forbidden_zone(self, point: Tuple[float, float]) -> bool:
        """Check if a point is inside the forbidden zone.
        
        Args:
            point: (x, y) coordinates
            
        Returns:
            True if point is in forbidden zone (with buffer), False otherwise
        """
        x, y = point
        xmin, xmax, ymin, ymax = self.config.forbidden_zone
        buffer = self.config.forbidden_zone_buffer
        
        # Expand zone by buffer for safety
        return (xmin - buffer <= x <= xmax + buffer and 
                ymin - buffer <= y <= ymax + buffer)
    
    def _validate_path_avoids_forbidden_zone(self, waypoints: List[Tuple[float, float]]) -> bool:
        """Check if all waypoints avoid the forbidden zone.
        
        Args:
            waypoints: List of (x, y) path waypoints
            
        Returns:
            True if path is clear of forbidden zone, False otherwise
        """
        for wp in waypoints:
            if self._is_in_forbidden_zone(wp):
                return False
        return True
    
    def _compute_path(self, goal: Tuple[float, float], obstacles: List) -> List[Tuple[float, float]]:
        """Compute optimized path using RRT-Connect + smoothing, avoiding forbidden zone.
        
        Tries multiple strategies before giving up:
        1. RRT with smoothing (if valid)
        2. RRT without smoothing (if smoothing caused violation)
        3. RRT with higher iterations
        """
        start = (self.world_state.robot_pose.x, self.world_state.robot_pose.y)
        
        # Add forbidden zone as rectangular obstacle region
        forbidden_obstacles = self._get_forbidden_zone_obstacles()
        all_obstacles = obstacles + forbidden_obstacles
        
        # Check if start or goal is in forbidden zone
        if self._is_in_forbidden_zone(start):
            print(f"⚠️  WARNING: Start position in forbidden zone!")
            return []  # Cannot plan if start is invalid
        if self._is_in_forbidden_zone(goal):
            print(f"⚠️  WARNING: Goal position in forbidden zone!")
            return []  # Cannot plan if goal is invalid
        
        try:
            # Strategy 1: RRT-Connect with smoothing
            path = rrt_connect_plan(
                start, goal, all_obstacles,
                step_size=self.config.path_planning_step_size,
                max_iter=self.config.path_planning_max_iter
            )
            
            if path and len(path) > 2:
                # Try smoothing
                smoothed_path = smooth_path(path)
                
                # Validate smoothed path
                if self._validate_path_avoids_forbidden_zone(smoothed_path):
                    return smoothed_path
                else:
                    # Smoothing caused violation - use unsmoothed path
                    print(f"⚠️  Smoothed path violates forbidden zone, using unsmoothed RRT path")
                    if self._validate_path_avoids_forbidden_zone(path):
                        return path
                    else:
                        # Even RRT path violates (shouldn't happen) - try higher iterations
                        print(f"⚠️  RRT path violates forbidden zone, retrying with more iterations")
                        path_retry = rrt_connect_plan(
                            start, goal, all_obstacles,
                            step_size=self.config.path_planning_step_size * 0.8,  # Smaller steps
                            max_iter=self.config.path_planning_max_iter * 2  # More iterations
                        )
                        if path_retry and self._validate_path_avoids_forbidden_zone(path_retry):
                            return path_retry
                        else:
                            print(f"⚠️  Cannot find valid path avoiding forbidden zone")
                            return []
            else:
                # Short path or direct path
                direct_path = [start, goal]
                if self._validate_path_avoids_forbidden_zone(direct_path):
                    return direct_path
                else:
                    # Direct path blocked, need RRT
                    print(f"⚠️  Direct path violates forbidden zone, need obstacle avoidance")
                    return []
        except Exception as e:
            print(f"⚠️  Path planning failed: {e}")
            return []
    
    def _get_forbidden_zone_obstacles(self) -> List[Tuple[float, float]]:
        """Generate obstacle points covering the forbidden zone.
        
        Returns:
            List of (x, y) points densely covering forbidden zone
        """
        xmin, xmax, ymin, ymax = self.config.forbidden_zone
        buffer = self.config.forbidden_zone_buffer
        
        # Create a grid of obstacle points in the forbidden zone
        obstacles = []
        step = 0.1  # 10cm spacing for dense coverage
        
        x = xmin - buffer
        while x <= xmax + buffer:
            y = ymin - buffer
            while y <= ymax + buffer:
                obstacles.append((x, y))
                y += step
            x += step
        
        return obstacles
    
    def _get_crate_positions_relative_to_robot(self, crates: List, pantry_zone: Tuple[float, float, float, float]) -> List[str]:
        """Determine which crates to flip based on position relative to robot.
        
        Args:
            crates: List of CrateInfo objects in the pantry
            pantry_zone: (xmin, xmax, ymin, ymax) of the pantry
            
        Returns:
            List of position flags for crates to flip (max 4):
            ["farthest_left", "middle_left", "middle_right", "furthest_right"]
        """
        if not crates:
            return []
        
        robot_pos = (self.world_state.robot_pose.x, self.world_state.robot_pose.y)
        
        # Calculate robot's viewing angle to pantry center
        pantry_center_x = (pantry_zone[0] + pantry_zone[1]) / 2
        pantry_center_y = (pantry_zone[2] + pantry_zone[3]) / 2
        
        # Vector from robot to pantry
        dx = pantry_center_x - robot_pos[0]
        dy = pantry_center_y - robot_pos[1]
        
        # Determine perpendicular axis for "left-right" sorting
        # If approaching from bottom/top (dy dominant), sort by x
        # If approaching from left/right (dx dominant), sort by y
        if abs(dy) > abs(dx):
            # Approaching from bottom/top - sort by x coordinate
            sort_key = lambda c: c.pos[0]
            reverse = dx < 0  # Reverse if approaching from right
        else:
            # Approaching from left/right - sort by y coordinate  
            sort_key = lambda c: c.pos[1]
            reverse = dy < 0  # Reverse if approaching from top
        
        # Sort crates by position relative to robot's viewpoint
        sorted_crates = sorted(crates, key=sort_key, reverse=reverse)
        
        # Determine number of crates to flip (max 4)
        num_to_flip = min(len(sorted_crates), self.config.robot_flip_capacity)
        
        # Assign position labels based on how many we're flipping
        positions = []
        if num_to_flip == 1:
            positions = ["middle_left"]  # Single crate - just use one position
        elif num_to_flip == 2:
            positions = ["middle_left", "middle_right"]
        elif num_to_flip == 3:
            positions = ["farthest_left", "middle_left", "middle_right"]
        elif num_to_flip >= 4:
            positions = ["farthest_left", "middle_left", "middle_right", "furthest_right"]
        
        return positions[:num_to_flip]
    
    def _publish_decision(self, decision: NavigationDecision):
        """
        Publish decision to ROS2.
        
        PLACEHOLDER - Will publish to /navigation/decision topic.
        """
        # self.decision_pub.publish(decision)
        
        # In test mode, just print
        if self.test_mode:
            print(f"\n📤 Publishing decision: {decision.status}")
    
    def _log_decision(self, decision: NavigationDecision):
        """Log decision for monitoring."""
        print(f"\n{'='*60}")
        print(f"🎯 DECISION: {decision.status}")
        print(f"   Reason: {decision.reason}")
        print(f"   Threat Level: {decision.threat_level}")
        print(f"   Confidence: {decision.confidence:.2f}")
        if decision.waypoints:
            print(f"   Waypoints: {len(decision.waypoints)}")
            for i, wp in enumerate(decision.waypoints[:5]):  # Show first 5
                print(f"      {i+1}. ({wp[0]:.2f}, {wp[1]:.2f})")
        if decision.flip_counts:
            print(f"   Flip Counts:")
            for pantry, count in decision.flip_counts.items():
                print(f"      {pantry}: {count} crates")
        if decision.flip_positions:
            print(f"   Flip Positions: {', '.join(decision.flip_positions)}")
        print(f"{'='*60}")
        # Statistics
        print(f"\n📊 Stats: Total={self.total_waypoints_received}, "
              f"Accepted={self.total_accepted}, Rejected={self.total_rejected}")
    
    def update_vision(self, detections: Dict):
        """
        Update world state from vision system.
        
        Should be called at 30Hz with latest ArUco detections.
        
        Args:
            detections: {marker_id: (x, y, theta), ...}
        """
        # Update Kalman tracker
        self.kalman_tracker.update(detections, dt=1/30)
        
        # Update crate tracking
        crate_detections = [
            {
                'id': mid, 
                'pos': (x, y, theta),
                'ownership': 'ours' if mid == 36 else 'opponent',
                'container': 'free',
                'confidence': 1.0
            }
            for mid, (x, y, theta) in detections.items()
            if mid in [36, 47, 41]
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
        
        # Update enemy
        enemy_state = self._get_enemy_state()
        if enemy_state:
            self.world_state.enemy = EnemyInfo(
                id=30,
                pos=(enemy_state.x, enemy_state.y, enemy_state.theta),
                velocity=(enemy_state.vx, enemy_state.vy),
                confidence=enemy_state.confidence
            )
    
    def run(self):
        """
        Main loop.
        
        In production: ROS2 spin loop
        In test mode: Simulated loop
        """
        if not self.test_mode and ROS2_AVAILABLE:
            # ROS2 spin
            # rclpy.spin(self.node)
            pass
        else:
            # Test mode
            self._run_test_loop()
    
    def _run_test_loop(self):
        """Test mode loop with simulated destinations."""
        print("\n🧪 TEST MODE - Simulating ROS2 workflow\n")
        
        for i, (x, y, task) in enumerate(self.test_destinations):
            print(f"\n{'#'*60}")
            print(f"# Test Case {i+1}: {task}")
            print(f"{'#'*60}")
            
            # Simulate receiving destination
            self.current_destination = (x, y)
            self.total_waypoints_received += 1
            print(f"📍 Simulated destination from Raspberry Pi: ({x:.2f}, {y:.2f})")
            
            # Simulate enemy for some cases
            if i == 1:  # Second test case
                print("⚠️  Simulating enemy presence for testing...")
                # Mock enemy near destination
                self.kalman_tracker.update({30: (x + 0.2, y + 0.1, 0.0)}, dt=1/30)
            
            # Analyze and respond
            time.sleep(0.5)
            self.analyze_and_respond()
            
            time.sleep(2)
        
        print("\n✅ Test complete!")
        print(f"📊 Final Stats: {self.total_accepted} accepted, {self.total_rejected} rejected")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="ROS2 Hybrid Supervisor")
    parser.add_argument('--team', choices=['blue', 'yellow'], default='blue')
    parser.add_argument('--test', action='store_true', help='Run in test mode without ROS2')
    args = parser.parse_args()
    
    supervisor = ROS2HybridSupervisor(
        team_color=args.team,
        test_mode=args.test or not ROS2_AVAILABLE
    )
    
    supervisor.run()


if __name__ == "__main__":
    main()
