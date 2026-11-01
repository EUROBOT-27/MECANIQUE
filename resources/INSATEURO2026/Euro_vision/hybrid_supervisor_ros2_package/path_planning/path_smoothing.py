import numpy as np
from typing import List, Tuple

def _line_segment_circle_collision(p1: np.ndarray, p2: np.ndarray, center: np.ndarray, radius: float) -> bool:
    """Return True if line segment p1-p2 intersects circle (center, radius) in 2D (x,y)."""
    x1, y1 = float(p1[0]), float(p1[1])
    x2, y2 = float(p2[0]), float(p2[1])
    cx, cy = float(center[0]), float(center[1])
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return np.hypot(cx - x1, cy - y1) <= radius
    t = ((cx - x1) * dx + (cy - y1) * dy) / (dx*dx + dy*dy)
    t = max(0.0, min(1.0, t))
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    dist = np.hypot(closest_x - cx, closest_y - cy)
    return dist <= radius

def smooth_path(path: List[np.ndarray], obstacles: List[Tuple[np.ndarray, float]], iterations: int = 100) -> List[np.ndarray]:
    """
    Smooths a given path by attempting to connect non-consecutive nodes with a straight line.
    First performs greedy straightening to find longest collision-free segments, then does random smoothing.
    
    Args:
        path: The initial path as a list of points.
        obstacles: A list of obstacles to check for collisions.
        iterations: The number of smoothing iterations.
        
    Returns:
        The smoothed path.
    """
    if len(path) <= 2:
        return list(path)
    
    # Step 1: Greedy straightening - find longest collision-free segments
    smoothed_path = list(path)
    i = 0
    while i < len(smoothed_path) - 1:
        # Try to connect from i to the farthest reachable point
        max_reach = i + 1
        
        for j in range(len(smoothed_path) - 1, i + 1, -1):
            p_start = smoothed_path[i]
            p_end = smoothed_path[j]
            
            # Check if straight line from i to j is collision-free
            is_collision_free = True
            for (c, r) in obstacles:
                if _line_segment_circle_collision(p_start, p_end, np.array([c[0], c[1]]), r):
                    is_collision_free = False
                    break
            
            if is_collision_free:
                # Found the longest segment from i to j
                max_reach = j
                break
        
        # If we can skip waypoints, remove them
        if max_reach > i + 1:
            # Remove all waypoints between i and max_reach
            smoothed_path = smoothed_path[:i + 1] + smoothed_path[max_reach:]
        
        i += 1
    
    # Step 2: Random smoothing for further refinement
    for _ in range(iterations):
        if len(smoothed_path) <= 2:
            break
        
        idx1, idx2 = np.random.choice(len(smoothed_path), 2)
        if idx1 == idx2:
            continue
        
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
            
        p1 = smoothed_path[idx1]
        p2 = smoothed_path[idx2]
        
        is_collision_free = True
        for (c, r) in obstacles:
            if _line_segment_circle_collision(p1, p2, np.array([c[0], c[1]]), r):
                is_collision_free = False
                break
        
        if is_collision_free:
            smoothed_path = smoothed_path[:idx1 + 1] + smoothed_path[idx2:]
            
    return smoothed_path
