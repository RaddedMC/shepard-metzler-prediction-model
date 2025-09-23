from collections import deque
from typing import List, Set, Tuple

class Pos:
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def adjacent_positions(self) -> List['Pos']:
        return [
            Pos(self.x + 1, self.y, self.z),
            Pos(self.x - 1, self.y, self.z),
            Pos(self.x, self.y + 1, self.z),
            Pos(self.x, self.y - 1, self.z),
            Pos(self.x, self.y, self.z + 1),
            Pos(self.x, self.y, self.z - 1),
        ]

class Polycube:
    def __init__(self, cubes: List[Pos]):
        self.cubes = cubes

    @staticmethod
    def new(cubes: List[Pos]) -> 'Polycube':
        return Polycube(cubes)

    def get_expansion_positions(self) -> Set[Pos]:
        expansion_positions = set()
        current_positions = set(self.cubes)
        for cube in self.cubes:
            for adj in cube.adjacent_positions():
                if adj not in current_positions:
                    expansion_positions.add(adj)
        return expansion_positions

    def expand(self, position: Pos) -> 'Polycube':
        return Polycube(self.cubes + [position])

    def normalize(self) -> 'Polycube':
        if not self.cubes:
            return Polycube(self.cubes[:])
        min_x = min(p.x for p in self.cubes)
        min_y = min(p.y for p in self.cubes)
        min_z = min(p.z for p in self.cubes)
        new_cubes = [Pos(p.x - min_x, p.y - min_y, p.z - min_z) for p in self.cubes]
        return Polycube(new_cubes)

    def is_face_connected(self) -> bool:
        if len(self.cubes) <= 1:
            return True
        visited = set()
        queue = deque()
        positions = set(self.cubes)
        queue.append(self.cubes[0])
        visited.add(self.cubes[0])
        while queue:
            current = queue.popleft()
            for adj in current.adjacent_positions():
                if adj in positions and adj not in visited:
                    visited.add(adj)
                    queue.append(adj)
        return len(visited) == len(self.cubes)

    @staticmethod
    def unit_cube() -> 'Polycube':
        return Polycube([Pos(0, 0, 0)])

    @staticmethod
    def domino() -> 'Polycube':
        return Polycube([Pos(0, 0, 0), Pos(1, 0, 0)])

    def get_dimensions(self) -> Tuple[int, int, int]:
        if not self.cubes:
            return (0, 0, 0)
        max_x = max(p.x for p in self.cubes)
        max_y = max(p.y for p in self.cubes)
        max_z = max(p.z for p in self.cubes)
        return (max_x + 1, max_y + 1, max_z + 1)

    def is_linear(self) -> bool:
        width, height, depth = self.get_dimensions()
        return (width == 1 and height == 1) or \
               (width == 1 and depth == 1) or \
               (height == 1 and depth == 1)

    def is_flat(self) -> bool:
        width, height, depth = self.get_dimensions()
        return width == 1 or height == 1 or depth == 1

    def get_canonical_hash(self) -> int:
        # Use a tuple of sorted normalized positions for hash
        norm = self.normalize()
        sorted_positions = sorted((p.x, p.y, p.z) for p in norm.cubes)
        return hash(tuple(sorted_positions))
