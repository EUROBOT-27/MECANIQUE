"""Capacity-Aware Strategy Manager

Extends the base StrategyManager with capacity planning:
- Robot can carry up to 6 crates
- Robot can flip up to 4 crates in one trip
- Intelligent task batching based on distance clustering
- Multi-task route optimization

Author: Strategy Team
Date: 2026-01-22
"""

import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from strategy_manager import StrategyManager
from utils.task_models import Task, TaskType, ActionType
from utils.world_state import CrateInfo, CrateOwnership, CrateContainer
from utils.config import StrategyConfig, DEFAULT_CONFIG


class CapacityAwareStrategyManager(StrategyManager):
    """
    Enhanced strategy manager with capacity planning.
    
    Features:
    - Batches tasks based on robot capacity (6 crates max, 4 flips max)
    - Clusters nearby tasks for efficient multi-pickup routes
    - Avoids committing to distant tasks when closer alternatives exist
    - Optimizes full-capacity trips over partial trips
    """
    
    def __init__(self, team_color: str = "blue", config: Optional[StrategyConfig] = None):
        """Initialize capacity-aware strategy manager."""
        super().__init__(team_color, config)
        
        # Capacity tracking
        self.current_load: int = 0  # Number of crates currently carried
        self.current_task_batch: List[Task] = []  # Tasks planned for current trip
        self.batch_commitment_time: Optional[float] = None
        
    def _cluster_tasks_by_distance(self, tasks: List[Task], max_distance: float) -> List[List[Task]]:
        """
        Cluster tasks by proximity for batch planning.
        
        Args:
            tasks: List of candidate tasks
            max_distance: Maximum distance between tasks in same cluster
            
        Returns:
            List of task clusters (each cluster is a list of nearby tasks)
        """
        if not tasks:
            return []
        
        clusters = []
        remaining = tasks.copy()
        
        while remaining:
            # Start new cluster with first remaining task
            cluster = [remaining.pop(0)]
            cluster_center = cluster[0].target_position
            
            # Find all tasks within max_distance of cluster center
            i = 0
            while i < len(remaining):
                task = remaining[i]
                dist = np.linalg.norm(
                    np.array(task.target_position) - np.array(cluster_center)
                )
                
                if dist <= max_distance:
                    cluster.append(remaining.pop(i))
                else:
                    i += 1
            
            clusters.append(cluster)
        
        return clusters
    
    def _evaluate_batch_utility(self, task_cluster: List[Task]) -> float:
        """
        Calculate combined utility for a batch of tasks.
        
        Considers:
        - Total expected score
        - Average distance (prefer tight clusters)
        - Capacity efficiency (prefer full loads)
        - Task compatibility (flip vs place)
        
        Args:
            task_cluster: List of tasks to evaluate as a batch
            
        Returns:
            Batch utility score
        """
        if not task_cluster:
            return 0.0
        
        # Count different task types
        pickup_tasks = []
        flip_tasks = []
        place_tasks = []
        
        for task in task_cluster:
            if task.task_type in [TaskType.PLACE_HAZELNUT_IN_NEST, TaskType.PLACE_HAZELNUT_IN_PANTRY]:
                place_tasks.append(task)
            elif task.task_type in [TaskType.FLIP_ENEMY_CRATE_IN_PANTRY, TaskType.FLIP_AND_PLACE_IN_PANTRY]:
                flip_tasks.append(task)
            else:
                pickup_tasks.append(task)
        
        # Check capacity constraints
        num_pickups = len(pickup_tasks)
        num_flips = len(flip_tasks)
        
        if num_pickups > self.config.robot_max_capacity:
            return 0.0  # Infeasible - too many crates
        
        if num_flips > self.config.robot_flip_capacity:
            return 0.0  # Infeasible - can't flip that many
        
        # Calculate total score
        total_score = sum(task.expected_score for task in task_cluster)
        
        # Calculate average distance (from robot to cluster centroid)
        if self.world_state and self.world_state.robot_pose:
            robot_pos = (self.world_state.robot_pose.x, self.world_state.robot_pose.y)
            cluster_positions = [task.target_position for task in task_cluster]
            centroid = np.mean(cluster_positions, axis=0)
            avg_distance = np.linalg.norm(np.array(centroid) - np.array(robot_pos))
        else:
            avg_distance = np.mean([task.distance_cost for task in task_cluster])
        
        # Calculate capacity efficiency (prefer fuller loads)
        capacity_used = num_pickups + num_flips
        capacity_efficiency = capacity_used / self.config.robot_max_capacity
        
        # Batch utility formula
        # Higher score for: more points, closer distance, fuller capacity
        utility = (
            total_score * self.config.weight_expected_score * (1.0 + 0.5 * capacity_efficiency)
            - avg_distance * self.config.weight_distance_cost
            - (self.config.robot_max_capacity - capacity_used) * 0.1  # Penalty for unused capacity
        )
        
        return max(0.0, utility)
    
    def select_best_task_batch(self) -> List[Task]:
        """
        Select optimal batch of tasks considering capacity constraints.
        
        Strategy:
        1. Cluster feasible tasks by proximity
        2. Evaluate each cluster's batch utility
        3. Select cluster with highest utility
        4. Commit to executing all tasks in that cluster
        
        Returns:
            List of tasks to execute (in order of distance from robot)
        """
        if not self.candidate_tasks:
            return []
        
        # Filter feasible tasks - exclude non-collecting/navigation-only tasks
        excluded_types = {
            TaskType.RETURN_TO_NEST,
            TaskType.REACH_CURSOR_ZONE,
            TaskType.EMPTY_OPPONENT_FRIDGE,
            TaskType.FILL_FRIDGE_WITH_EMPTY,
        }
        feasible_tasks = [
            t for t in self.candidate_tasks
            if t.utility > 0 and t.task_type not in excluded_types
        ]
        
        if not feasible_tasks:
            return []
        
        # Cluster tasks by distance
        clustering_distance = self.config.capacity_clustering_distance
        task_clusters = self._cluster_tasks_by_distance(feasible_tasks, clustering_distance)
        
        # Evaluate each cluster
        cluster_utilities = [
            (cluster, self._evaluate_batch_utility(cluster))
            for cluster in task_clusters
        ]
        
        # Sort by batch utility
        cluster_utilities.sort(key=lambda x: x[1], reverse=True)
        
        if not cluster_utilities or cluster_utilities[0][1] <= 0:
            return []
        
        # Select best cluster
        best_cluster = cluster_utilities[0][0]
        
        # Sort tasks in cluster by distance from robot (nearest first)
        if self.world_state and self.world_state.robot_pose:
            robot_pos = (self.world_state.robot_pose.x, self.world_state.robot_pose.y)
            best_cluster.sort(key=lambda task: np.linalg.norm(
                np.array(task.target_position) - np.array(robot_pos)
            ))
        
        # Limit by capacity
        pickup_count = 0
        flip_count = 0
        final_batch = []
        
        for task in best_cluster:
            is_flip = task.task_type in [TaskType.FLIP_ENEMY_CRATE_IN_PANTRY, TaskType.FLIP_AND_PLACE_IN_PANTRY]
            is_pickup = task.task_type in [TaskType.PLACE_HAZELNUT_IN_NEST, TaskType.PLACE_HAZELNUT_IN_PANTRY]
            
            # Check capacity
            if is_flip and flip_count >= self.config.robot_flip_capacity:
                continue
            if is_pickup and pickup_count >= self.config.robot_max_capacity:
                continue
            
            final_batch.append(task)
            if is_flip:
                flip_count += 1
            if is_pickup:
                pickup_count += 1
        
        return final_batch
    
    def select_best_task(self) -> Optional[Task]:
        """
        Override to use capacity-aware batch planning.
        
        Returns first task from optimal batch, stores rest for commitment.
        Falls back to navigation tasks if no batch tasks available.
        Implements STRICT commitment to prevent task thrashing.
        """
        current_time = time.time()
        
        # ABSOLUTE COMMITMENT TO RETURN-TO-NEST - never switch away
        if self.committed_task_id is not None:
            committed_task = next(
                (t for t in self.candidate_tasks if t.task_id == self.committed_task_id and t.utility > 0),
                None
            )
            if committed_task is not None and committed_task.task_type == TaskType.RETURN_TO_NEST:
                self.best_task = committed_task
                print(f"\n[NEST COMMITTED] {self.best_task.description}")
                if self.best_task.path:
                    waypoints_str = " -> ".join([f"({wp[0]:.2f}, {wp[1]:.2f})" for wp in self.best_task.path])
                    print(f"Waypoints: {waypoints_str}")
                return self.best_task
        
        # STRICT COMMITMENT CHECK - if we're locked to a task, stay with it
        if self.committed_task_id is not None and self.task_commitment_time is not None:
            time_committed = current_time - self.task_commitment_time
            
            # HARD LOCK during minimum commitment duration
            if time_committed < self.min_commitment_duration:
                # Find current committed task
                committed_task = next(
                    (t for t in self.candidate_tasks if t.task_id == self.committed_task_id and t.utility > 0),
                    None
                )
                if committed_task is not None:
                    self.best_task = committed_task
                    print(f"\n[LOCKED {time_committed:.1f}s/{self.min_commitment_duration:.0f}s] {self.best_task.description}")
                    if self.best_task.path:
                        waypoints_str = " -> ".join([f"({wp[0]:.2f}, {wp[1]:.2f})" for wp in self.best_task.path])
                        print(f"Waypoints: {waypoints_str}")
                    return self.best_task
        
        # Get optimal batch
        task_batch = self.select_best_task_batch()
        
        if not task_batch:
            # No batch tasks - fall back to navigation/return tasks
            navigation_tasks = [
                t for t in self.candidate_tasks
                if t.utility > 0 and t.task_type in {TaskType.RETURN_TO_NEST, TaskType.REACH_CURSOR_ZONE}
            ]
            if navigation_tasks:
                # Pick highest utility navigation task
                navigation_tasks.sort(key=lambda t: t.utility, reverse=True)
                
                # Check if we should commit to this new task
                if self.committed_task_id != navigation_tasks[0].task_id:
                    # New task - update commitment
                    self.best_task = navigation_tasks[0]
                    self.committed_task_id = self.best_task.task_id
                    self.task_commitment_time = current_time
                    self.last_task_switch_time = current_time
                    self.current_task_batch = [self.best_task]
                    
                    print(f"\n[NEW] Navigation Task: {self.best_task.description}")
                else:
                    # Continue with same task
                    self.best_task = navigation_tasks[0]
                    print(f"\n[CONTINUE] Navigation Task: {self.best_task.description}")
                
                if self.best_task.path:
                    waypoints_str = " -> ".join([f"({wp[0]:.2f}, {wp[1]:.2f})" for wp in self.best_task.path])
                    print(f"Waypoints: {waypoints_str}")
                
                return self.best_task
            return None
        
        # Check if first task in batch is the same as committed task
        if self.committed_task_id == task_batch[0].task_id:
            # Continue with current batch
            self.current_task_batch = task_batch
            self.best_task = task_batch[0]
            
            print(f"\n[CONTINUE] Capacity Plan: {len(task_batch)} tasks")
            print(f"Task: {self.best_task.description}")
        else:
            # New batch - check if we should switch
            time_since_last_switch = float('inf')
            if self.last_task_switch_time is not None:
                time_since_last_switch = current_time - self.last_task_switch_time
            
            # Only switch if enough time has passed
            if time_since_last_switch < 2.0:
                # Too soon to switch - find and return current committed task if still valid
                committed_task = next(
                    (t for t in self.candidate_tasks if t.task_id == self.committed_task_id and t.utility > 0),
                    None
                )
                if committed_task is not None:
                    self.best_task = committed_task
                    print(f"\n[COOLDOWN] {self.best_task.description}")
                    if self.best_task.path:
                        waypoints_str = " -> ".join([f"({wp[0]:.2f}, {wp[1]:.2f})" for wp in self.best_task.path])
                        print(f"Waypoints: {waypoints_str}")
                    return self.best_task
            
            # Switch to new batch
            self.current_task_batch = task_batch
            self.best_task = task_batch[0]
            self.committed_task_id = self.best_task.task_id
            self.task_commitment_time = current_time
            self.last_task_switch_time = current_time
            
            print(f"\n[NEW] Capacity Plan: {len(task_batch)} tasks")
            print(f"Task: {self.best_task.description}")
        
        if self.best_task.path:
            waypoints_str = " -> ".join([f"({wp[0]:.2f}, {wp[1]:.2f})" for wp in self.best_task.path])
            print(f"Waypoints: {waypoints_str}")
        
        # Show remaining tasks in batch
        if len(task_batch) > 1:
            print(f"Next in batch: {', '.join([t.description[:30] + '...' for t in task_batch[1:3]])}")
        
        return self.best_task
    
    def get_capacity_status(self) -> Dict:
        """
        Get current capacity usage and batch plan.
        
        Returns:
            Dictionary with capacity info
        """
        pickup_count = sum(1 for t in self.current_task_batch 
                          if t.task_type in [TaskType.PLACE_HAZELNUT_IN_NEST, TaskType.PLACE_HAZELNUT_IN_PANTRY])
        flip_count = sum(1 for t in self.current_task_batch
                        if t.task_type in [TaskType.FLIP_ENEMY_CRATE_IN_PANTRY, TaskType.FLIP_AND_PLACE_IN_PANTRY])
        
        return {
            'batch_size': len(self.current_task_batch),
            'pickups_planned': pickup_count,
            'flips_planned': flip_count,
            'pickup_capacity_used': f"{pickup_count}/{self.config.robot_max_capacity}",
            'flip_capacity_used': f"{flip_count}/{self.config.robot_flip_capacity}",
            'remaining_pickup_capacity': self.config.robot_max_capacity - pickup_count,
            'remaining_flip_capacity': self.config.robot_flip_capacity - flip_count,
        }
    
    def print_capacity_plan(self):
        """Print detailed capacity plan for debugging."""
        status = self.get_capacity_status()
        
        print("\n" + "="*70)
        print("CAPACITY PLAN")
        print("="*70)
        print(f"Batch Size: {status['batch_size']} tasks")
        print(f"Pickups: {status['pickup_capacity_used']}")
        print(f"Flips: {status['flip_capacity_used']}")
        print(f"Remaining Pickup Slots: {status['remaining_pickup_capacity']}")
        print(f"Remaining Flip Slots: {status['remaining_flip_capacity']}")
        print("\nBatch Tasks:")
        for i, task in enumerate(self.current_task_batch, 1):
            print(f"  {i}. {task.description} - {task.expected_score:.0f}pts")
        print("="*70 + "\n")
