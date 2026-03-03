"""LSTM training and forecasting pipeline."""
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader

from util.config import CFG
from util.data_path import LSTM_err, LSTM_for, weights_path
from util.data_utils import load_and_prepare
from util.lstm_model import LSTMRegressor
from util.output_io import save_error_csv, save_forecast_csv, save_summary_csv
from util.seq_dataset import SeqDataset

SEED = CFG["random_seed"]


def train_and_forecast(
    data_file: Path, force_retrain: bool = False
) -> tuple[pd.Series, pd.Series, MinMaxScaler, pd.DataFrame]:
    """Full LSTM pipeline: load data, train (or load weights), infer, save outputs.

    Args:
        data_file:      Path to wide-format price CSV (e.g. cassava_price_avg).
        force_retrain:  If True, ignore cached weights and retrain from scratch.

    Returns:
        forecast : pd.Series, 12-month DatetimeIndex, name='forecast_price'
        actual   : pd.Series, 12-month DatetimeIndex (y_test in original scale)
        scaler   : fitted MinMaxScaler
        long     : full long-format DataFrame (all years, column 'price')
    """
    data_file = Path(data_file)
    crop_name = data_file.parent.name

    train, future, series, scaler, long = load_and_prepare(data_file)

    SEQ_LEN = CFG["data"]["seq_len"]
    PRED_LEN = CFG["data"]["pred_len"]

    ds = SeqDataset(series, SEQ_LEN, PRED_LEN)
    loader = DataLoader(ds, batch_size=len(ds))

    torch.manual_seed(SEED)
    np.random.seed(SEED)

    weights_path.mkdir(parents=True, exist_ok=True)
    weight_file = weights_path / f"lstm_{crop_name}.pth"

    model = LSTMRegressor()
    crit = nn.MSELoss()
    opt = torch.optim.Adam(model.parameters(), lr=CFG["lstm"]["learning_rate"])

    if weight_file.exists() and not force_retrain:
        model.load_state_dict(torch.load(weight_file, weights_only=True))
        print(f"Loaded weights from {weight_file.name}")
    else:
        EPOCHS = CFG["lstm"]["epochs"]
        for epoch in range(1, EPOCHS + 1):
            for seq, targ in loader:
                opt.zero_grad()
                pred = model(seq)
                loss = crit(pred, targ)
                loss.backward()
                opt.step()
            if epoch % 50 == 0:
                print(f"epoch {epoch:>3}/{EPOCHS}  loss={loss.item():.5f}")
        torch.save(model.state_dict(), weight_file)
        print(f"Saved weights to {weight_file.name}")

    # Inference
    model.eval()
    with torch.no_grad():
        window = (
            torch.tensor(series[-SEQ_LEN:], dtype=torch.float32)
            .unsqueeze(0)
            .unsqueeze(-1)
        )
        preds_scaled = model(window).squeeze(0).numpy()

    preds = scaler.inverse_transform(preds_scaled.reshape(-1, 1)).flatten()
    forecast_year = CFG["train_cutoff_year"] + 1
    forecast = pd.Series(
        preds,
        index=pd.date_range(f"{forecast_year}-01-01", periods=12, freq="MS"),
        name="forecast_price",
    )

    save_forecast_csv(forecast, LSTM_for, crop_name)

    # Error metrics
    actual = future["price"]
    error = actual - forecast
    abs_error = error.abs()
    abs_pct_error = abs_error / actual * 100
    mae = mean_absolute_error(actual, forecast)
    mape = abs_pct_error.mean()

    error_df = pd.DataFrame(
        {
            "actual": actual,
            "forecast": forecast,
            "error": error,
            "abs_error": abs_error,
            "abs_pct_error": abs_pct_error,
        }
    )
    save_error_csv(error_df, LSTM_err, crop_name)

    accuracy = 100 - (mae / actual.mean() * 100)
    summary = {
        "MAE": round(mae, 6),
        "MAPE": round(mape, 4),
        "accuracy_pct": round(accuracy, 2),
    }
    save_summary_csv(summary, LSTM_err, crop_name)

    return forecast, actual, scaler, long


if __name__ == "__main__":
    import argparse

    from util.data_path import (
        cassava_price_avg,
        corn_price_avg,
        green_bean_price_avg,
        soybean_price_avg,
    )

    crops = {
        "cassava": cassava_price_avg,
        "corn": corn_price_avg,
        "green_bean": green_bean_price_avg,
        "soybean": soybean_price_avg,
    }

    p = argparse.ArgumentParser(description="Train LSTM and forecast crop prices.")
    p.add_argument("--crop", default="cassava", choices=list(crops))
    p.add_argument("--force-retrain", action="store_true")
    args = p.parse_args()

    train_and_forecast(crops[args.crop], force_retrain=args.force_retrain)
