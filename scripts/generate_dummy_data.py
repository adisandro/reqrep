import csv
import numpy as np
import os


def generate_csv_file(mconfigs, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    time_values = np.arange(0, 20.0, 0.1)
    for file_index, config in enumerate(mconfigs):
        mean = config['mean']
        std_dev = config['std_dev']
        filename = os.path.join(output_dir, f'dummy_{file_index:03d}.csv')
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time|s', 'x|s', 'y|m'])
            for t in time_values:
                y = np.random.normal(mean, std_dev)
                writer.writerow([round(t, 1), round(t, 1), y])

# Example usage:
configs = [
    {'mean': 10, 'std_dev': 2},
    {'mean': 12, 'std_dev': 3},
    {'mean': 8,  'std_dev': 1},
    {'mean': 15, 'std_dev': 4},
    {'mean': 9,  'std_dev': 2.5}
]

generate_csv_file(mconfigs=configs, output_dir='data/dummy')