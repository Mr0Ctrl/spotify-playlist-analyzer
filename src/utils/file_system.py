import os
from datetime import datetime
from typing import Union, List

def get_safe_filename(path: Union[str, List[str]]) -> str:
    """
    Returns a safe filename from a path or list of paths.
    For multiple paths, combines them with underscores.
    """
    if isinstance(path, list):
        if len(path) == 1:
            return os.path.splitext(os.path.basename(path[0]))[0]
        else:
            # Combine multiple filenames
            names = [os.path.splitext(os.path.basename(p))[0] for p in path]
            # Take first 2-3 names to avoid too long filename
            if len(names) > 3:
                combined = "-".join(names[:3]) + f"_and_{len(names)-3}_more"
            else:
                combined = "_".join(names)
            return combined
    else:
        # Single path (file or directory)
        if os.path.isfile(path):
            return os.path.splitext(os.path.basename(path))[0]
        else:
            # Directory path
            return os.path.basename(path)

def create_output_dir(playlist_name: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = f"out/{timestamp}_{playlist_name}"
    os.makedirs(path, exist_ok=True)
    return path