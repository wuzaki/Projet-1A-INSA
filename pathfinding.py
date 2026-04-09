import heapq

class PathFinding:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def heuristic(self, a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(dx, dy) + (1.414 - 1) * min(dx, dy)

    def get_neighbors(self, node):
        x, y = node

        directions = [
            (-1,0),(1,0),(0,-1),(0,1),      # cardinales
            (-1,-1),(1,-1),(-1,1),(1,1)     # diagonales
        ]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if not (0 <= nx < self.cols and 0 <= ny < self.rows):
                continue

            # case bloquée
            if self.grid[ny][nx] != 0:
                continue

            # empêche de couper les coins
            if dx != 0 and dy != 0:
                if self.grid[y][nx] != 0 or self.grid[ny][x] != 0:
                    continue

            yield (nx, ny)

    def find_path(self, start, goal):
        if not (0 <= goal[0] < self.cols and 0 <= goal[1] < self.rows):
            return []

        if self.grid[goal[1]][goal[0]] != 0:
            return []

        open_set = []
        heapq.heappush(open_set, (0, start))

        came_from = {start: None}
        g_score = {start: 0}

        max_iterations = 2000
        iterations = 0

        while open_set:
            iterations += 1
            if iterations > max_iterations:
                return []
            
            _, current = heapq.heappop(open_set)
            if self.heuristic(current, goal) > 50:
                continue

            if current == goal:
                break

            for neighbor in self.get_neighbors(current):
                cost = 1.414 if neighbor[0] != current[0] and neighbor[1] != current[1] else 1
                tentative_g = g_score[current] + cost

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, goal)

                    heapq.heappush(open_set, (f_score, neighbor))
                    came_from[neighbor] = current

        return self.reconstruct_path(came_from, start, goal)

    def reconstruct_path(self, came_from, start, goal):
        if goal not in came_from:
            return []

        path = []
        current = goal

        while current != start:
            path.append(current)
            current = came_from[current]

        path.reverse()
        return path