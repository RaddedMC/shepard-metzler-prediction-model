import argparse
import csv
from polycube_generator import cubes
import numpy as np

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
    return polycube_coords_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cubes with specified parameters.")
    parser.add_argument('-n', '--num-cubes', type=int, default=5, help='Maximum limit of cubes in the shape')
    parser.add_argument('-a', '--angle-round', type=int, default=10, help='Round viewing angles to the nearest a degrees')
    args = parser.parse_args()
    
    num_cubes = args.num_cubes
    angle_round = args.angle_round
    
    print("Generating angles...")
    angles = list(list_all_angles(angle_round))
    print("Generating polycubes...")
    polycubes = generate_all_polycubes(num_cubes)
    
    print("Cross-join on angles and polycubes...")
    angles_polycubes = [(y,x) for x in angles for y in polycubes]
    
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
            for cube in range(0, num_cubes-1):
                try:
                    block_positions.append(i[0][cube])
                except IndexError:
                    block_positions.append("")
            angle_x = i[1][0]
            angle_y = i[1][1]
            
            row.append(num_cubes_i)
            row.extend(block_positions)
            row.append(angle_x)
            row.append(angle_y)
            
            writer.writerow(row)
            
    print("Export paired-cube list")
    with open("paired_cubes.csv", "w") as f:
        writer = csv.writer(f)
        header = ["id", "SAME", "im_1_num_blocks"]
        [header.append(f"im_1_block_{i}_pos") for i in range(1,num_cubes+1)]
        header.append("im_1_angle_x")
        header.append("im_1_angle_y")
        header.append("im_2_num_blocks")
        [header.append(f"im_2_block_{i}_pos") for i in range(1,num_cubes+1)]
        header.append("im_2_angle_x")
        header.append("im_2_angle_y")
        
        writer.writerow(header)
        
        for i in range(0, len(angles_polycubes)):
            for j in range(0, len(angles_polycubes)):
                row = []
                id = i * len(angles_polycubes) + j
                num_cubes_i = len(angles_polycubes[i][0])
                block_positions_i = []
                for cube in range(0, num_cubes_i):
                    try:
                        block_positions_i.append(angles_polycubes[i][0][cube-1])
                    except IndexError:
                        block_positions.append("")
                angle_x_i = angles_polycubes[i][1][0]
                angle_y_i = angles_polycubes[i][1][1]
                
                num_cubes_j = len(angles_polycubes[j][0])
                block_positions_j = []
                for cube in range(0, num_cubes_j):
                    try:
                        block_positions_j.append(angles_polycubes[j][0][cube-1])
                    except IndexError:
                        block_positions.append("")
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
                
                writer.writerow(row)
            
    print("Done.")