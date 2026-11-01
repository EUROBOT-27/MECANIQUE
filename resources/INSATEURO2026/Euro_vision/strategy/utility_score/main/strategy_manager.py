"""Strategy Manager - Main Decision System

Implements utility-based task selection and integrates with existing
perception, path planning, and obstacle avoidance modules.
"""

import sys
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import numpy as np
import time

# Add path_planning to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from path_planning.utils.rrt_connect import rrt_connect_plan
except ImportError:
    # Fallback for ros_ready_pipeline structure
    from ros_ready_pipeline.path_planning.rrt_connect import rrt_connect_plan

from utils.task_models import (
    Task,
    TaskType,
    ActionType,
    PlaceHazelnutInNest,
    PlaceHazelnutInPantry,
    FlipEnemyCrateInPantry,
    FlipAndPlaceInPantry,
    EmptyOpponentFridge,
    FillFridgeWithEmpty,
    ReachCursorZone,
    ReturnToNest,
)
from utils.world_state import (
    WorldState,
    CrateInfo,
    CrateOwnership,
    CrateContainer,
)
from utils.config import StrategyConfig, DEFAULT_CONFIG
from utils.crate_id_tracker import CrateIDTracker


class StrategyManager:
    """
    High-level strategy and decision-making system.
    
    Responsibilities:
    - Maintain world state
    - Generate candidate tasks
    - Compute utilities for all tasks
    - Select best task
    - Plan path to selected task
    - Return actionable output (path + action)
    """
    
    def __init__(
        self,
        team_color: str = "blue",
        config: Optional[StrategyConfig] = None
    ):
        """
        Initialize strategy manager.
        
        Args:
            team_color: "blue" or "yellow"
            config: Strategy configuration (uses DEFAULT_CONFIG if None)
        """
        self.team_color = team_color.lower()
        self.config = config if config is not None else DEFAULT_CONFIG
        
        # Crate ID tracker for handling multiple crates with same ArUco ID
        self.crate_tracker = CrateIDTracker()
        
        # World state
        self.world_state: Optional[WorldState] = None
        
        # Task management
        self.candidate_tasks: List[Task] = []
        self.best_task: Optional[Task] = None
        
        # Task commitment tracking
        self.committed_task_id: Optional[str] = None
        self.last_map_state_hash: Optional[int] = None
        self.task_commitment_time: Optional[float] = None  # When current task was committed
        self.min_commitment_duration: float = 5.0  # Minimum seconds before switching tasks (increased from 3s)
        self.utility_switch_threshold: float = 1.5  # Utility difference needed to justify switch (increased from 0.5)
        self.last_task_switch_time: Optional[float] = None  # Track last switch to prevent rapid switching
        
        # Performance tracking
        self.last_planning_time: float = 0.0
        self.planning_count: int = 0
    
    # ========================================================================
    # WORLD STATE UPDATE
    # ========================================================================
    
    def update_world_state(
        self,
        robot_pose: Tuple[float, float, float],  # (x, y, theta)
        detected_crates: List[Dict],  # From ArUco detector + classification
        enemy_positions: List[Tuple[float, float, float]] = None,  # [(x, y, theta), ...]
        static_obstacles: List[Tuple[np.ndarray, float]] = None,
        time_remaining: float = 100.0,
        tasks_completed: List[str] = None,
    ):
        """
        Update world state with latest perception data.
        
        Args:
            robot_pose: Robot position and orientation (x, y, theta)
            detected_crates: List of detected crates with format:
                [
                    {
                        'id': 36,  # ArUco marker ID
                        'pos': (x, y, z),  # World coordinates
                        'ownership': 'ours' or 'opponent',
                        'type': 'hazelnut' or 'empty',
                        'container': 'free' or 'pantry' or 'fridge' or 'nest'
                    },
                    ...
                ]
            enemy_positions: List of enemy robot positions (from LiDAR when available)
            static_obstacles: Obstacles from crate obstacle manager
            time_remaining: Seconds remaining in match
            tasks_completed: List of task IDs already completed
        """
        from utils.world_state import RobotPose, EnemyInfo
        
        # Create robot pose
        robot = RobotPose(
            x=robot_pose[0],
            y=robot_pose[1],
            theta=robot_pose[2],
            timestamp=time.time()
        )
        
        # Assign unique IDs to crates (handles multiple crates with same ArUco ID)
        detected_crates_with_ids = self.crate_tracker.assign_unique_ids(detected_crates)
        
        # Process crates
        crates = []
        for crate_dict in detected_crates_with_ids:
            ownership = CrateOwnership.OURS if crate_dict['ownership'] == 'ours' else CrateOwnership.OPPONENT
            
            # Parse container
            container_str = crate_dict.get('container', 'free')
            container_map = {
                'free': CrateContainer.FREE,
                'pantry': CrateContainer.PANTRY,
                'fridge': CrateContainer.FRIDGE,
                'nest': CrateContainer.NEST,
            }
            container = container_map.get(container_str, CrateContainer.UNKNOWN)
            
            crate = CrateInfo(
                unique_id=crate_dict['unique_id'],
                aruco_id=crate_dict['aruco_id'],
                position=(crate_dict['pos'][0], crate_dict['pos'][1]),
                ownership=ownership,
                container=container,
                confidence=crate_dict.get('confidence', 1.0),
                last_seen=time.time()
            )
            crates.append(crate)
        
        # Process enemies
        enemies = []
        if enemy_positions:
            for enemy_pos in enemy_positions:
                enemy = EnemyInfo(
                    position=(enemy_pos[0], enemy_pos[1]),
                    theta=enemy_pos[2],
                    last_seen=time.time()
                )
                enemies.append(enemy)
        
        # Determine match phase
        phase = "endgame" if time_remaining <= self.config.endgame_threshold else "main"
        
        # Create world state
        self.world_state = WorldState(
            robot_pose=robot,
            crates=crates,
            enemies=enemies,
            static_obstacles=static_obstacles if static_obstacles else [],
            dynamic_obstacles=[],  # Will be populated from enemies below
            time_remaining=time_remaining,
            match_phase=phase
        )
        
        # Add enemies as dynamic obstacles (circular obstacles with robot footprint radius)
        if enemies:
            enemy_obstacles = []
            for enemy in enemies:
                # Enemy position as obstacle (x, y, radius)
                enemy_pos = np.array([enemy.position[0], enemy.position[1], 0.0])
                enemy_radius = 0.15  # 15cm radius for enemy robot footprint
                enemy_obstacles.append((enemy_pos, enemy_radius))
            self.world_state.dynamic_obstacles = enemy_obstacles
        
    
    # ========================================================================
    # TASK GENERATION
    # ========================================================================
    
    def evaluate_tasks(self) -> List[Task]:
        """
        Generate all possible tasks and compute their utilities.
        
        Returns:
            List of Task objects with computed utilities
        """
        if self.world_state is None:
            return []
        
        self.candidate_tasks = []
        
        # Generate all task types
        self._generate_hazelnut_nest_tasks()
        self._generate_hazelnut_pantry_tasks()
        self._generate_flip_pantry_tasks()
        self._generate_flip_and_place_tasks()
        self._generate_endgame_tasks()  # Return to nest tasks
        
        # Compute utilities for all tasks (with path planning)
        start_time = time.time()
        
        for task in self.candidate_tasks:
            # Plan path to task destination
            robot_pos = np.array([
                self.world_state.robot_pose.x,
                self.world_state.robot_pose.y,
                0.0
            ])
            target_pos = np.array([task.target_position[0], task.target_position[1], 0.0])
            
            # Get all obstacles
            obstacles = self.world_state.get_all_obstacles()
            
            # For pickup tasks, plan path through crate position first
            if task.action == ActionType.PLACE and task.associated_crate is not None:
                # Path: Robot → Crate (pickup) → Pantry (place)
                crate_pos = np.array([
                    task.associated_crate.position[0],
                    task.associated_crate.position[1],
                    0.0
                ])
                
                # Adjust crate position - approach perpendicular to X-axis
                # Draw vertical line through crate center, find intersections with arm reach circle
                crate_center_x = crate_pos[0]
                crate_center_y = crate_pos[1]
                arm_reach = self.config.arm_reach_distance
                
                # Vertical line: x = crate_center_x
                # Circle: (x - cx)^2 + (y - cy)^2 = r^2
                # Two intersection points: (crate_center_x, crate_center_y ± arm_reach)
                point1 = np.array([crate_center_x, crate_center_y + arm_reach, 0.0])
                point2 = np.array([crate_center_x, crate_center_y - arm_reach, 0.0])
                
                # Pick closest point to robot
                dist1 = np.linalg.norm(robot_pos[:2] - point1[:2])
                dist2 = np.linalg.norm(robot_pos[:2] - point2[:2])
                
                if dist1 < dist2:
                    adjusted_crate_pos = point1
                    chosen_idx = 1
                else:
                    adjusted_crate_pos = point2
                    chosen_idx = 2
                
                # Store for visualization
                task.perpendicular_point1 = point1
                task.perpendicular_point2 = point2
                task.chosen_approach_point = adjusted_crate_pos
                
                # Debug output
                print(f"  [PERP-PLACE] Crate {task.associated_crate.unique_id} at ({crate_center_x:.3f}, {crate_center_y:.3f})")
                print(f"  [PERP-PLACE] P1=({point1[0]:.3f}, {point1[1]:.3f}) dist={dist1:.3f}m")
                print(f"  [PERP-PLACE] P2=({point2[0]:.3f}, {point2[1]:.3f}) dist={dist2:.3f}m")
                print(f"  [PERP-PLACE] Chosen: P{chosen_idx} at ({adjusted_crate_pos[0]:.3f}, {adjusted_crate_pos[1]:.3f})")
                
                # Adjust target position based on task type
                # For pantries: stop on circle around pantry center, closest to crate
                # For nests: go directly to center (no offset needed)
                if task.task_type == TaskType.PLACE_HAZELNUT_IN_PANTRY:
                    # Direction from pantry center toward adjusted crate position
                    pantry_to_crate = adjusted_crate_pos[:2] - target_pos[:2]
                    distance = np.linalg.norm(pantry_to_crate)
                    
                    if distance > 0.001:
                        # Unit vector from pantry toward crate
                        direction = pantry_to_crate / distance
                        # Place on circle around pantry, in direction of crate
                        adjusted_target_pos = target_pos.copy()
                        adjusted_target_pos[:2] = target_pos[:2] + direction * self.config.pantry_placement_distance
                    else:
                        adjusted_target_pos = target_pos
                else:
                    # For nests: use target directly (no circular offset)
                    adjusted_target_pos = target_pos
                
                # Plan path from robot to crate (adjusted)
                path_to_crate = rrt_connect_plan(
                    robot_pos,
                    adjusted_crate_pos,
                    obstacles,
                    self.config.field_bounds,
                    max_iter=self.config.path_planning_max_iter,
                    step_size=self.config.path_planning_step_size
                )
                
                # Plan path from crate to target (adjusted)
                path_to_target = rrt_connect_plan(
                    adjusted_crate_pos,
                    adjusted_target_pos,
                    obstacles,
                    self.config.field_bounds,
                    max_iter=self.config.path_planning_max_iter,
                    step_size=self.config.path_planning_step_size
                )
                
                # Combine paths (avoid duplicating crate position)
                if path_to_crate and path_to_target:
                    path = path_to_crate + path_to_target[1:]  # Skip first point of second path
                else:
                    path = None
            else:
                # Direct path for other tasks (flip in place, etc.)
                # For flip tasks, also use perpendicular approach
                if task.action == ActionType.FLIP and task.associated_crate is not None:
                    crate_pos = np.array([
                        task.associated_crate.position[0],
                        task.associated_crate.position[1],
                        0.0
                    ])
                    
                    # Perpendicular approach (vertical line intersection)
                    crate_center_x = crate_pos[0]
                    crate_center_y = crate_pos[1]
                    arm_reach = self.config.arm_reach_distance
                    
                    point1 = np.array([crate_center_x, crate_center_y + arm_reach, 0.0])
                    point2 = np.array([crate_center_x, crate_center_y - arm_reach, 0.0])
                    
                    dist1 = np.linalg.norm(robot_pos[:2] - point1[:2])
                    dist2 = np.linalg.norm(robot_pos[:2] - point2[:2])
                    
                    if dist1 < dist2:
                        adjusted_target = point1
                        chosen_idx = 1
                    else:
                        adjusted_target = point2
                        chosen_idx = 2
                    
                    # Store for visualization
                    task.perpendicular_point1 = point1
                    task.perpendicular_point2 = point2
                    task.chosen_approach_point = adjusted_target
                    
                    # Debug output
                    print(f"  [PERP-FLIP] Crate at ({crate_center_x:.3f}, {crate_center_y:.3f})")
                    print(f"  [PERP-FLIP] P1=({point1[0]:.3f}, {point1[1]:.3f}) dist={dist1:.3f}m")
                    print(f"  [PERP-FLIP] P2=({point2[0]:.3f}, {point2[1]:.3f}) dist={dist2:.3f}m")
                    print(f"  [PERP-FLIP] Chosen: P{chosen_idx} at ({adjusted_target[0]:.3f}, {adjusted_target[1]:.3f})")
                    
                    target_pos = adjusted_target
                
                path = rrt_connect_plan(
                    robot_pos,
                    target_pos,
                    obstacles,
                    self.config.field_bounds,
                    max_iter=self.config.path_planning_max_iter,
                    step_size=self.config.path_planning_step_size
                )
            
            # Compute utility with path
            task.compute_utility(self.world_state, self.config, path)
            
            # Debug output for pantry tasks to see which is chosen
            if task.task_type == TaskType.PLACE_HAZELNUT_IN_PANTRY and task.path:
                path_len = sum(np.linalg.norm(task.path[i+1][:2] - task.path[i][:2]) 
                              for i in range(len(task.path)-1))
                print(f"  [PANTRY-EVAL] {task.pantry_name}: crate {task.associated_crate.unique_id} "
                      f"path={path_len:.3f}m utility={task.utility:.3f}")
        
        self.last_planning_time = time.time() - start_time
        self.planning_count += 1
        
        # Sort by utility (descending)
        self.candidate_tasks.sort(key=lambda t: t.utility, reverse=True)
        
        return self.candidate_tasks
    
    def _generate_hazelnut_nest_tasks(self):
        """Generate tasks for placing our crates in nest."""
        free_crates = self.world_state.get_free_crates(CrateOwnership.OURS)
        
        # Determine nest position based on team
        if self.team_color == "blue":
            nest_bounds = self.config.nest_blue
        else:
            nest_bounds = self.config.nest_yellow
        
        # Use nest center as target
        nest_center = (
            (nest_bounds[0] + nest_bounds[1]) / 2.0,
            (nest_bounds[2] + nest_bounds[3]) / 2.0
        )
        
        for crate in free_crates:
            task = PlaceHazelnutInNest(
                task_id=f"nest_hazelnut_{crate.unique_id}",
                task_type=TaskType.PLACE_HAZELNUT_IN_NEST,
                target_position=nest_center,
                action=ActionType.PLACE,
                associated_crate=crate
            )
            self.candidate_tasks.append(task)
    
    def _generate_hazelnut_pantry_tasks(self):
        """Generate tasks for placing our crates in pantries.
        
        Strategy: Fill pantries up to 4 crates max (any color).
        Pantry is available if < 4 total crates.
        """
        free_crates = self.world_state.get_free_crates(CrateOwnership.OURS)
        
        # Count TOTAL crates (ours + enemy) in each pantry
        pantry_total_counts = {p_name: 0 for p_name in self.config.pantry_zones.keys()}
        
        for crate in self.world_state.crates:
            if crate.container == CrateContainer.PANTRY:
                # Find which pantry this crate is in
                crate_x, crate_y = crate.position
                for p_name, p_bounds in self.config.pantry_zones.items():
                    # Inflate pantry boundaries by tolerance for detection
                    tol = self.config.pantry_detection_tolerance
                    if ((p_bounds[0] - tol) <= crate_x <= (p_bounds[1] + tol) and
                        (p_bounds[2] - tol) <= crate_y <= (p_bounds[3] + tol)):
                        pantry_total_counts[p_name] += 1
                        break
        
        for crate in free_crates:
            # Generate task for each pantry that has space (< 4 total crates)
            for pantry_name, pantry_bounds in self.config.pantry_zones.items():
                # Skip FULL pantries (4 crates total)
                if pantry_total_counts[pantry_name] >= self.config.pantry_capacity:
                    continue
                
                pantry_center = (
                    (pantry_bounds[0] + pantry_bounds[1]) / 2.0,
                    (pantry_bounds[2] + pantry_bounds[3]) / 2.0
                )
                
                task = PlaceHazelnutInPantry(
                    task_id=f"pantry_{pantry_name}_hazelnut_{crate.unique_id}",
                    task_type=TaskType.PLACE_HAZELNUT_IN_PANTRY,
                    target_position=pantry_center,
                    action=ActionType.PLACE,
                    associated_crate=crate,
                    pantry_name=pantry_name
                )
                self.candidate_tasks.append(task)
    
    def _generate_flip_pantry_tasks(self):
        """Generate tasks for flipping enemy crates in pantries (6pt swing)."""
        # Get all crates in pantries that belong to opponent
        all_crates = self.world_state.crates
        
        for crate in all_crates:
            # Only flip enemy crates that are in pantries
            if (crate.ownership == CrateOwnership.OPPONENT and 
                crate.container == CrateContainer.PANTRY):
                
                # Determine which pantry it's in
                crate_x, crate_y = crate.position
                pantry_name = None
                
                for p_name, p_bounds in self.config.pantry_zones.items():
                    # Inflate pantry boundaries by tolerance for detection
                    tol = self.config.pantry_detection_tolerance
                    if ((p_bounds[0] - tol) <= crate_x <= (p_bounds[1] + tol) and
                        (p_bounds[2] - tol) <= crate_y <= (p_bounds[3] + tol)):
                        pantry_name = p_name
                        break
                
                if pantry_name:
                    # Create flip task - target is the crate position
                    task = FlipEnemyCrateInPantry(
                        task_id=f"flip_pantry_{pantry_name}_enemy_{crate.unique_id}",
                        task_type=TaskType.FLIP_ENEMY_CRATE_IN_PANTRY,
                        target_position=(crate_x, crate_y),
                        action=ActionType.FLIP,
                        associated_crate=crate,
                        pantry_name=pantry_name
                    )
                    self.candidate_tasks.append(task)
    
    def _generate_flip_and_place_tasks(self):
        """Generate tasks for flipping free enemy crates and placing them in pantries.
        
        Strategy: Flip free enemy crates and place in pantries with space.
        This gives us 3pts (enemy loses nothing since crate was free).
        """
        # Get all free enemy crates
        enemy_free_crates = self.world_state.get_free_crates(CrateOwnership.OPPONENT)
        
        if not enemy_free_crates:
            return
        
        # Count TOTAL crates in each pantry
        pantry_total_counts = {p_name: 0 for p_name in self.config.pantry_zones.keys()}
        
        for crate in self.world_state.crates:
            if crate.container == CrateContainer.PANTRY:
                # Find which pantry this crate is in
                crate_x, crate_y = crate.position
                for p_name, p_bounds in self.config.pantry_zones.items():
                    # Inflate pantry boundaries by tolerance for detection
                    tol = self.config.pantry_detection_tolerance
                    if ((p_bounds[0] - tol) <= crate_x <= (p_bounds[1] + tol) and
                        (p_bounds[2] - tol) <= crate_y <= (p_bounds[3] + tol)):
                        pantry_total_counts[p_name] += 1
                        break
        
        # For each free enemy crate, find closest pantry with space
        for crate in enemy_free_crates:
            crate_pos = np.array(crate.position)
            
            # Find closest pantry with space (< 4 total crates)
            closest_pantry = None
            min_distance = float('inf')
            
            for pantry_name, pantry_bounds in self.config.pantry_zones.items():
                # Skip FULL pantries (4 crates total)
                if pantry_total_counts[pantry_name] >= self.config.pantry_capacity:
                    continue
                
                pantry_center = np.array([
                    (pantry_bounds[0] + pantry_bounds[1]) / 2.0,
                    (pantry_bounds[2] + pantry_bounds[3]) / 2.0
                ])
                
                distance = np.linalg.norm(crate_pos - pantry_center)
                if distance < min_distance:
                    min_distance = distance
                    closest_pantry = (pantry_name, pantry_center)
            
            if closest_pantry:
                pantry_name, pantry_center = closest_pantry
                task = FlipAndPlaceInPantry(
                    task_id=f"flip_place_{pantry_name}_enemy_{crate.unique_id}",
                    task_type=TaskType.FLIP_AND_PLACE_IN_PANTRY,
                    target_position=tuple(pantry_center),
                    action=ActionType.PLACE,  # Flip happens during pickup
                    associated_crate=crate,
                    pantry_name=pantry_name
                )
                self.candidate_tasks.append(task)
    
    def _generate_empty_fridge_tasks(self):
        """Generate task for emptying opponent fridge."""
        opponent_fridge_crates = self.world_state.get_opponent_fridge_hazelnut_crates()
        
        if len(opponent_fridge_crates) == 0:
            return
        
        # Determine opponent fridge position
        if self.team_color == "blue":
            fridge_bounds = self.config.fridge_yellow
        else:
            fridge_bounds = self.config.fridge_blue
        
        fridge_center = (
            (fridge_bounds[0] + fridge_bounds[1]) / 2.0,
            (fridge_bounds[2] + fridge_bounds[3]) / 2.0
        )
        
        task = EmptyOpponentFridge(
            task_id="empty_opponent_fridge",
            task_type=TaskType.EMPTY_OPPONENT_FRIDGE,
            target_position=fridge_center,
            action=ActionType.FLIP
        )
        self.candidate_tasks.append(task)
    
    def _generate_fill_fridge_tasks(self):
        """Generate tasks for filling our fridge with crates."""
        # Get any free crates (ours or opponent's)
        our_free_crates = self.world_state.get_free_crates(CrateOwnership.OURS)
        opponent_free_crates = self.world_state.get_free_crates(CrateOwnership.OPPONENT)
        free_crates = our_free_crates + opponent_free_crates
        
        # Determine our fridge position
        if self.team_color == "blue":
            fridge_bounds = self.config.fridge_blue
        else:
            fridge_bounds = self.config.fridge_yellow
        
        fridge_center = (
            (fridge_bounds[0] + fridge_bounds[1]) / 2.0,
            (fridge_bounds[2] + fridge_bounds[3]) / 2.0
        )
        
        for crate in free_crates:
            task = FillFridgeWithEmpty(
                task_id=f"fill_fridge_empty_{crate.unique_id}",
                task_type=TaskType.FILL_FRIDGE_WITH_EMPTY,
                target_position=fridge_center,
                action=ActionType.PLACE,
                associated_crate=crate
            )
            self.candidate_tasks.append(task)
    
    def _generate_cursor_zone_tasks(self):
        """Generate task for reaching cursor zone."""
        # Check if already completed
        if "cursor_zone" in self.world_state.tasks_completed:
            return
        
        cursor_bounds = self.config.cursor_zone
        cursor_center = (
            (cursor_bounds[0] + cursor_bounds[1]) / 2.0,
            (cursor_bounds[2] + cursor_bounds[3]) / 2.0
        )
        
        task = ReachCursorZone(
            task_id="cursor_zone",
            task_type=TaskType.REACH_CURSOR_ZONE,
            target_position=cursor_center,
            action=ActionType.NONE
        )
        self.candidate_tasks.append(task)
    
    def _generate_endgame_tasks(self):
        """Generate endgame positioning tasks."""
        # Determine our nest zone (not endgame zone)
        if self.team_color == "blue":
            nest_bounds = self.config.nest_blue
        else:
            nest_bounds = self.config.nest_yellow
        
        # Center of nest (partial) - fully inside
        center = (
            (nest_bounds[0] + nest_bounds[1]) / 2.0,
            (nest_bounds[2] + nest_bounds[3]) / 2.0
        )
        
        # Deep inside nest (full) - 30% from edge
        deep_inside = (
            nest_bounds[0] + (nest_bounds[1] - nest_bounds[0]) * 0.3,
            center[1]
        )
        
        # Partial endgame task
        task_partial = ReturnToNest(
            task_id="endgame_partial",
            task_type=TaskType.RETURN_TO_NEST,
            target_position=center,
            action=ActionType.NONE,
            fully_inside=False
        )
        self.candidate_tasks.append(task_partial)
        
        # Full endgame task
        task_full = ReturnToNest(
            task_id="endgame_full",
            task_type=TaskType.RETURN_TO_NEST,
            target_position=deep_inside,
            action=ActionType.NONE,
            fully_inside=True
        )
        self.candidate_tasks.append(task_full)
    
    # ========================================================================
    # MAP STATE TRACKING
    # ========================================================================
    
    def _compute_map_state_hash(self) -> int:
        """Compute hash of current map state to detect changes."""
        if self.world_state is None:
            return 0
        
        # Track: enemy positions, crate positions and ownership
        state_components = []
        
        # Enemy positions (rounded to 20cm to avoid noise)
        for enemy in self.world_state.enemies:
            state_components.append((round(enemy.position[0] * 5) / 5, round(enemy.position[1] * 5) / 5))
        
        # Crate states (position + ownership + container)
        for crate in self.world_state.crates:
            state_components.append((
                crate.unique_id,
                round(crate.position[0] * 5) / 5,
                round(crate.position[1] * 5) / 5,
                crate.ownership.value,
                crate.container.value
            ))
        
        return hash(tuple(sorted(state_components, key=str)))
    
    def _has_map_state_changed(self) -> bool:
        """Check if map state has changed since last check."""
        current_hash = self._compute_map_state_hash()
        
        if self.last_map_state_hash is None:
            self.last_map_state_hash = current_hash
            return False
        
        changed = current_hash != self.last_map_state_hash
        if changed:
            self.last_map_state_hash = current_hash
        
        return changed
    
    # ========================================================================
    # TASK SELECTION
    # ========================================================================
    
    def select_best_task(self) -> Optional[Task]:
        """Select the task with highest utility.
        
        Implements STRICT commitment logic to prevent task thrashing:
        - Minimum 5s commitment period (hard lock)
        - Large utility threshold (1.5) required to switch
        - Cooldown period between switches
        - Ignore ALL map changes during commitment
        
        Returns:
            Best task or None if no feasible tasks
        """
        if not self.candidate_tasks:
            return None
        
        # Filter to feasible tasks (utility > 0)
        feasible_tasks = [t for t in self.candidate_tasks if t.utility > 0]
        
        if not feasible_tasks:
            return None
        
        current_time = time.time()
        
        # STRICT COMMITMENT LOGIC
        if self.committed_task_id is not None:
            # Try to find current committed task in feasible tasks
            committed_task = next(
                (t for t in feasible_tasks if t.task_id == self.committed_task_id),
                None
            )
            
            if committed_task is not None:
                # Calculate time since commitment
                time_committed = 0.0
                if self.task_commitment_time is not None:
                    time_committed = current_time - self.task_commitment_time
                
                # HARD LOCK: Always stay committed during minimum duration
                if time_committed < self.min_commitment_duration:
                    self.best_task = committed_task
                    print(f"\nTask: {self.best_task.description} [LOCKED {time_committed:.1f}s/{self.min_commitment_duration:.0f}s]")
                    if self.best_task.path:
                        waypoints_str = " -> ".join([f"({wp[0]:.2f}, {wp[1]:.2f})" for wp in self.best_task.path])
                        print(f"Waypoints: {waypoints_str}")
                    return self.best_task
                
                # After minimum time, check if switch is worth it
                best_alternative = feasible_tasks[0]  # Sorted by utility
                utility_gain = best_alternative.utility - committed_task.utility
                
                # Only switch if MAJOR improvement AND not recently switched
                time_since_last_switch = float('inf')
                if self.last_task_switch_time is not None:
                    time_since_last_switch = current_time - self.last_task_switch_time
                
                # Stay committed unless huge utility gain
                if utility_gain < self.utility_switch_threshold or time_since_last_switch < 2.0:
                    self.best_task = committed_task
                    print(f"\nTask: {self.best_task.description} [COMMITTED {time_committed:.1f}s]")
                    if self.best_task.path:
                        waypoints_str = " -> ".join([f"({wp[0]:.2f}, {wp[1]:.2f})" for wp in self.best_task.path])
                        print(f"Waypoints: {waypoints_str}")
                    return self.best_task
        
        # SWITCH TO NEW TASK (only if major improvement or no current commitment)
        # Use highest utility task
        self.best_task = feasible_tasks[0]
        
        # Update commitment tracking
        self.committed_task_id = self.best_task.task_id
        self.task_commitment_time = current_time
        self.last_task_switch_time = current_time
        
        print(f"\nTask: {self.best_task.description} [NEW COMMITMENT]")
        if self.best_task.path:
            waypoints_str = " -> ".join([f"({wp[0]:.2f}, {wp[1]:.2f})" for wp in self.best_task.path])
            print(f"Waypoints: {waypoints_str}")
        
        return self.best_task
    
    def get_best_task_output(self) -> Optional[Dict]:
        """
        Get actionable output for the best task.
        
        Returns:
            Dictionary with:
            {
                'task_id': str,
                'task_type': str,
                'action': str,  # 'pickup', 'place', 'flip', 'none'
                'path': List[np.ndarray],  # Waypoints to follow
                'target': (x, y),
                'description': str,
                'utility': float
            }
            
            Returns None if no task selected or no path available.
        """
        if self.best_task is None:
            return None
        
        if self.best_task.path is None or len(self.best_task.path) == 0:
            return None
        
        return {
            'task_id': self.best_task.task_id,
            'task_type': self.best_task.task_type.value,
            'action': self.best_task.action.value,
            'path': self.best_task.path,
            'target': self.best_task.target_position,
            'description': self.best_task.description,
            'utility': self.best_task.utility,
            'expected_score': self.best_task.expected_score,
            'time_cost': self.best_task.time_cost,
        }
    
    # ========================================================================
    # DEBUGGING AND MONITORING
    # ========================================================================
    
    def print_task_rankings(self, top_n: int = 5):
        """Print top N tasks by utility."""
        pass  # Disabled for clean logs
    
    def get_statistics(self) -> Dict:
        """Get performance statistics."""
        return {
            'num_candidate_tasks': len(self.candidate_tasks),
            'num_feasible_tasks': len([t for t in self.candidate_tasks if t.utility > 0]),
            'last_planning_time': self.last_planning_time,
            'planning_count': self.planning_count,
            'world_state': self.world_state.to_dict() if self.world_state else None,
        }


# ============================================================================
# EXTENSIBILITY NOTES
# ============================================================================

"""
ADDING NEW TASKS:
1. Define new TaskType in task_models.py
2. Create new Task subclass with compute_expected_score() and is_feasible()
3. Add generation method in StrategyManager (e.g., _generate_new_task_type)
4. Call generation method in evaluate_tasks()

ADDING NEW SCORING RULES:
1. Add score constants to StrategyConfig
2. Update relevant Task.compute_expected_score() methods
3. Adjust utility weights if needed

TUNING UTILITY WEIGHTS:
1. Modify StrategyConfig defaults
2. Or use config.set_aggressive_mode() / set_defensive_mode()
3. Or create custom StrategyConfig instance with desired weights

INTEGRATING NEW SENSORS:
1. Add new fields to WorldState (e.g., lidar_scan)
2. Update update_world_state() to accept new data
3. Update safety/feasibility checks in tasks to use new data

EXAMPLE USAGE:
    from strategy import StrategyManager, StrategyConfig
    
    # Initialize
    config = StrategyConfig()
    config.set_defensive_mode()  # Tune for safety
    manager = StrategyManager(team_color="blue", config=config)
    
    # Update world state
    manager.update_world_state(
        robot_pose=(1.5, 1.0, 0.0),
        detected_crates=[...],
        enemy_positions=[...],
        time_remaining=85.0
    )
    
    # Evaluate and select
    tasks = manager.evaluate_tasks()
    best_task = manager.select_best_task()
    
    # Get output
    output = manager.get_best_task_output()
    if output:
        path = output['path']
        action = output['action']
        # Execute path and action...
"""
