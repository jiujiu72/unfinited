import heapq
import math

DIRECTIONS = [
    (1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
    (1, 1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (-1, -1, 1.414),
]

MAX_ITERATIONS = 2000


def heuristic(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy) + (1.414 - 1.0) * min(dx, dy)


def astar(dungeon, start, goal):
    if start == goal:
        return []

    if not dungeon.is_walkable(goal[0], goal[1]):
        return []

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    iterations = 0

    while open_set:
        iterations += 1
        if iterations > MAX_ITERATIONS:
            break

        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        cx, cy = current
        for dx, dy, cost in DIRECTIONS:
            nx, ny = cx + dx, cy + dy

            if not dungeon.is_walkable(nx, ny):
                continue

            if dx != 0 and dy != 0:
                if not dungeon.is_walkable(cx + dx, cy) or not dungeon.is_walkable(cx, cy + dy):
                    continue

            new_g = g_score[current] + cost
            neighbor = (nx, ny)

            if neighbor in g_score and new_g >= g_score[neighbor]:
                continue

            g_score[neighbor] = new_g
            f = new_g + heuristic(neighbor, goal)
            came_from[neighbor] = current
            heapq.heappush(open_set, (f, neighbor))

    return []
