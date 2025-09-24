import os
import pickle
import zstandard as zstd
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from collections import Counter
import argparse

# from .polycube import Polycube
from polycube import Polycube
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from itertools import product, combinations

def generate_polycubes(n):
    if n < 1:
        return []
    elif n == 1:
        return [Polycube.unit_cube()]
    elif n == 2:
        return [Polycube.domino()]

    base_cubes = generate_polycubes(n - 1)
    unique_hashes = set()
    lock = Lock()
    total = len(base_cubes)

    def process_base_cube(base_cube):
        local_polycubes = []
        for position in base_cube.get_expansion_positions():
            expanded_shape = base_cube.expand(position)
            if not expanded_shape.is_face_connected():
                continue
            normalized = expanded_shape.normalize()
            canonical_hash = normalized.get_canonical_hash()
            # Only add if not already present (avoid rotations)
            with lock:
                if canonical_hash not in unique_hashes:
                    unique_hashes.add(canonical_hash)
                    local_polycubes.append(normalized)
        return local_polycubes

    results = []
    with ThreadPoolExecutor() as executor:
        for local_polycubes in executor.map(process_base_cube, base_cubes):
            results.extend(local_polycubes)
    # Only keep unique canonical polycubes
    canonical_polycubes = {}
    for polycube in results:
        h = polycube.get_canonical_hash()
        if h not in canonical_polycubes:
            canonical_polycubes[h] = polycube
    print(f"Found {len(canonical_polycubes)} unique polycubes")

    return list(canonical_polycubes.values())

def save_to_cache(polycubes, path):
    serialized = pickle.dumps(polycubes)
    with open(path, "wb") as f:
        cctx = zstd.ZstdCompressor(level=3)
        f.write(cctx.compress(serialized))

def load_from_cache(path):
    with open(path, "rb") as f:
        dctx = zstd.ZstdDecompressor()
        decompressed = dctx.decompress(f.read())
        return pickle.loads(decompressed)

def get_known_count(n):
    known_counts = {
        1: 1, 2: 1, 3: 2, 4: 8, 5: 29, 6: 166, 7: 1023, 8: 6922, 9: 48311,
        10: 346543, 11: 2522522, 12: 18598427, 13: 139333147, 14: 1056657611,
        15: 8107839447, 16: 62709211271, 17: 489997729602, 18: 3847265309118
    }
    return known_counts.get(n)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cubes with specified parameters.")
    parser.add_argument('-n', '--num-cubes', type=int, default=5, help='Maximum limit of cubes in the shape')
    args = parser.parse_args()
    num_cubes = args.num_cubes
    
    polycube_coords_list = []
    for i in range(1, num_cubes + 1):
        polycube_list = generate_polycubes(i)
        for cube in polycube_list:
            blocks = []
            for block in cube.cubes:
                blocks.append((block.x, block.y, block.z))
            polycube_coords_list.append(blocks)
    # Only print unique cubes
    unique_coords = []
    seen = set()
    for blocks in polycube_coords_list:
        key = tuple(sorted(blocks))
        if key not in seen:
            seen.add(key)
            unique_coords.append(blocks)
    [print(i) for i in unique_coords]
    print(len(unique_coords))
    
    import matplotlib.pyplot as plt

    os.makedirs("images", exist_ok=True)

    def render_cube(blocks, filename):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_box_aspect([1,1,1])
        for x, y, z in blocks:
            # Draw cube at (x, y, z)
            r = [0, 1]
            for s, e in combinations(np.array(list(product(r, r, r))), 2):
                if np.sum(np.abs(s-e)) == 1:
                    ax.plot3D(*zip(s + np.array([x, y, z]), e + np.array([x, y, z])), color="b")
        ax.set_axis_off()
        plt.tight_layout()
        plt.savefig(filename)
        plt.close(fig)


    for idx, blocks in enumerate(unique_coords):
        filename = os.path.join("images", f"cube_{idx}.png")
        render_cube(blocks, filename)