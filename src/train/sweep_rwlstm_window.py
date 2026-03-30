"""Sweep RW-LSTM window sizes on validation year to select best per crop.

For each crop x window_size combination, trains a rolling-window 3-layer LSTM
using data up to val_year-1, predicts val_year, and computes MAPE.
The window size with lowest validation MAPE is selected per crop.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader

# Ensure project root is on path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from util.config import CFG
from util.data_path import (
    LSTM_3L_err,
    cassava_long,
    corn_long,
    green_bean_long,
    soybean_long,
)
from util.lstm_model import LSTMRegressor
from util.seq_dataset import SeqDataset

SEED = CFG["random_seed"]
SEQ_LEN = CFG["data"]["seq_len"]
PRED_LEN = CFG["data"]["pred_len"]
EPOCHS = 300
LR = 1e-2
HIDDEN = 32
LAYERS = 3

VAL_YEAR = CFG.get("val_year", 2023)
FIRST_TRAIN_START = 2004
WINDOW_SIZES = [5, 6, 7, 8, 9, 10]

ALL_CROPS = {
    "cassava": cassava_long,
    "corn": corn_long,
    "green_bean": green_bean_long,
    "soybean": soybean_long,
}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def train_single_window(series: np.ndarray, pred_len: int) -> np.ndarray:
    """Train a 3-layer LSTM on one window and return scaled predictions."""
    ds = SeqDataset(series, seq_len=SEQ_LEN, pred_len=pred_len)
    if len(ds) == 0:
        return np.zeros(pred_len)
    loader = DataLoader(ds, batch_size=len(ds), shuffle=True)

    model = LSTMRegressor(hidden=HIDDEN, layers=LAYERS, pred_len=pred_len).to(device)
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
    last_seq = series[-SEQ_LEN:]
    with torch.no_grad():
        x = (
            torch.tensor(last_seq, dtype=torch.float32)
            .unsqueeze(0)
            .unsqueeze(-1)
            .to(device)
        )
        preds = model(x).cpu().numpy().reshape(-1)
    return preds


def sweep_crop(crop_name: str, data_file: Path) -> dict:
    """Sweep window sizes for one crop, return val MAPE per window size."""
    long = pd.read_csv(data_file, index_col="date", parse_dates=True)[["price"]]
    val_actual = long[long.index.year == VAL_YEAR]["price"]

    results = {}

    for ws in WINDOW_SIZES:
        torch.manual_seed(SEED)
        np.random.seed(SEED)

        # The last window for validation: trains on [VAL_YEAR-ws, VAL_YEAR-1], predicts VAL_YEAR
        train_start = VAL_YEAR - ws
        train_end = VAL_YEAR - 1

        if train_start < FIRST_TRAIN_START:
            print(f"  Window {ws}yr: train_start {train_start} < {FIRST_TRAIN_START}, skipping")
            results[ws] = float("nan")
            continue

        train = long[
            (long.index.year >= train_start) & (long.index.year <= train_end)
        ][["price"]]

        if len(train) < SEQ_LEN + PRED_LEN:
            print(f"  Window {ws}yr: insufficient training data ({len(train)} rows), skipping")
            results[ws] = float("nan")
            continue

        scaler = MinMaxScaler()
        train_scaled = scaler.fit_transform(train).reshape(-1).astype(np.float32)

        preds_scaled = train_single_window(train_scaled, PRED_LEN)
        preds = scaler.inverse_transform(preds_scaled.reshape(-1, 1)).flatten()

        forecast = pd.Series(
            preds,
            index=pd.date_range(f"{VAL_YEAR}-01-01", periods=PRED_LEN, freq="MS"),
            name="forecast_price",
        )

        abs_pct_error = (val_actual - forecast).abs() / val_actual * 100
        mape = abs_pct_error.mean()
        results[ws] = round(float(mape), 2)

        print(f"  Window {ws}yr: Val MAPE = {mape:.2f}%")

    return results


def main():
    print(f"Validation year: {VAL_YEAR}")
    print(f"Window sizes: {WINDOW_SIZES}")
    print(f"Device: {device}")
    print()

    all_results = {}

    for crop_name, data_file in ALL_CROPS.items():
        print(f"{'=' * 50}")
        print(f"Crop: {crop_name}")
        print(f"{'=' * 50}")
        all_results[crop_name] = sweep_crop(crop_name, data_file)
        print()

    # Build results table
    rows = []
    for crop_name, res in all_results.items():
        row = {"crop": crop_name}
        valid = {k: v for k, v in res.items() if not np.isnan(v)}
        for ws in WINDOW_SIZES:
            row[f"window_{ws}"] = res.get(ws, float("nan"))
        if valid:
            best_ws = min(valid, key=valid.get)
            row["best_window"] = best_ws
            row["best_mape"] = valid[best_ws]
        else:
            row["best_window"] = None
            row["best_mape"] = None
        rows.append(row)

    df = pd.DataFrame(rows)

    # Save results
    out_path = LSTM_3L_err / "window_selection_validation.csv"
    LSTM_3L_err.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\nResults saved to: {out_path}")

    # Print summary table
    print("\n" + "=" * 70)
    print("VALIDATION MAPE (%) BY WINDOW SIZE")
    print("=" * 70)
    header = f"{'Crop':<12}" + "".join(f"{ws}yr{'':>5}" for ws in WINDOW_SIZES) + "  Best"
    print(header)
    print("-" * 70)
    for _, row in df.iterrows():
        line = f"{row['crop']:<12}"
        for ws in WINDOW_SIZES:
            val = row[f"window_{ws}"]
            if np.isnan(val):
                line += f"{'N/A':>8}"
            else:
                bold = " *" if ws == row["best_window"] else "  "
                line += f"{val:>6.2f}{bold}"
            line += " "
        line += f"  {row['best_window']}yr"
        print(line)
    print("=" * 70)
    print("* = selected (lowest validation MAPE)")

    return df


if __name__ == "__main__":
    main()
