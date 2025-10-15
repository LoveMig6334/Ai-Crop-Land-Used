import pandas as pd


def parse_forecast_file(file_path):
    """
    Parse forecast file and extract date-price data
    """
    dates = []
    prices = []

    with open(file_path, "r") as file:
        lines = file.readlines()

        # Find the start of forecast data
        start_reading = False
        for line in lines:
            line = line.strip()

            if line == "Forecast Data:":
                start_reading = True
                continue

            if start_reading and line.startswith("----"):
                continue

            if start_reading and line.startswith("Overall Statistics:"):
                break

            if start_reading and ":" in line and line != "Forecast Data:":
                try:
                    date_str, price_str = line.split(": ")
                    dates.append(pd.to_datetime(date_str))
                    prices.append(float(price_str))
                except ValueError:
                    continue

    return dates, prices


def load_rolling_window_forecast(file_path):
    """
    Load forecasted data from rolling window forecast files.

    This function parses files with the format:
    - Window sections with "Training: YYYY-YYYY, Predicting: YYYY"
    - Date-price pairs in format "YYYY-MM-DD: price"
    - Window statistics and overall statistics

    Args:
        file_path (str): Path to the rolling window forecast file

    Returns:
        dict: Dictionary containing:
            - 'dates': List of datetime objects
            - 'prices': List of float prices
            - 'windows': List of window information dicts
            - 'overall_stats': Dictionary of overall statistics
    """
    dates = []
    prices = []
    windows = []
    overall_stats = {}

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    current_window = None
    reading_forecast_data = False
    reading_overall_stats = False

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Parse window header
        if "Training:" in line and "Predicting:" in line:
            # Extract window information
            parts = line.split(" - ")
            if len(parts) >= 2:
                window_info = parts[1]
                training_part = window_info.split(", ")[0].replace("Training: ", "")
                predicting_part = window_info.split(", ")[1].replace("Predicting: ", "")

                current_window = {
                    "training_period": training_part,
                    "predicting_year": predicting_part,
                    "dates": [],
                    "prices": [],
                }
            reading_forecast_data = True
            continue

        # Parse date-price pairs
        if (
            reading_forecast_data
            and ":" in line
            and not line.startswith("Window")
            and not line.startswith("Overall")
            and not line.startswith("----")
        ):
            try:
                # Handle lines like "2024-01-01: 3.16"
                # Split on the last colon to separate date from price
                if ": " in line:  # Make sure there's a colon followed by space
                    date_str, price_str = line.rsplit(": ", 1)
                    # Check if date_str looks like a date (contains hyphens)
                    if "-" in date_str:
                        date = pd.to_datetime(date_str)
                        price = float(price_str)

                        dates.append(date)
                        prices.append(price)

                        if current_window:
                            current_window["dates"].append(date)
                            current_window["prices"].append(price)

            except (ValueError, IndexError):
                continue

        # Parse window statistics
        if line.startswith("Window") and "Statistics:" in line:
            reading_forecast_data = False
            continue

        if current_window and line.startswith("Mean:"):
            try:
                # Parse "Mean: 2.82, Min: 2.58, Max: 3.19"
                stats_parts = line.split(", ")
                window_stats = {}
                for part in stats_parts:
                    key, value = part.split(": ")
                    window_stats[key.lower()] = float(value)

                current_window["statistics"] = window_stats
                windows.append(current_window)
                current_window = None
            except (ValueError, IndexError):
                continue

        # Parse overall statistics
        if line.startswith("Overall Consolidated Statistics:"):
            reading_overall_stats = True
            continue

        if reading_overall_stats and ":" in line:
            try:
                key, value = line.split(": ", 1)
                # Convert key to snake_case
                key = key.lower().replace(" ", "_")

                # Try to convert to appropriate type
                try:
                    if "." in value:
                        overall_stats[key] = float(value)
                    else:
                        overall_stats[key] = int(value)
                except ValueError:
                    overall_stats[key] = value

            except ValueError:
                continue

    return {
        "dates": dates,
        "prices": prices,
        "windows": windows,
        "overall_stats": overall_stats,
    }


def load_rolling_window_forecast_simple(file_path):
    """
    Simple function to load just dates and prices from rolling window forecast files.

    Args:
        file_path (str): Path to the rolling window forecast file

    Returns:
        tuple: (dates, prices) - Lists of datetime objects and float prices
    """
    result = load_rolling_window_forecast(file_path)
    return result["dates"], result["prices"]
