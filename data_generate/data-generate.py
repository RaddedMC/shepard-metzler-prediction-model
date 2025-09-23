import argparse
from polycube_generator import generator

# List all angles that exist within our desired angle-rounding
def list_all_angles(angle_round):
    for x in range(0, 360, angle_round):
        for y in range(0, 360, angle_round):
            yield (x, y)
            
# Generate all polycubes that can be made from 1 to n cubes
def generate_all_polycubes(num_cubes):
    return generator.generate_polycubes(num_cubes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cubes with specified parameters.")
    parser.add_argument('-n', '--num-cubes', type=int, default=5, help='Maximum limit of cubes in the shape')
    parser.add_argument('-a', '--angle-round', type=int, default=10, help='Round viewing angles to the nearest a degrees')
    args = parser.parse_args()
    
    num_cubes = args.num_cubes
    angle_round = args.angle_round
    
    # print([ i for i in list_all_angles(angle_round)])
    print(generate_all_polycubes(num_cubes))