import heapq

"""
Ce fichier contient la classe PathFinding, pour la gestion du pathfinding.
"""

# ==== PathFinding ====
class PathFinding:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

        # Précalcul des voisins pour chaque cellule (la grille est statique)
        self.neighbors_cache: dict[tuple, list] = {}
        self.precompute_neighbors()

    def precompute_neighbors(self):
        """Calcule une fois pour toutes les voisins de chaque cellule libre."""
        directions = [
            (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
            (-1,-1, 1.414), (1,-1, 1.414), (-1, 1, 1.414), (1, 1, 1.414),
        ]
        grid = self.grid
        rows = self.rows
        cols = self.cols

        for y in range(rows):
            for x in range(cols):
                if grid[y][x] != 0:
                    continue # cellule mur → pas de voisins
                neighbors = []
                for dx, dy, cost in directions:
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < cols and 0 <= ny < rows):
                        continue
                    if grid[ny][nx] != 0:
                        continue
                    if dx != 0 and dy != 0: # diagonale : pas de coin coupé
                        if grid[y][nx] != 0 or grid[ny][x] != 0:
                            continue
                    neighbors.append((nx, ny, cost))
                self.neighbors_cache[(x, y)] = neighbors

    @staticmethod
    def heuristic(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(dx, dy) + 0.414 * min(dx, dy)   # Chebyshev octile
    
    def find_path2(self, start, goal, dynamic_obstacles=None):
        if not (0 <= goal[0] < self.cols and 0 <= goal[1] < self.rows):
            return []
        if self.grid[goal[1]][goal[0]] != 0:
            return []
        if start == goal:
            return []

        neighbors_cache = self.neighbors_cache
        heuristic = self.heuristic

        # Bloque les cases des obstacles dynamiques
        blocked = dynamic_obstacles if dynamic_obstacles else set()

        open_set  = [(heuristic(start, goal), 0.0, start)]
        came_from = {start: None}
        g_score = {start: 0.0}
        closed = set()

        max_iterations = 2000
        iterations = 0

        while open_set:
            iterations += 1
            if iterations > max_iterations:
                return []

            _, g_cur, current = heapq.heappop(open_set)

            if current in closed:
                continue
            closed.add(current)

            if current == goal:
                break

            if g_cur > g_score.get(current, float('inf')):
                continue

            for nx, ny, cost in neighbors_cache.get(current, ()):
                neighbor = (nx, ny)
                if neighbor in blocked:  # 👈 obstacle dynamique
                    continue
                tentative_g = g_score[current] + cost
                if tentative_g < g_score.get(neighbor, float('inf')):
                    g_score[neighbor]   = tentative_g
                    came_from[neighbor] = current
                    f = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, tentative_g, neighbor))

        return self.reconstruct_path(came_from, start, goal)

    def find_path(self, start, goal):
        # Validations rapides
        if not (0 <= goal[0] < self.cols and 0 <= goal[1] < self.rows):
            return []
        if self.grid[goal[1]][goal[0]] != 0:
            return []
        if start == goal:
            return []

        neighbors_cache = self.neighbors_cache
        heuristic = self.heuristic

        open_set  = [(heuristic(start, goal), 0.0, start)]
        came_from = {start: None}
        g_score = {start: 0.0}
        closed = set()

        max_iterations = 2000
        iterations = 0

        while open_set:
            iterations += 1
            if iterations > max_iterations:
                return []

            _, g_cur, current = heapq.heappop(open_set)

            if current in closed:
                continue
            closed.add(current)

            if current == goal:
                break

            # g_cur peut être périmé (entrée dupliquée dans le heap)
            if g_cur > g_score.get(current, float('inf')):
                continue

            for nx, ny, cost in neighbors_cache.get(current, ()):
                neighbor = (nx, ny)
                tentative_g = g_score[current] + cost
                if tentative_g < g_score.get(neighbor, float('inf')):
                    g_score[neighbor]   = tentative_g
                    came_from[neighbor] = current
                    f = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, tentative_g, neighbor))

        return self.reconstruct_path(came_from, start, goal)

    @staticmethod
    def reconstruct_path(came_from, start, goal):
        if goal not in came_from:
            return []
        path    = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path