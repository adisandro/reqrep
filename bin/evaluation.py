#!/usr/bin/env python3
import subprocess

if __name__ == "__main__":
    for n in range(10):
        subprocess.Popen(["python3", "bin/main.py", "data/case_studies/CC", "CC1", "-s", f"_{n}"])
