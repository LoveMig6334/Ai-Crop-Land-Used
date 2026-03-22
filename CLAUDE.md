# CLAUDE.md

## Project Overview

ML project forecasting Thai agricultural commodity prices (cassava, corn, green beans, soybean)
using LSTM, Transformer, and ARIMA models.

## Commands

```bash
# Activate venv (Windows)
.venv\Scripts\activate

# Verify PyTorch / GPU
python -c "import torch; print(torch.__version__); print('GPU:', torch.cuda.is_available())"

# Model notebooks
jupyter notebook "src/model1/(2) LSTM Model.ipynb"
jupyter notebook "src/model1/(2) Transformer Model.ipynb"
jupyter notebook "src/model1/(2) ARIMA Model.ipynb"
jupyter notebook "src/model_advanced/(4) LSTM 3 Layer.ipynb"

# Analysis notebooks
jupyter notebook "src/Data Analytical.ipynb"
jupyter notebook "src/Data Analytical Trends.ipynb"
jupyter notebook "src/Error Analytical.ipynb"
jupyter notebook "src/Gantt chart.ipynb"
jupyter notebook "src/Overlap_price.ipynb"

# Training scripts
python -m src.train.train_lstm --crop cassava
python -m src.train.train_transformer --crop corn
python -m src.train.train_arima --crop green_bean
```

## Architecture

### Data Pipeline
1. **Raw** (`data/raw/`) — Excel/CSV with Thai Buddhist Era dates
2. **Preprocessing** (`src/data preparation/`) — cleans data, converts Thai dates
3. **Long-format** (`data/long_format/`) — primary input: `date, price`
4. **Output** — forecasts: `model/forecast_price/`, errors: `model/error_record/`, weights: `model/weights/`, figures: `fig/`

### Critical Path Management
**Always use `src/util/data_path.py`** — never hardcode paths.

```python
from src.util.data_path import cassava_long, LSTM_for, reports_path
from src.util.output_io import load_forecast_csv, save_forecast_csv
df = pd.read_csv(cassava_long, index_col="date", parse_dates=True)[["price"]]
```

### Key Path Variables
- `cassava_long`, `corn_long`, `green_bean_long`, `soybean_long` — long-format CSVs (primary)
- `LSTM_for`, `Transformer_for`, `ARIMA_for` — forecast output dirs
- `LSTM_err`, `Transformer_err`, `ARIMA_err` — error metrics dirs
- `LSTM_3L_for`, `LSTM_3L_err` — rolling-window 3-Layer LSTM forecast/error dirs
- `weights_path` — `model/weights/`
- `fig_root` — `fig/`
- `fig_model_forecast` — `fig/model/forecast/`
- `fig_model_error` — `fig/model/error/` (`views/` for cross-model comparisons)
- `fig_analysis_image` / `figs_path` — `fig/analysis/image/`
- `fig_analysis_trans` — `fig/analysis/transitions/`
- `fig_analysis_trends` — `fig/analysis/trends/`
- `fig_analysis_overlap` — `fig/analysis/overlap/`
- `fig_final_lstm3` — `fig/final/lstm-3layer/`
- `fig_final_gantt` — `fig/final/gantt chart/`
- `reports_path` — `reports/` (per-crop `.md` summaries + `crop_analysis_index.csv`)

### Output Helpers (`src/util/output_io.py`)
- `save_forecast_csv(forecast, dir, crop_name)` → `{dir}/{crop_name}_forecast.csv`
- `load_forecast_csv(dir, crop_name)` → DataFrame, DatetimeIndex, `forecast_price` column
- `save_error_csv(error_df, dir, crop_name)` → `{dir}/{crop_name}_error_metrics.csv`
- `save_summary_csv(metrics_dict, dir, crop_name)` → `{dir}/{crop_name}_summary.csv`

### Config (`src/util/config.py`)
```python
from src.util.config import CFG
# seq_len=12, pred_len=12, random_seed=42, lstm.epochs=300, train_cutoff_year=2023
```

### Model Classes
- `src/util/lstm_model.py` — `LSTMRegressor(hidden, layers, pred_len)` (2 or 3 layers)
- `src/util/transformer_model.py` — `TransformerRegressor` (self-attention + positional encoding)
- `src/util/seq_dataset.py` — `SeqDataset(data, seq_len=12, pred_len=12)` — used by all models
- Both LSTM and Transformer use MinMaxScaler, `seq_len=12`, `pred_len=12`.

### Directory Structure
```
src/
  model1/           Standard 1-year LSTM / Transformer / ARIMA notebooks
  model_advanced/   Rolling-window 3-layer LSTM (feeds Gantt/Overlap)
  train/            train_lstm.py, train_transformer.py, train_arima.py
  util/             data_path.py, config.py, output_io.py, lstm_model.py,
                    transformer_model.py, seq_dataset.py, data_utils.py
  tools/            gil_test.py, machine_check.py
  data preparation/ Data cleaning scripts
reports/            Per-crop .md summaries + crop_analysis_index.csv
fig/
  model/forecast/   Per-model forecast plots
  model/error/      Per-model error plots; views/ for cross-model
  analysis/image/   Analytical charts
  analysis/transitions/  GIF animations
  analysis/trends/  Long-term trend plots
  analysis/overlap/ Normalized price overlap
  final/lstm-3layer/     3-layer LSTM forecasts
  final/gantt chart/     Gantt charts
```

## Data Format

- **Primary (long-format):** `data/long_format/{crop}/price_avg.csv`, columns `date, price`
  — 252 rows per crop (2004-01-01 to 2024-12-01)
- **Legacy (wide-format):** columns `year`, `1`–`12`; years in BE (subtract 543 for CE)
  — kept for backward compatibility; use long-format for new code

## Key Dependencies

- PyTorch 2.7+ (CUDA 12.6), pandas, numpy, matplotlib, scikit-learn
- statsmodels, statsforecast (ARIMA), Flask (web interface), pyyaml
