import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import random
from copy import deepcopy
import os
import json
import pickle

class CubeStructureGenerator:
    def __init__(self):
        self.directions = [
            (1, 0, 0), (-1, 0, 0),  # x-axis
            (0, 1, 0), (0, -1, 0),  # y-axis
            (0, 0, 1), (0, 0, -1)   # z-axis
        ]
    
    def generate_connected_structure(self, num_cubes):
        """Generate a connected cube structure with specified number of cubes"""
        if num_cubes <= 0:
            return []
        
        # Start with one cube at origin
        cubes = [(0, 0, 0)]
        
        # Add remaining cubes one by one, ensuring connectivity
        for _ in range(num_cubes - 1):
            # Choose a random existing cube to extend from
            base_cube = random.choice(cubes)
            
            # Find valid adjacent positions
            valid_positions = []
            for dx, dy, dz in self.directions:
                new_pos = (base_cube[0] + dx, base_cube[1] + dy, base_cube[2] + dz)
                if new_pos not in cubes:
                    valid_positions.append(new_pos)
            
            if valid_positions:
                new_cube = random.choice(valid_positions)
                cubes.append(new_cube)
        
        return cubes
    
    def normalize_structure(self, cubes):
        """Normalize structure to start from (0,0,0)"""
        if not cubes:
            return cubes
        
        min_x = min(cube[0] for cube in cubes)
        min_y = min(cube[1] for cube in cubes)
        min_z = min(cube[2] for cube in cubes)
        
        normalized = [(x - min_x, y - min_y, z - min_z) for x, y, z in cubes]
        return normalized
    
    def apply_random_transform(self, cubes):
        """Apply random rotation and reflection to create variations"""
        if not cubes:
            return cubes
        
        transformed = deepcopy(cubes)
        
        # Random rotations (90-degree increments around each axis)
        rotations = [
            lambda p: (p[0], p[1], p[2]),  # identity
            lambda p: (p[0], -p[2], p[1]),  # 90° around x
            lambda p: (p[0], -p[1], -p[2]),  # 180° around x
            lambda p: (p[0], p[2], -p[1]),  # 270° around x
            lambda p: (-p[2], p[1], p[0]),  # 90° around y
            lambda p: (-p[0], p[1], -p[2]),  # 180° around y
            lambda p: (p[2], p[1], -p[0]),  # 270° around y
            lambda p: (-p[1], p[0], p[2]),  # 90° around z
            lambda p: (-p[0], -p[1], p[2]),  # 180° around z
            lambda p: (p[1], -p[0], p[2]),  # 270° around z
        ]
        
        # Apply random rotation
        rotation = random.choice(rotations)
        transformed = [rotation(cube) for cube in transformed]
        
        # Apply random reflection
        if random.random() < 0.3:  # 30% chance of reflection
            axis = random.choice([0, 1, 2])
            transformed = [tuple(-cube[i] if i == axis else cube[i] for i in range(3)) 
                          for cube in transformed]
        
        return self.normalize_structure(transformed)
    
    def structures_are_same(self, struct1, struct2):
        """Check if two structures are the same after normalization"""
        if len(struct1) != len(struct2):
            return False
        
        # Normalize both structures
        norm1 = set(self.normalize_structure(struct1))
        norm2 = set(self.normalize_structure(struct2))
        
        # Try all possible rotations and reflections of struct2
        rotations = [
            lambda p: (p[0], p[1], p[2]),
            lambda p: (p[0], -p[2], p[1]),
            lambda p: (p[0], -p[1], -p[2]),
            lambda p: (p[0], p[2], -p[1]),
            lambda p: (-p[2], p[1], p[0]),
            lambda p: (-p[0], p[1], -p[2]),
            lambda p: (p[2], p[1], -p[0]),
            lambda p: (-p[1], p[0], p[2]),
            lambda p: (-p[0], -p[1], p[2]),
            lambda p: (p[1], -p[0], p[2]),
        ]
        
        for rotation in rotations:
            rotated = [rotation(cube) for cube in norm2]
            normalized_rotated = set(self.normalize_structure(rotated))
            if norm1 == normalized_rotated:
                return True
            
            # Also try reflections
            for axis in range(3):
                reflected = [tuple(-cube[i] if i == axis else cube[i] for i in range(3)) 
                           for cube in rotated]
                normalized_reflected = set(self.normalize_structure(reflected))
                if norm1 == normalized_reflected:
                    return True
        
        return False
    
    def generate_pair(self, num_cubes, should_be_same=True):
        """Generate a pair of structures with specified properties"""
        # Generate first structure
        struct1 = self.generate_connected_structure(num_cubes)
        struct1 = self.normalize_structure(struct1)
        
        if should_be_same:
            # Create a transformed version of the same structure
            struct2 = self.apply_random_transform(struct1)
        else:
            # Generate a different structure
            max_attempts = 100
            for _ in range(max_attempts):
                struct2 = self.generate_connected_structure(num_cubes)
                struct2 = self.normalize_structure(struct2)
                
                if not self.structures_are_same(struct1, struct2):
                    break
            else:
                # If we couldn't generate a different structure, apply more transforms
                struct2 = self.apply_random_transform(struct1)
                # Add or move one cube to make it different
                if len(struct2) > 1:
                    struct2 = struct2[:-1]  # Remove last cube
                    # Add a new cube at a different position
                    base_cube = random.choice(struct2)
                    for dx, dy, dz in self.directions:
                        new_pos = (base_cube[0] + dx, base_cube[1] + dy, base_cube[2] + dz)
                        if new_pos not in struct2:
                            struct2.append(new_pos)
                            break
        
        return struct1, struct2
    
    def generate_dataset(self, num_pairs=20, cube_counts=None, same_ratio=0.5):
        """Generate a dataset of cube structure pairs"""
        if cube_counts is None:
            cube_counts = [3, 4, 5]  # Default cube counts
        
        dataset = []
        same_count = int(num_pairs * same_ratio)
        different_count = num_pairs - same_count
        
        # Generate same pairs
        for _ in range(same_count):
            num_cubes = random.choice(cube_counts)
            struct1, struct2 = self.generate_pair(num_cubes, should_be_same=True)
            dataset.append({
                'pair_id': len(dataset),
                'structure1': struct1,
                'structure2': struct2,
                'num_cubes': num_cubes,
                'is_same': True
            })
        
        # Generate different pairs
        for _ in range(different_count):
            num_cubes = random.choice(cube_counts)
            struct1, struct2 = self.generate_pair(num_cubes, should_be_same=False)
            dataset.append({
                'pair_id': len(dataset),
                'structure1': struct1,
                'structure2': struct2,
                'num_cubes': num_cubes,
                'is_same': False
            })
        
        # Shuffle the dataset
        random.shuffle(dataset)
        
        # Update pair_ids after shuffling
        for i, pair in enumerate(dataset):
            pair['pair_id'] = i
        
        return dataset
    
    def draw_cube(self, ax, position, color='lightblue', alpha=1.0):
        """Draw a single solid cube at given position"""
        x, y, z = position
        
        # Define the vertices of a cube
        vertices = np.array([
            [x, y, z], [x+1, y, z], [x+1, y+1, z], [x, y+1, z],  # bottom face
            [x, y, z+1], [x+1, y, z+1], [x+1, y+1, z+1], [x, y+1, z+1]  # top face
        ])
        
        # Define the 6 faces of the cube with proper ordering for solid appearance
        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],  # bottom (z=0)
            [vertices[4], vertices[7], vertices[6], vertices[5]],  # top (z=1) - reversed for proper normal
            [vertices[0], vertices[4], vertices[5], vertices[1]],  # front (y=0)
            [vertices[2], vertices[6], vertices[7], vertices[3]],  # back (y=1)
            [vertices[1], vertices[5], vertices[6], vertices[2]],  # right (x=1)
            [vertices[4], vertices[0], vertices[3], vertices[7]]   # left (x=0)
        ]
        
        # Create different shades for different faces to enhance 3D effect
        if isinstance(color, str):
            import matplotlib.colors as mcolors
            base_color = mcolors.to_rgb(color)
        else:
            base_color = color[:3] if len(color) >= 3 else color
        
        # Create shading: top face lightest, front medium, right darkest
        face_colors = []
        shading_factors = [0.7, 1.0, 0.8, 0.6, 0.5, 0.6]  # bottom, top, front, back, right, left
        
        for factor in shading_factors:
            shaded_color = tuple(min(1.0, c * factor) for c in base_color)
            face_colors.append(shaded_color)
        
        # Add faces to the plot with solid appearance
        collection = Poly3DCollection(faces, 
                                    facecolors=face_colors, 
                                    alpha=alpha, 
                                    edgecolors='black',
                                    linewidths=0.5)
        
        # Ensure proper z-ordering for solid appearance
        collection.set_sort_zpos(z + 0.5)
        ax.add_collection3d(collection)
    
    def visualize_pair(self, pair_data, figsize=(15, 7), save_path=None):
        """Visualize a pair of cube structures with solid cubes - same color for both"""
        struct1 = pair_data['structure1']
        struct2 = pair_data['structure2']
        is_same = pair_data['is_same']
        pair_id = pair_data['pair_id']
        
        # Use same color for both structures in the pair
        cube_color = 'steelblue'  # Consistent color for both structures
        
        fig = plt.figure(figsize=figsize)
        
        # Plot first structure
        ax1 = fig.add_subplot(121, projection='3d')
        
        # Sort cubes by distance from camera for proper rendering
        sorted_cubes1 = sorted(struct1, key=lambda cube: cube[0] + cube[1] + cube[2])
        for cube in sorted_cubes1:
            self.draw_cube(ax1, cube, color=cube_color, alpha=1.0)
        
        ax1.set_title(f'Pair {pair_id} - Structure 1', fontsize=12, fontweight='bold')
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        
        # Set equal aspect ratio and clean appearance
        max_range1 = max(max(cube) for cube in struct1) + 1
        ax1.set_xlim([0, max_range1])
        ax1.set_ylim([0, max_range1])
        ax1.set_zlim([0, max_range1])
        
        # Set viewing angle for better 3D effect
        ax1.view_init(elev=20, azim=45)
        ax1.grid(False)
        ax1.set_facecolor('white')
        
        # Plot second structure with SAME color
        ax2 = fig.add_subplot(122, projection='3d')
        
        # Sort cubes by distance from camera for proper rendering
        sorted_cubes2 = sorted(struct2, key=lambda cube: cube[0] + cube[1] + cube[2])
        for cube in sorted_cubes2:
            self.draw_cube(ax2, cube, color=cube_color, alpha=1.0)  # Same color as structure 1
        
        ax2.set_title(f'Pair {pair_id} - Structure 2', fontsize=12, fontweight='bold')
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_zlabel('Z')
        
        # Set equal aspect ratio and clean appearance
        max_range2 = max(max(cube) for cube in struct2) + 1
        ax2.set_xlim([0, max_range2])
        ax2.set_ylim([0, max_range2])
        ax2.set_zlim([0, max_range2])
        
        # Set viewing angle for better 3D effect
        ax2.view_init(elev=20, azim=45)
        ax2.grid(False)
        ax2.set_facecolor('white')
        
        # Add main title with better styling
        same_text = "SAME" if is_same else "DIFFERENT"
        color = 'green' if is_same else 'red'
        fig.suptitle(f'Cube Pair {pair_id} ({pair_data["num_cubes"]} cubes each) - {same_text}', 
                    fontsize=16, fontweight='bold', color=color)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()  # Close to save memory
        
        return fig
    
    def save_all_visualizations(self, dataset, folder_name="try6Dataset"):
        """Save visualizations of all pairs"""
        vis_folder = os.path.join(folder_name, 'visualizations')
        saved_files = []
        
        print("Saving visualizations...")
        for i, pair in enumerate(dataset):
            filename = f"pair_{pair['pair_id']:03d}_{pair['num_cubes']}cubes_{'same' if pair['is_same'] else 'diff'}.png"
            save_path = os.path.join(vis_folder, filename)
            
            self.visualize_pair(pair, save_path=save_path)
            saved_files.append(save_path)
            
            if (i + 1) % 10 == 0:
                print(f"  Saved {i + 1}/{len(dataset)} visualizations")
        
        print(f"All {len(dataset)} visualizations saved to {vis_folder}")
        return saved_files
    
    def create_output_folder(self, folder_name="try6Dataset"):
        """Create output folder and subfolders"""
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        # Create subfolders
        subfolders = ['visualizations', 'data', 'stats']
        for subfolder in subfolders:
            subfolder_path = os.path.join(folder_name, subfolder)
            if not os.path.exists(subfolder_path):
                os.makedirs(subfolder_path)
        
        return folder_name
    
    def save_dataset_stats(self, dataset, folder_name="try6Dataset"):
        """Save dataset statistics to a file"""
        same_count = sum(1 for pair in dataset if pair['is_same'])
        different_count = len(dataset) - same_count
        
        cube_count_distribution = {}
        for pair in dataset:
            count = pair['num_cubes']
            if count not in cube_count_distribution:
                cube_count_distribution[count] = {'same': 0, 'different': 0}
            
            if pair['is_same']:
                cube_count_distribution[count]['same'] += 1
            else:
                cube_count_distribution[count]['different'] += 1
        
        # Save text stats
        stats_file = os.path.join(folder_name, 'stats', 'dataset_stats.txt')
        with open(stats_file, 'w') as f:
            f.write(f"Dataset Statistics\n")
            f.write(f"==================\n")
            f.write(f"Total pairs: {len(dataset)}\n")
            f.write(f"Same pairs: {same_count} ({same_count/len(dataset)*100:.1f}%)\n")
            f.write(f"Different pairs: {different_count} ({different_count/len(dataset)*100:.1f}%)\n\n")
            
            f.write(f"Distribution by cube count:\n")
            for count in sorted(cube_count_distribution.keys()):
                stats = cube_count_distribution[count]
                total = stats['same'] + stats['different']
                f.write(f"{count} cubes: {total} pairs ({stats['same']} same, {stats['different']} different)\n")
        
        # Save JSON stats
        stats_data = {
            'total_pairs': len(dataset),
            'same_pairs': same_count,
            'different_pairs': different_count,
            'same_ratio': same_count / len(dataset),
            'cube_count_distribution': cube_count_distribution
        }
        
        json_file = os.path.join(folder_name, 'stats', 'dataset_stats.json')
        with open(json_file, 'w') as f:
            json.dump(stats_data, f, indent=2)
        
        return stats_file, json_file
    
    def save_dataset(self, dataset, folder_name="try6Dataset"):
        """Save the complete dataset in multiple formats"""
        # Save as JSON (human-readable)
        json_file = os.path.join(folder_name, 'data', 'dataset.json')
        with open(json_file, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        # Save as pickle (for Python use)
        pickle_file = os.path.join(folder_name, 'data', 'dataset.pkl')
        with open(pickle_file, 'wb') as f:
            pickle.dump(dataset, f)
        
        # Save as CSV-like format for easy reading
        csv_file = os.path.join(folder_name, 'data', 'dataset_summary.csv')
        with open(csv_file, 'w') as f:
            f.write("pair_id,num_cubes,is_same,structure1,structure2\n")
            for pair in dataset:
                struct1_str = ";".join([f"{x},{y},{z}" for x, y, z in pair['structure1']])
                struct2_str = ";".join([f"{x},{y},{z}" for x, y, z in pair['structure2']])
                f.write(f"{pair['pair_id']},{pair['num_cubes']},{pair['is_same']},\"{struct1_str}\",\"{struct2_str}\"\n")
        
        return json_file, pickle_file, csv_file

# Example usage and demonstration
def main():
    # Create generator
    generator = CubeStructureGenerator()
    
    # Create output folder
    folder_name = "try6Dataset"
    generator.create_output_folder(folder_name)
    print(f"Created output folder: {folder_name}")
    
    # Generate dataset
    print("Generating dataset...")
    dataset = generator.generate_dataset(
        num_pairs=50,           # Generate 50 pairs
        cube_counts=[3, 4, 5],  # Mix of 3, 4, and 5 cube structures
        same_ratio=0.5          # 50% same, 50% different
    )
    
    # Save dataset in multiple formats
    print("Saving dataset...")
    json_file, pickle_file, csv_file = generator.save_dataset(dataset, folder_name)
    print(f"Dataset saved as:")
    print(f"  JSON: {json_file}")
    print(f"  Pickle: {pickle_file}")
    print(f"  CSV: {csv_file}")
    
    # Save statistics
    stats_txt, stats_json = generator.save_dataset_stats(dataset, folder_name)
    print(f"Statistics saved as:")
    print(f"  Text: {stats_txt}")
    print(f"  JSON: {stats_json}")
    
    # Save all visualizations
    vis_files = generator.save_all_visualizations(dataset, folder_name)
    print(f"Saved {len(vis_files)} visualization files")
    
    # Create a summary file
    summary_file = os.path.join(folder_name, "README.txt")
    with open(summary_file, 'w') as f:
        f.write("Cube Structure Dataset - try6Dataset\n")
        f.write("====================================\n\n")
        f.write(f"This folder contains a generated dataset of {len(dataset)} cube structure pairs.\n\n")
        f.write("Folder Structure:\n")
        f.write("- data/: Contains the dataset in multiple formats\n")
        f.write("  - dataset.json: Human-readable JSON format\n")
        f.write("  - dataset.pkl: Python pickle format for easy loading\n")
        f.write("  - dataset_summary.csv: CSV format for spreadsheet use\n\n")
        f.write("- visualizations/: PNG images of all cube pairs\n")
        f.write("  - Files named as: pair_XXX_YYYcubes_same/diff.png\n\n")
        f.write("- stats/: Dataset statistics\n")
        f.write("  - dataset_stats.txt: Human-readable statistics\n")
        f.write("  - dataset_stats.json: Machine-readable statistics\n\n")
        f.write("Dataset Properties:\n")
        same_count = sum(1 for pair in dataset if pair['is_same'])
        f.write(f"- Total pairs: {len(dataset)}\n")
        f.write(f"- Same pairs: {same_count} ({same_count/len(dataset)*100:.1f}%)\n")
        f.write(f"- Different pairs: {len(dataset)-same_count} ({(len(dataset)-same_count)/len(dataset)*100:.1f}%)\n")
        f.write("- All cube structures are connected (consecutive)\n")
        f.write("- Each pair has equal number of cubes in both structures\n")
        
        cube_counts = set(pair['num_cubes'] for pair in dataset)
        f.write(f"- Cube counts: {sorted(cube_counts)}\n")
    
    print(f"Summary saved to: {summary_file}")
    
    # Display summary
    print(f"\nDataset Summary:")
    print(f"Generated {len(dataset)} pairs with 50% same/different ratio")
    print(f"All files saved to '{folder_name}' folder")
    
    # Show first few pairs info
    print("\nFirst 5 pairs preview:")
    for i in range(min(5, len(dataset))):
        pair = dataset[i]
        same_text = "SAME" if pair['is_same'] else "DIFFERENT"
        print(f"  Pair {pair['pair_id']}: {pair['num_cubes']} cubes, {same_text}")
    
    return dataset, generator, folder_name

# Function to load saved dataset
def load_dataset(folder_name="try6Dataset"):
    """Load a previously saved dataset"""
    pickle_file = os.path.join(folder_name, 'data', 'dataset.pkl')
    
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as f:
            dataset = pickle.load(f)
        print(f"Loaded {len(dataset)} pairs from {pickle_file}")
        return dataset
    else:
        print(f"Dataset file not found: {pickle_file}")
        return None

# Run the example
if __name__ == "__main__":
    dataset, generator, folder_name = main()
    
    print(f"\n{'='*50}")
    print("DATASET GENERATION COMPLETE!")
    print(f"{'='*50}")
    print(f"All files saved to: {os.path.abspath(folder_name)}")
    print("\nTo load this dataset later, use:")
    print("dataset = load_dataset('try6Dataset')")