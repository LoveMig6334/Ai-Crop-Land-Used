# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Crop Land-Use Analysis and Price Forecasting — a machine learning project for analyzing and
forecasting Thai agricultural commodity prices (cassava, corn, green beans, soybean) using LSTM,
Transformer, and ARIMA models.

## Commands

### Environment Setup
```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify PyTorch and GPU
python -c "import torch; print(torch.__version__); print('GPU:', torch.cuda.is_available())"
```

### Running Models
```bash
# Standard 1-year forecast notebooks
jupyter notebook "src/model1/(2) LSTM Model.ipynb"
jupyter notebook "src/model1/(2) Transformer Model.ipynb"
jupyter notebook "src/model1/(2) ARIMA Model.ipynb"

# 3-Layer rolling-window LSTM (core advanced model)
jupyter notebook "src/model_advanced/(4) LSTM 3 Layer.ipynb"

# Analysis / deliverable notebooks
jupyter notebook "src/Data Analytical.ipynb"
jupyter notebook "src/Error Analytical.ipynb"
jupyter notebook "src/Gantt chart.ipynb"
jupyter notebook "src/Overlap_price.ipynb"

# Training scripts (importable, scriptable)
python -m src.train.train_lstm --crop cassava
python -m src.train.train_transformer --crop corn
python -m src.train.train_arima --crop green_bean
```

## Architecture

### Data Pipeline
1. **Raw Data** (`data/raw/`) — Excel/CSV files with Thai Buddhist Era dates
2. **Preprocessing** (`src/data preparation/`) — Cleans data, handles Thai date formats
3. **Long-format data** (`data/long_format/`) — Primary input: `date, price` columns
4. **Model Output**:
   - Forecasts: `model/forecast_price/{MODEL_TYPE}/`
   - Error metrics: `model/error_record/{MODEL_TYPE}/`
   - Weights: `model/weights/`
   - Visualizations: `fig/` (centralized)

### Critical Path Management
**Always use `src/util/data_path.py` for file paths** — never hardcode paths.

```python
from src.util.data_path import cassava_long, LSTM_for, LSTM_5T_for, weights_path
from src.util.output_io import load_forecast_csv, save_forecast_csv
df = pd.read_csv(cassava_long, index_col="date", parse_dates=True)[["price"]]
```

Key path variables:
- `cassava_long`, `corn_long`, `green_bean_long`, `soybean_long` — long-format CSVs (primary input)
- `cassava_price_avg`, `corn_price_avg`, `green_bean_price_avg`, `soybean_price_avg` — wide-format legacy CSVs
- `LSTM_for`, `Transformer_for`, `ARIMA_for` — standard forecast output directories
- `LSTM_5T_for`, `LSTM_5T_err` — rolling-window (3-Layer LSTM) forecast/error directories
- `LSTM_err`, `Transformer_err`, `ARIMA_err` — standard error metrics directories
- `weights_path` — `model/weights/` (saved `.pth` files)
- `fig_root` — `fig/` (centralized figure root)
- `fig_model_forecast` — `fig/model/forecast/` (per-model forecast plots)
- `fig_model_error` — `fig/model/error/` (per-model error plots; `views/` for cross-model comparisons)
- `fig_analysis_image` — `fig/analysis/image/` (analytical charts; also aliased as `figs_path`)
- `fig_analysis_trans` — `fig/analysis/transitions/` (GIF animations)
- `fig_analysis_trends` — `fig/analysis/trends/` (long-term trend plots)
- `fig_analysis_overlap` — `fig/analysis/overlap/` (normalized price overlap)
- `fig_final_lstm3` — `fig/final/lstm-3layer/` (3-layer LSTM per-crop forecasts)
- `fig_final_gantt` — `fig/final/gantt chart/` (Gantt schedule charts)
- `reports_path` — `reports/` (project root; per-crop Markdown summaries + `crop_analysis_index.csv`)

### Output Helpers (`src/util/output_io.py`)
- `save_forecast_csv(forecast, dir, crop_name)` → `{dir}/{crop_name}_forecast.csv`
- `load_forecast_csv(dir, crop_name)` → DataFrame with DatetimeIndex, `forecast_price` column
- `save_error_csv(error_df, dir, crop_name)` → `{dir}/{crop_name}_error_metrics.csv`
- `save_summary_csv(metrics_dict, dir, crop_name)` → `{dir}/{crop_name}_summary.csv`

### Config (`src/util/config.py`)
```python
from src.util.config import CFG
# CFG["data"]["seq_len"]   → 12
# CFG["data"]["pred_len"]  → 12
# CFG["random_seed"]       → 42
# CFG["lstm"]["epochs"]    → 300
# CFG["train_cutoff_year"] → 2023
```

### Model Classes
- `src/util/lstm_model.py` — `LSTMRegressor(hidden, layers, pred_len)` (supports 2 or 3 layers)
- `src/util/transformer_model.py` — `TransformerRegressor` (self-attention with positional encoding)
- `src/util/seq_dataset.py` — `SeqDataset(data, seq_len=12, pred_len=12)` used by all models

Both LSTM and Transformer use `seq_len=12` (input) and `pred_len=12` (output) with MinMaxScaler.

### Directory Structure
```
src/
  model1/            Standard 1-year LSTM / Transformer / ARIMA notebooks
  model_advanced/    Rolling-window 3-layer LSTM (core model, feeds Gantt/Overlap)
  train/             Importable training scripts (train_lstm.py, train_transformer.py, train_arima.py)
  util/              Shared utilities
    data_path.py     All path variables
    config.py        CFG dict from config.yaml
    output_io.py     save/load forecast & error CSVs
    lstm_model.py    LSTMRegressor
    transformer_model.py  TransformerRegressor
    seq_dataset.py   SeqDataset
    data_utils.py    load_and_prepare(data_file) → (train, future, series, scaler, long)
  tools/             Diagnostic utilities (gil_test.py, machine_check.py)
  data preparation/  Data cleaning scripts
reports/             Analysis reports (Markdown / CSV) — per-crop summaries + crop_analysis_index.csv
fig/
  model/
    forecast/        Per-model forecast plots (LSTM/, ARIMA/, Transformer/)
    error/           Per-model error plots; views/ for cross-model comparisons
  analysis/
    image/           Analytical charts per crop + combined
    transitions/     GIF price animations
    trends/          Long-term trend plots
    overlap/         Normalized price overlap chart
  final/
    lstm-3layer/     3-layer LSTM per-crop forecast figures
    gantt chart/     Gantt schedule charts (optimize.png, optimal.png)
```

## Data Format

### Primary (Long-format CSV)
```csv
date,price
2004-01-01,0.99
2004-02-01,0.95
...
```
- File: `data/long_format/{crop}/price_avg.csv`
- 252 rows per crop (2004-01-01 to 2024-12-01)
- Generated by `src/data preparation/migrate_to_long_format.py`

### Legacy (Wide-format CSV)
```csv
year,1,2,3,4,5,6,7,8,9,10,11,12
2547,0.99,0.95,...
```
- Columns 1–12 = months; years in BE (subtract 543 for CE)
- Kept for backward compatibility; use long-format for new code

## Key Dependencies

- PyTorch 2.7+ (CUDA 12.6 for GPU)
- pandas, numpy, matplotlib
- scikit-learn (MinMaxScaler)
- statsmodels, statsforecast (ARIMA)
- Flask (web interface)
- pyyaml (config loading)
