import argparse
import csv
from polycube_generator import cubes
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading
from scipy.spatial.transform import Rotation as R

# Generate a list of quaternions for rotations, spaced by angle_round degrees
def list_all_quaternions(angle_round):
    for x in range(0, 360, angle_round):
        for y in range(0, 360, angle_round):
            for z in range(0, 360, angle_round):
                # Create quaternion from Euler angles (xyz order)
                quat = R.from_euler('xyz', [x, y, z], degrees=True).as_quat()
                yield tuple(quat)

# Generate all polycubes that can be made from 1 to n cubes
def generate_all_polycubes(num_cubes):
    polycube_coords_list = []
    for i in range(1, num_cubes + 1):
        polycube_i_list = cubes.generate_polycubes(i)
        for i, cube in enumerate(polycube_i_list):
            coords = list(zip(*np.nonzero(cube)))
            polycube_coords_list.append(coords)
    
    # Convert back to standard int
    for i in range(0, len(polycube_coords_list)):
        for j in range(0, len(polycube_coords_list[i])):
            for k in range(0, len(polycube_coords_list[i][j])):
                polycube_coords_list[i][j] = tuple(int(i) for i in polycube_coords_list[i][j])
            
    return polycube_coords_list

def write_single_cubes(quat_polycubes):
    print("Export single-cube list")
    with open("single_cubes.csv", "w") as f:
        writer = csv.writer(f)
        header = ["num_blocks"]
        [header.append(f"block_{i}_pos") for i in range(1,num_cubes+1)]
        header.extend(["quat_x", "quat_y", "quat_z", "quat_w"])
        
        writer.writerow(header)
        
        for i in quat_polycubes:
            row = []
            num_cubes_i = len(i[0])
            block_positions = []
            for cube in range(0, num_cubes):
                try:
                    block_positions.append(i[0][cube])
                except IndexError:
                    block_positions.append("()")
            quat = i[1]
            row.append(num_cubes_i)
            row.extend(block_positions)
            row.extend(quat)  # quat_x, quat_y, quat_z, quat_w
            
            writer.writerow(row)

def paired_row(args):
    i, j, quat_polycubes, num_cubes = args
    row = []
    id = i * len(quat_polycubes) + j
    num_cubes_i = len(quat_polycubes[i][0])
    block_positions_i = []
    for cube in range(0, num_cubes):
        if cube < len(quat_polycubes[i][0]):
            block_positions_i.append(quat_polycubes[i][0][cube])
        else:
            block_positions_i.append("()")
    quat_i = quat_polycubes[i][1]
    
    num_cubes_j = len(quat_polycubes[j][0])
    block_positions_j = []
    for cube in range(0, num_cubes):
        if cube < len(quat_polycubes[j][0]):
            block_positions_j.append(quat_polycubes[j][0][cube])
        else:
            block_positions_j.append("()")
    quat_j = quat_polycubes[j][1]
    
    same = block_positions_i == block_positions_j
    
    row.append(id)
    row.append(same)
    row.append(num_cubes_i)
    row.extend(block_positions_i)
    row.extend(quat_i)
    row.append(num_cubes_j)
    row.extend(block_positions_j)
    row.extend(quat_j)
    return row

def write_paired_cubes(quat_polycubes):
    print("Export paired-cube list")
    header = ["id", "SAME", "im_1_num_blocks"]
    [header.append(f"im_1_block_{i}_pos") for i in range(1,num_cubes+1)]
    header.extend(["im_1_quat_x", "im_1_quat_y", "im_1_quat_z", "im_1_quat_w"])
    header.append("im_2_num_blocks")
    [header.append(f"im_2_block_{i}_pos") for i in range(1,num_cubes+1)]
    header.extend(["im_2_quat_x", "im_2_quat_y", "im_2_quat_z", "im_2_quat_w"])

    task_queue = Queue(maxsize=1000)
    write_lock = threading.Lock()

    def worker():
        while True:
            args = task_queue.get()
            if args is None:
                break
            row = paired_row(args)
            with write_lock:
                writer.writerow(row)
            task_queue.task_done()

    with open("paired_cubes.csv", "a", newline='') as f:
        writer = csv.writer(f)
        if pair_id_start == 0:
            writer.writerow(header)

        num_workers = min(8, threading.active_count() + 4)
        threads = []
        for _ in range(num_workers):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
            
        i_start = int(pair_id_start / len(quat_polycubes))
        j_start = pair_id_start - (len(quat_polycubes) * i_start)
        print(f"Starting at {pair_id_start}, i={i_start}, j={j_start}. quat_polycubes={len(quat_polycubes)}")

        for i in range(i_start, len(quat_polycubes)):
            for j in range(j_start, len(quat_polycubes)):
                task_queue.put((i, j, quat_polycubes, num_cubes))

        for _ in threads:
            task_queue.put(None)

        task_queue.join()
        for t in threads:
            t.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cubes with specified parameters.")
    parser.add_argument('-n', '--num-cubes', type=int, default=5, help='Maximum limit of cubes in the shape')
    parser.add_argument('-a', '--angle-round', type=int, default=10, help='Round viewing angles to the nearest a degrees')
    parser.add_argument('-s', '--single-only', type=bool, default=False, help='Only generate single cubes, not paired cubes')
    parser.add_argument('-p', '--pair-id-start', type=int, default=0, help="Sets the starting id for paired cubes")
    args = parser.parse_args()
    
    num_cubes = args.num_cubes
    angle_round = args.angle_round
    pair_id_start = args.pair_id_start
    single_only = args.single_only
    
    print("Generating quaternions...")
    quaternions = list(list_all_quaternions(angle_round))
    print("Generating polycubes...")
    polycubes = generate_all_polycubes(num_cubes)
    
    print("Cross-join on quaternions and polycubes...")
    quat_polycubes = [(y,x) for x in quaternions for y in polycubes]
    
    write_single_cubes(quat_polycubes)
            
    if not single_only:
        write_paired_cubes(quat_polycubes)
            
    print("Done.")