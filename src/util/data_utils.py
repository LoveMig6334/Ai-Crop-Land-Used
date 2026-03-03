"""Shared data preparation utilities for model training."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from util.config import CFG


def load_and_prepare(data_file: Path) -> tuple:
    """Load wide-format CSV and prepare train/test splits.

    Reads a wide CSV with Buddhist Era years (columns: year, 1-12),
    melts to long format, converts BE → Gregorian dates, splits on
    CFG["train_cutoff_year"], and scales with MinMaxScaler.

    Returns:
        train  : DataFrame, columns ['price', 'scaled'], DatetimeIndex
        future : DataFrame, column  ['price'], DatetimeIndex (cutoff+1 year)
        series : np.ndarray float32 (scaled train prices)
        scaler : fitted MinMaxScaler
        long   : full long-format DataFrame (all years, column 'price')
    """
    cutoff = CFG["train_cutoff_year"]

    wide = pd.read_csv(data_file)
    long = wide.melt(id_vars="year", var_name="month", value_name="price").sort_values(
        ["year", "month"]
    )
    long["date"] = pd.to_datetime(
        (long["year"] - 543).astype(str)
        + "-"
        + long["month"].astype(str).str.zfill(2)
        + "-01"
    )
    long = long.set_index("date").sort_index()

    train = long[long.index.year <= cutoff]["price"].to_frame()
    future = long[long.index.year == cutoff + 1]["price"].to_frame()

    scaler = MinMaxScaler()
    train["scaled"] = scaler.fit_transform(train[["price"]])
    series = train["scaled"].values.astype(np.float32)

    return train, future, series, scaler, long
