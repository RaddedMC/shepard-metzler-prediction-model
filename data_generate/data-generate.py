import argparse
import csv
from polycube_generator import cubes
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading

# List all angles that exist within our desired angle-rounding
def list_all_angles(angle_round):
    for x in range(0, 360, angle_round):
        for y in range(0, 360, angle_round):
            yield (x, y)
            
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

def write_single_cubes(angles_polycubes):
    print("Export single-cube list")
    with open("single_cubes.csv", "w") as f:
        writer = csv.writer(f)
        header = ["num_blocks"]
        [header.append(f"block_{i}_pos") for i in range(1,num_cubes+1)]
        header.append("angle_x")
        header.append("angle_y")
        
        writer.writerow(header)
        
        for i in angles_polycubes:
            row = []
            num_cubes_i = len(i[0])
            block_positions = []
            for cube in range(0, num_cubes):
                try:
                    block_positions.append(i[0][cube])
                except IndexError:
                    block_positions.append("()")
            angle_x = i[1][0]
            angle_y = i[1][1]
            
            row.append(num_cubes_i)
            row.extend(block_positions)
            row.append(angle_x)
            row.append(angle_y)
            
            writer.writerow(row)
            
def paired_row(args):
    i, j, angles_polycubes, num_cubes = args
    row = []
    id = i * len(angles_polycubes) + j
    num_cubes_i = len(angles_polycubes[i][0])
    block_positions_i = []
    for cube in range(0, num_cubes):
        if cube < len(angles_polycubes[i][0]):
            block_positions_i.append(angles_polycubes[i][0][cube])
        else:
            block_positions_i.append("()")
    angle_x_i = angles_polycubes[i][1][0]
    angle_y_i = angles_polycubes[i][1][1]
    
    num_cubes_j = len(angles_polycubes[j][0])
    block_positions_j = []
    for cube in range(0, num_cubes):
        if cube < len(angles_polycubes[j][0]):
            block_positions_j.append(angles_polycubes[j][0][cube])
        else:
            block_positions_j.append("()")
    angle_x_j = angles_polycubes[j][1][0]
    angle_y_j = angles_polycubes[j][1][1]
    
    same = block_positions_i == block_positions_j
    
    row.append(id)
    row.append(same)
    row.append(num_cubes_i)
    row.extend(block_positions_i)
    row.append(angle_x_i)
    row.append(angle_y_i)
    row.append(num_cubes_j)
    row.extend(block_positions_j)
    row.append(angle_x_j)
    row.append(angle_y_j)
    return row

def write_paired_cubes(angles_polycubes):
    print("Export paired-cube list")
    header = ["id", "SAME", "im_1_num_blocks"]
    [header.append(f"im_1_block_{i}_pos") for i in range(1,num_cubes+1)]
    header.append("im_1_angle_x")
    header.append("im_1_angle_y")
    header.append("im_2_num_blocks")
    [header.append(f"im_2_block_{i}_pos") for i in range(1,num_cubes+1)]
    header.append("im_2_angle_x")
    header.append("im_2_angle_y")

    task_queue = Queue(maxsize=1000)  # limit queue size to avoid memory issues
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

        num_workers = min(8, threading.active_count() + 4)  # adjust as needed
        threads = []
        for _ in range(num_workers):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
            
        i_start = int(pair_id_start / len(angles_polycubes))
        j_start = pair_id_start - (len(angles_polycubes) * i_start)
        print(f"Starting at {pair_id_start}, i={i_start}, j={j_start}. angles_polycubes={len(angles_polycubes)}")

        for i in range(i_start, len(angles_polycubes)):
            for j in range(j_start, len(angles_polycubes)):
                task_queue.put((i, j, angles_polycubes, num_cubes))

        # Signal workers to exit
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
    pair_id_start = args.pair_id_start + 1
    single_only = args.single_only
    
    print("Generating angles...")
    angles = list(list_all_angles(angle_round))
    print("Generating polycubes...")
    polycubes = generate_all_polycubes(num_cubes)
    
    print("Cross-join on angles and polycubes...")
    angles_polycubes = [(y,x) for x in angles for y in polycubes]
    
    write_single_cubes(angles_polycubes)
            
    if not single_only:
        write_paired_cubes(angles_polycubes)
            
    print("Done.")