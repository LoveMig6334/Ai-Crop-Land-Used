import datetime
import os
from pathlib import Path


def get_log_dir() -> Path:
    log_dir = Path(__file__).parent.parent.parent / "logs"
    return log_dir


def get_timestamp_string() -> str:
    """Get a timestamp string for filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_directory_exists(directory_path) -> str:
    """Ensure a directory exists, create it if it doesn't"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path
