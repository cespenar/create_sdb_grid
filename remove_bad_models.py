import glob
import os

if __name__ == "__main__":

    base_dir = 'logs'

    files_to_remove = [
        'custom_He0.01.data.GYRE',
        'custom_He0.001.data.GYRE',
        'custom_He0.0001.data.GYRE',
        'custom_start.data.GYRE',
        'custom_He0.01_summary.txt',
        'custom_He0.001_summary.txt',
        'custom_He0.0001_summary.txt',
        'custom_He0.01.data',
        'custom_He0.001.data',
        'custom_He0.0001.data',
        'custom_start.data',
    ]

    for log_dir in sorted(glob.glob(os.path.join(base_dir, 'logs_*'))):
        print(log_dir)
        for f_name in sorted(glob.glob(os.path.join(log_dir, '*'))):
            if os.path.basename(f_name) in files_to_remove:
                os.remove(f_name)
                print(f"{f_name} removed")
            