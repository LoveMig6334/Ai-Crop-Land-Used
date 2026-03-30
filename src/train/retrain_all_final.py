"""Re-train RW-LSTM with validated window sizes and evaluate on test year.

Reads the window selection results from sweep_rwlstm_window.py, then:
1. For each crop, uses the selected window size
2. Trains rolling-window 3-layer LSTM on train+val data (up to val_year)
3. Predicts the test year and computes final metrics
4. Saves forecasts and error metrics to LSTM-3L output dirs
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from util.config import CFG
from util.data_path import (
    LSTM_3L_err,
    LSTM_3L_for,
    weights_path,
    cassava_long,
    corn_long,
    green_bean_long,
    soybean_long,
)
from util.lstm_model import LSTMRegressor
from util.output_io import save_error_csv, save_forecast_csv, save_summary_csv
from util.seq_dataset import SeqDataset

SEED = CFG["random_seed"]
SEQ_LEN = CFG["data"]["seq_len"]
PRED_LEN = CFG["data"]["pred_len"]
EPOCHS = 300
LR = 1e-2
HIDDEN = 32
LAYERS = 3

VAL_YEAR = CFG.get("val_year", 2023)
TEST_YEAR = CFG.get("test_year", 2024)
FIRST_TRAIN_START = 2004

ALL_CROPS = {
    "cassava": cassava_long,
    "corn": corn_long,
    "green_bean": green_bean_long,
    "soybean": soybean_long,
}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_selected_windows() -> dict[str, int]:
    """Load best window sizes from the validation sweep results."""
    csv_path = LSTM_3L_err / "window_selection_validation.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Window selection results not found at {csv_path}. "
            "Run sweep_rwlstm_window.py first."
        )
    df = pd.read_csv(csv_path)
    return dict(zip(df["crop"], df["best_window"].astype(int)))


def retrain_crop(crop_name: str, data_file: Path, window_size: int):
    """Retrain RW-LSTM for one crop with the validated window size."""
    long = pd.read_csv(data_file, index_col="date", parse_dates=True)[["price"]]
    test_actual = long[long.index.year == TEST_YEAR]["price"]

    torch.manual_seed(SEED)
    np.random.seed(SEED)

    # Rolling windows up to VAL_YEAR (train+val), predicting up to TEST_YEAR
    num_windows = TEST_YEAR - (FIRST_TRAIN_START + window_size - 1)

    all_window_info = []
    all_forecasts = []

    for window_idx in range(num_windows):
        train_start = FIRST_TRAIN_START + window_idx
        train_end = train_start + window_size - 1
        pred_year = train_end + 1

        train = long[
            (long.index.year >= train_start) & (long.index.year <= train_end)
        ][["price"]]
        future = long[long.index.year == pred_year][["price"]]

        if future.empty:
            continue

        scaler = MinMaxScaler()
        train_scaled = scaler.fit_transform(train).reshape(-1).astype(np.float32)

        ds = SeqDataset(train_scaled, seq_len=SEQ_LEN, pred_len=PRED_LEN)
        if len(ds) == 0:
            continue
        loader = DataLoader(ds, batch_size=len(ds), shuffle=True)

        model = LSTMRegressor(hidden=HIDDEN, layers=LAYERS, pred_len=PRED_LEN).to(device)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=LR)

        model.train()
        for _ in range(EPOCHS):
            for seq, targ in loader:
                seq, targ = seq.to(device), targ.to(device)
                pred = model(seq)
                loss = criterion(pred, targ)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        model.eval()
        last_seq = train_scaled[-SEQ_LEN:]
        with torch.no_grad():
            x = (
                torch.tensor(last_seq, dtype=torch.float32)
                .unsqueeze(0)
                .unsqueeze(-1)
                .to(device)
            )
            preds_scaled = model(x).cpu().numpy().reshape(-1)

        preds = scaler.inverse_transform(preds_scaled.reshape(-1, 1)).flatten()
        months = pd.date_range(f"{pred_year}-01-01", periods=PRED_LEN, freq="MS")
        forecast = pd.Series(preds, index=months, name="forecast_price")

        all_window_info.append({
            "window_idx": window_idx + 1,
            "train_start": train_start,
            "train_end": train_end,
            "pred_year": pred_year,
            "forecast": forecast,
        })
        all_forecasts.append(forecast)

        mae_w = mean_absolute_error(future["price"], forecast)
        print(
            f"  Window {window_idx + 1}/{num_windows}: "
            f"{train_start}-{train_end} -> {pred_year} | MAE: {mae_w:.4f}"
        )

    # Save the last window's forecast (TEST_YEAR)
    final_forecast = all_window_info[-1]["forecast"]
    save_forecast_csv(final_forecast, LSTM_3L_for, crop_name)

    # Save model weights from last window
    weights_path.mkdir(parents=True, exist_ok=True)
    weight_file = weights_path / f"lstm_3layer_{crop_name}.pth"
    # (model from last iteration is still in scope)
    torch.save(model.state_dict(), weight_file)

    # Compute test-year error metrics
    error = test_actual - final_forecast
    abs_error = error.abs()
    abs_pct_error = abs_error / test_actual * 100
    mae = mean_absolute_error(test_actual, final_forecast)
    mape = abs_pct_error.mean()
    accuracy = 100 - (mae / test_actual.mean() * 100)

    error_df = pd.DataFrame({
        "actual": test_actual,
        "forecast": final_forecast,
        "error": error,
        "abs_error": abs_error,
        "abs_pct_error": abs_pct_error,
    })
    save_error_csv(error_df, LSTM_3L_err, crop_name)
    save_summary_csv(
        {
            "crop": crop_name,
            "model": "LSTM-3L",
            "window_size": window_size,
            "mae": round(mae, 6),
            "mape": round(float(mape), 4),
            "accuracy_pct": round(accuracy, 2),
        },
        LSTM_3L_err,
        crop_name,
    )

    print(f"  FINAL: MAE={mae:.4f}, MAPE={mape:.2f}%, Accuracy={accuracy:.2f}%")
    return final_forecast, test_actual, mape, accuracy


def main():
    selected = load_selected_windows()
    print(f"Selected window sizes: {selected}")
    print(f"Test year: {TEST_YEAR}")
    print(f"Device: {device}")
    print()

    results = []
    for crop_name, data_file in ALL_CROPS.items():
        ws = selected[crop_name]
        print(f"{'=' * 50}")
        print(f"Crop: {crop_name} (window={ws}yr)")
        print(f"{'=' * 50}")
        _, _, mape, acc = retrain_crop(crop_name, data_file, ws)
        results.append({
            "crop": crop_name,
            "window_size": ws,
            "test_mape": round(float(mape), 2),
            "test_accuracy": round(acc, 2),
        })
        print()

    # Summary
    print("=" * 60)
    print("FINAL TEST RESULTS (RW-LSTM with validated window sizes)")
    print("=" * 60)
    df = pd.DataFrame(results)
    print(df.to_string(index=False))

    out_path = LSTM_3L_err / "final_test_results.csv"
    df.to_csv(out_path, index=False)
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
