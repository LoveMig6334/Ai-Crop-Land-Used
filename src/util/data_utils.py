"""Shared data preparation utilities for model training."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from util.config import CFG


def load_and_prepare(data_file: Path) -> tuple:
    """Load long-format CSV and prepare train/test splits.

    Reads a long CSV (columns: date, price) produced by migrate_to_long_format.py,
    splits on CFG["train_cutoff_year"], and scales with MinMaxScaler.

    Returns:
        train  : DataFrame, columns ['price', 'scaled'], DatetimeIndex
        future : DataFrame, column  ['price'], DatetimeIndex (cutoff+1 year)
        series : np.ndarray float32 (scaled train prices)
        scaler : fitted MinMaxScaler
        long   : full long-format DataFrame (all years, column 'price')
    """
    cutoff = CFG["train_cutoff_year"]

    long = pd.read_csv(data_file, index_col="date", parse_dates=True)[["price"]]
    assert isinstance(long.index, pd.DatetimeIndex)

    train = long[long.index.year <= cutoff]["price"].to_frame()
    future = long[long.index.year == cutoff + 1]["price"].to_frame()

    scaler = MinMaxScaler()
    train["scaled"] = scaler.fit_transform(train[["price"]])
    series = train["scaled"].values.astype(np.float32)

    return train, future, series, scaler, long
