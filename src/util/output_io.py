"""
CSV-based output helpers for forecast and error data.

Replaces the custom plain-text format that required parse_loc.py.
"""
from pathlib import Path

import pandas as pd


def save_forecast_csv(forecast: pd.Series, output_dir: Path, crop_name: str) -> Path:
    """Save a 12-month forecast Series to CSV.

    Output: {output_dir}/{crop_name}_forecast.csv
    Columns: date, forecast_price
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{crop_name}_forecast.csv"
    df = forecast.rename("forecast_price").rename_axis("date").reset_index()
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df.to_csv(path, index=False)
    print(f"Forecast saved to: {path}")
    return path


def load_forecast_csv(output_dir: Path, crop_name: str) -> pd.DataFrame:
    """Load a previously saved forecast CSV."""
    path = Path(output_dir) / f"{crop_name}_forecast.csv"
    return pd.read_csv(path, parse_dates=["date"], index_col="date")


def save_error_csv(error_df: pd.DataFrame, output_dir: Path, crop_name: str) -> Path:
    """Save the monthly error table to CSV.

    Output: {output_dir}/{crop_name}_error_metrics.csv
    Columns: date, actual, forecast, error, abs_error, abs_pct_error
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{crop_name}_error_metrics.csv"
    out = error_df[["actual", "forecast", "error", "abs_error", "abs_pct_error"]].copy()
    out.index = pd.DatetimeIndex(out.index).strftime("%Y-%m-%d")
    out.index.name = "date"
    out.to_csv(path)
    print(f"Error metrics saved to: {path}")
    return path


def save_summary_csv(metrics: dict, output_dir: Path, crop_name: str) -> Path:
    """Save key-value summary metrics to CSV.

    Output: {output_dir}/{crop_name}_summary.csv
    Columns: metric, value
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{crop_name}_summary.csv"
    pd.DataFrame(list(metrics.items()), columns=["metric", "value"]).to_csv(
        path, index=False
    )
    print(f"Summary saved to: {path}")
    return path
