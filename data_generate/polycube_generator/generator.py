import os
import pickle
import zstandard as zstd
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from collections import Counter

from .polycube import Polycube

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
    # print(f"Processing {total} base polycubes of size {n-1}")

    def process_base_cube(base_cube):
        local_polycubes = []
        for position in base_cube.get_expansion_positions():
            expanded_shape = base_cube.expand(position)
            if not expanded_shape.is_face_connected():
                continue
            normalized = expanded_shape.normalize()
            canonical_hash = normalized.get_canonical_hash()
            with lock:
                if canonical_hash not in unique_hashes:
                    unique_hashes.add(canonical_hash)
                    local_polycubes.append(normalized)
        return local_polycubes

    results = []
    with ThreadPoolExecutor() as executor:
        for idx, local_polycubes in enumerate(executor.map(process_base_cube, base_cubes)):
            results.extend(local_polycubes)
            #if idx % 100 == 0 or idx == total - 1:
                #print(f"\rGenerating polycubes n={n}: {100.0 * idx / total:.1f}%", end="", flush=True)
    #print(f"\rGenerating polycubes n={n}: 100%")
    print(f"Found {len(results)} unique polycubes")

    return results

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