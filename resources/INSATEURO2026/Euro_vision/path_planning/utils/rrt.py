import numpy as np
from typing import List, Tuple, Optional


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


def rrt_plan(start: np.ndarray, goal: np.ndarray, obstacles: List[Tuple[np.ndarray, float]],
             bounds: Tuple[float, float, float, float], max_iter: int = 2000, step_size: float = 0.25,
             goal_sample_rate: float = 0.05) -> Optional[List[np.ndarray]]:
    """
    Simple RRT planner in 2D (x,y). start/goal are array-like with at least two elements.

    Args:
        start: array-like [x, y, ...]
        goal: array-like [x, y, ...]
        obstacles: list of tuples (center(np.array), radius(float))
        bounds: (xmin, xmax, ymin, ymax)
        max_iter: maximum number of iterations
        step_size: growth step size (meters)
        goal_sample_rate: probability to sample the goal directly

    Returns:
        List of 3D points [[x,y,0], ...] representing the path, or None on failure.
    """
    xmin, xmax, ymin, ymax = bounds

    class Node:
        def __init__(self, x: float, y: float, parent: Optional['Node'] = None):
            self.x = x
            self.y = y
            self.parent = parent

    def sample_node() -> Node:
        if np.random.rand() < goal_sample_rate:
            return Node(float(goal[0]), float(goal[1]))
        return Node(float(np.random.uniform(xmin, xmax)), float(np.random.uniform(ymin, ymax)))

    def nearest(node_list: List[Node], rnd: Node) -> Node:
        dlist = [(n.x - rnd.x)**2 + (n.y - rnd.y)**2 for n in node_list]
        idx = int(np.argmin(dlist))
        return node_list[idx]

    def steer(from_node: Node, to_node: Node, step: float) -> Node:
        dx = to_node.x - from_node.x
        dy = to_node.y - from_node.y
        dist = np.hypot(dx, dy)
        if dist <= step:
            return Node(to_node.x, to_node.y, from_node)
        theta = np.arctan2(dy, dx)
        nx = from_node.x + step * np.cos(theta)
        ny = from_node.y + step * np.sin(theta)
        return Node(nx, ny, from_node)

    def collision_free(p_from: Node, p_to: Node) -> bool:
        p1 = np.array([p_from.x, p_from.y])
        p2 = np.array([p_to.x, p_to.y])
        for (c, r) in obstacles:
            if _line_segment_circle_collision(p1, p2, np.array([c[0], c[1]]), r):
                return False
        return True

    start_node = Node(float(start[0]), float(start[1]))
    goal_node = Node(float(goal[0]), float(goal[1]))
    node_list = [start_node]

    for i in range(max_iter):
        rnd = sample_node()
        nearest_node = nearest(node_list, rnd)
        new_node = steer(nearest_node, rnd, step_size)
        if not collision_free(nearest_node, new_node):
            continue
        node_list.append(new_node)
        if np.hypot(new_node.x - goal_node.x, new_node.y - goal_node.y) <= step_size:
            # build path
            path = [np.array([goal_node.x, goal_node.y, 0.0])]
            cur = new_node
            while cur is not None:
                path.append(np.array([cur.x, cur.y, 0.0]))
                cur = cur.parent
            path.reverse()
            return path

    return None
