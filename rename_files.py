#!/usr/bin/env python3
import os
from pathlib import Path

data_dir = Path("./data")

for folder in data_dir.iterdir():
    if folder.is_dir():
        old_file = folder / "25-01-2026.html"
        new_file = folder / "26-01-2026.html"
        if old_file.exists():
            old_file.rename(new_file)
            print(f"Renamed: {old_file} -> {new_file}")
