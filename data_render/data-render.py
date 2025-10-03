import argparse
import tailer
import csv

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates images of cubes given a dataset.")
    parser.add_argument('-s', '--sample-amount', type=float, default="0.33", help="The % of data that is converted into image. Defaults to 0.33%")
    
    args = parser.parse_args()
    sample_amount = args.sample_amount
    
    print("Opening dataset...")
    try:
        with open("../data_generate/paired_cubes.csv", "r") as dataset:
            print("Opened dataset successfully!")
            last_row = 
            print(f"Number of rows in the CSV file: {row_count}")
    except FileNotFoundError:
        print("File not found! Please make sure you generate a dataset with data_generate/data-generate.py")