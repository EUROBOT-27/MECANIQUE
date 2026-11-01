import numpy as np
from typing import List, Tuple, Optional


from .path_smoothing import smooth_path, _line_segment_circle_collision


def rrt_connect_plan(start: np.ndarray, goal: np.ndarray, obstacles: List[Tuple[np.ndarray, float]],
                     bounds: Tuple[float, float, float, float], max_iter: int = 2000,
                     step_size: float = 0.5, goal_sample_rate: float = 0.05) -> Optional[List[np.ndarray]]:
    """
    RRT-Connect planner (2D x,y) returning a list of [x,y,0] points from start to goal.

    Args:
        start: array-like [x,y,...]
        goal: array-like [x,y,...]
        obstacles: list of (center(np.array), radius(float))
        bounds: (xmin, xmax, ymin, ymax)
        max_iter: max iterations (per tree growth)
        step_size: incremental step size
        goal_sample_rate: probability to sample the goal directly (helps convergence)

    Returns:
        path as list of np.array([x,y,0.0]) or None if not found
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

    def extend(tree: List[Node], target: Node) -> Optional[Node]:
        """Try to extend tree towards target; return last added node or None."""
        nearest_node = nearest(tree, target)
        new_node = steer(nearest_node, target, step_size)
        if not collision_free(nearest_node, new_node):
            return None
        tree.append(new_node)
        # keep extending while we can get closer
        while True:
            if np.hypot(new_node.x - target.x, new_node.y - target.y) <= step_size:
                return new_node
            next_node = steer(new_node, target, step_size)
            if not collision_free(new_node, next_node):
                return new_node
            tree.append(next_node)
            new_node = next_node

    def connect(tree: List[Node], target: Node) -> Optional[Node]:
        """Attempt to connect tree to target by repeatedly extending; return final node if reached."""
        while True:
            new = extend(tree, target)
            if new is None:
                return None
            if np.hypot(new.x - target.x, new.y - target.y) <= step_size:
                return new
            # otherwise keep trying (extend already did multiple steps)

    start_node = Node(float(start[0]), float(start[1]))
    goal_node = Node(float(goal[0]), float(goal[1]))

    tree_a = [start_node]
    tree_b = [goal_node]

    for i in range(max_iter):
        rnd = sample_node()
        na = extend(tree_a, rnd)
        if na is not None:
            nb = connect(tree_b, na)
            if nb is not None:
                # build path from start -> na  and nb -> goal
                path_a = []
                cur = na
                while cur is not None:
                    path_a.append(np.array([cur.x, cur.y, 0.0]))
                    cur = cur.parent
                path_a.reverse()

                path_b = []
                cur = nb
                while cur is not None:
                    path_b.append(np.array([cur.x, cur.y, 0.0]))
                    cur = cur.parent
                # path_b goes from meeting node back to goal; we need path from meeting to goal
                # avoid duplicating the meeting point
                full = path_a + path_b
                return smooth_path(full, obstacles)
        # swap trees
        tree_a, tree_b = tree_b, tree_a

    return None
