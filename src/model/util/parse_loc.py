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
