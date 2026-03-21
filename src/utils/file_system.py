import os
from datetime import datetime

def get_safe_filename(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]

def create_output_dir(playlist_name: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = f"out/{timestamp}_{playlist_name}"
    os.makedirs(path, exist_ok=True)
    return path