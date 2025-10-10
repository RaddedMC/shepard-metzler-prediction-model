import argparse
import csv
from polycube_generator import cubes
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading
import sqlite3
            
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

# Write the angles to the database
def create_angles(conn):
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS angle (
            id INTEGER PRIMARY KEY,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL
        );"""
    )
    
    for x in range(0, 360, angle_round):
        for y in range(0, 360, angle_round):
            cursor.execute(
                """INSERT INTO angle(x,y)
                VALUES(?,?);""", (x, y) 
            )
            
# Write the polycubes to the database
def create_polycubes(conn):
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS polycube (
        id INTEGER PRIMARY KEY,
        num_blocks INTEGER NOT NULL,
        block_positions TEXT NOT NULL
        );"""
    )
    polycube_list = generate_all_polycubes(num_cubes)
    for polycube in polycube_list:
        num_blocks = len(polycube)
        block_positions = []
        for block in range (0, num_blocks):
            block_positions.append(polycube[block])
        cursor.execute(
            """INSERT INTO polycube(num_blocks, block_positions)
            VALUES(?,?);""", (num_blocks, str(block_positions))
        )
        
# Write singular cube views to the database
def create_single_cube_views(conn):
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE single_cube_view AS
           SELECT
               ROW_NUMBER() OVER () AS id,
               angle.id AS angle_id,
               polycube.id AS polycube_id
           FROM angle
           CROSS JOIN polycube;
        """
    )
    
# Write paired cube views to the database
def create_paired_cube_views(conn):
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE paired_cube_view AS
           SELECT
               ROW_NUMBER() OVER () AS id,
               scv1.id AS single_cube_view_id_1,
               scv2.id AS single_cube_view_id_2,
               (scv1.polycube_id = scv2.polycube_id) AS same
           FROM single_cube_view scv1
           CROSS JOIN single_cube_view scv2;
        """
    )

# Start
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
    
    print("Connecting to database...")
    try:
        with sqlite3.connect("cubes_data.sqlite3") as conn:
            print("Generating angles...")
            create_angles(conn)
            
            print("Generating polycubes...")
            create_polycubes(conn)
            
            print("Create single polycube views...")
            create_single_cube_views(conn)
            
            print("Create paired polycube views...")
            print("This may take a while.")
            create_paired_cube_views(conn)
            
            print("Done.")
    except sqlite3.OperationalError as e:
        print("Failed to open database: ", e)