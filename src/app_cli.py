import logging
import os
import sys
from pathlib import Path

# Add the parent directory (src) to the Python path to enable utils imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import ensure_directory_exists, get_log_dir, get_timestamp_string


def setup_log() -> dict:
    log_dir = get_log_dir()
    ensure_directory_exists(log_dir)

    time_stamp = get_timestamp_string()
    log_file = os.path.join(log_dir, f"log_{time_stamp}.log")

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)

    root_logger.info(f"Logging setup complete. Log file: {log_file}")

    return {"log_dir": log_dir, "log_file": log_file, "root_logger": root_logger}


def main() -> None:
    setup_log()

    while True:
        ...


if __name__ == "__main__":
    main()
