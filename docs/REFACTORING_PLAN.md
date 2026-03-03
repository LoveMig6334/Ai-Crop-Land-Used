# Refactoring Plan: AI Crop Land-Use Forecasting Project

## Context

This project forecasts Thai agricultural commodity prices (cassava, corn, green beans, soybean) using LSTM, Transformer, and ARIMA models. The core functionality works but the codebase has accumulated several data science anti-patterns: duplicated utility classes, hardcoded hyperparameters, custom text-based output formats, no model persistence, training logic locked in notebooks, and a large flat `requirements.txt` with Windows-specific packages. This plan addresses all of them in a dependency-ordered sequence, keeping the project runnable after every phase.

---

## Phase 0 — Repository Hygiene
**Goal:** Stop tracking generated artifacts (outputs, images, raw binaries) in git.

**Files to modify:**
- `.gitignore` — Expand from 2 lines to cover:
  - `.venv/` (currently not ignored but the directory is large)
  - `model/weights/*.pth` (to be created in Phase 4)
  - `model/forecast_price/`, `model/error_record/` (regenerable outputs)
  - `src/image/`, `src/figs/`, `model/image/` (generated plots)
  - `data/raw/**/*.xls` (binary files; CSV equivalents exist)
  - `.ipynb_checkpoints/`

**Verification:** `git status` is clean after committing new `.gitignore`.

---

## Phase 1 — Consolidate Path Registry
**Goal:** Delete `src/data preparation/raw_data_path.py` — its paths overlap with and duplicate `src/util/data_path.py`. The raw paths file also has a broken `parent.parent.parent.parent` path calculation.

**Files to modify:**
- `src/util/data_path.py` — Add the `data/raw/` paths from `raw_data_path.py` to the bottom.
- `src/data preparation/raw_data_path.py` — Delete (or replace with a deprecation import shim).

**Verification:** `python -c "from src.util.data_path import cassava_raw_price_avg; print(cassava_raw_price_avg)"` prints the correct path.

---

## Phase 2 — Consolidate Model Utility Classes
**Goal:** Eliminate three duplicate `SeqDataset` definitions and the silent divergence between the two `LSTMRegressor` variants. This also fixes a training correctness bug.

### Current problem
| File | `LSTMRegressor` FC output | Effect |
|---|---|---|
| `lstm_cust_class.py` | `nn.Linear(hidden, 1)` | Single-step; notebook trains on `targ[:, 0]` only |
| `manystep_lstm_class.py` | `nn.Linear(hidden, pred_len)` | Multi-step direct; correct MSE over all 12 targets |
| `transformer_cust_class.py` | N/A | Has its own `SeqDataset` copy |

> **Note:** Fixing this bug will produce different LSTM model weights and slightly different accuracy metrics than currently saved. This is intentional — the current single-step training is incorrect for a 12-month direct forecast.

**Files to create:**
- `src/util/seq_dataset.py` — Single canonical `SeqDataset` (uses `torch.tensor(..., dtype=torch.float32)`)
- `src/util/lstm_model.py` — Single `LSTMRegressor(hidden=32, layers=2, pred_len=12)` with `nn.Linear(hidden, pred_len)`
- `src/util/transformer_model.py` — Clean copy of `TransformerRegressor` + `PositionalEncoding` from `transformer_cust_class.py`

**Files to replace with deprecation shims:**
- `src/util/lstm_cust_class.py` — Re-export from `lstm_model.py`
- `src/util/manystep_lstm_class.py` — Re-export from `lstm_model.py`
- `src/util/transformer_cust_class.py` — Re-export from `transformer_model.py`

**Notebooks to update:**
- `src/model1/(2) LSTM Model.ipynb` — Update imports; remove rolling-window inference loop; update training loss to `crit(pred, targ)` (not `targ[:, 0]`)
- `src/model1/(2) Transformer Model.ipynb` — Update imports only

**Verification:** Both model notebooks run end-to-end and produce a `forecast` Series of length 12 with no NaN values.

---

## Phase 3 — Introduce Config File for Hyperparameters
**Goal:** Replace all hardcoded hyperparameters across three notebooks with a single `config.yaml`.

### Hardcoded values to capture
| Param | LSTM | Transformer | ARIMA |
|---|---|---|---|
| `seq_len` / `pred_len` | 12 / 12 | 12 / 12 | 12 / 12 |
| `epochs` | 300 | 500 | N/A |
| `learning_rate` | 1e-2 | 1e-3 | N/A |
| `hidden` / `layers` | 32 / 2 | N/A | N/A |
| `d_model`, `nhead` | N/A | 64, 8 | N/A |
| `random_seed` | None | None | None |
| `train_cutoff_year` | 2023 | 2023 | 2023 |

**Files to create:**
- `config.yaml` (project root) — All hyperparameters + `random_seed: 42`
- `src/util/config.py` — Loader that provides a `CFG` dict singleton: `from util.config import CFG`

**Notebooks to update:** All three `src/model1/` notebooks — replace literal values with `CFG["lstm"]["hidden"]` etc.

**Verification:** Change `epochs: 10` in `config.yaml`, run a notebook, confirm training stops at 10.

---

## Phase 4 — Random Seeds and Model Persistence
**Goal:** Make training fully deterministic and save weights so notebooks don't require a full retrain on every open.

**Files to modify:**
- `config.yaml` — Add `paths.weights_dir: model/weights`
- `src/util/data_path.py` — Add `weights_path = project_root / "model" / "weights"`
- All three `src/model1/` notebooks — Add seed calls before model init; add save/load block:
  ```python
  # Set seeds
  torch.manual_seed(SEED); np.random.seed(SEED)

  # Save or load
  if weight_file.exists():
      model.load_state_dict(torch.load(weight_file, weights_only=True))
  else:
      # ... train ...
      torch.save(model.state_dict(), weight_file)
  ```

**Verification:** Run a notebook twice. Second run prints "Loaded weights" and produces identical forecasts.

---

## Phase 5 — Migrate Output Format from .txt to CSV
**Goal:** Replace the custom plain-text forecast/error format (requiring the fragile `parse_loc.py` parser) with standard CSVs loadable with `pd.read_csv()`.

### New formats
**`model/forecast_price/LSTM/cassava_forecast.csv`:**
```
date,forecast_price
2024-01-01,3.51
...
```
**`model/error_record/LSTM/cassava_error_metrics.csv`:** Monthly error table with columns `date, actual, forecast, error, abs_error, abs_pct_error`

**`model/error_record/LSTM/cassava_summary.csv`:** Key-value pairs (MAE, MAPE, accuracy_pct, etc.)

**Files to create:**
- `src/util/output_io.py` — `save_forecast_csv()`, `load_forecast_csv()`, `save_error_csv()` functions

**Files to modify:**
- All three `src/model1/` notebooks — Replace `with open(..., "w") as f: f.write(...)` blocks with `save_forecast_csv(...)` / `save_error_csv(...)` calls
- `src/Error Analytical.ipynb` — Update to use `load_forecast_csv()` instead of `parse_loc`

**Files to deprecate (delete in Phase 9):**
- `src/util/parse_loc.py` — Add deprecation comment; keep until all consumers are migrated

**Verification:** `pd.read_csv("model/forecast_price/LSTM/cassava_forecast.csv", ...)` returns a clean 12-row DataFrame. `parse_loc.py` is no longer imported anywhere.

---

## Phase 6 — Extract Training Logic to .py Scripts
**Goal:** Move the train/predict/evaluate logic out of notebook cells into importable Python scripts. Notebooks become thin orchestrators (import + visualize).

**Dependency:** Phases 2, 3, 4, 5 must be complete.

**Files to create:**
- `src/train/__init__.py`
- `src/train/train_lstm.py` — `train_and_forecast(data_file, force_retrain=False) -> (forecast, actual, scaler)`. Contains: data loading + melt, scaling, SeqDataset, training loop, weight save/load, forecast generation, CSV output.
- `src/train/train_transformer.py` — Same pattern for `TransformerRegressor`
- `src/train/train_arima.py` — Same pattern for `AutoARIMA`; saves selected model order to a JSON sidecar for reproducibility (no `.pth` needed)

**Notebooks after refactor (`src/model1/` all three):**
```python
# Cell 1: imports + config
from util.data_path import cassava_price_avg as data_file
from train.train_lstm import train_and_forecast

# Cell 2: run
forecast, actual, scaler = train_and_forecast(data_file)

# Remaining cells: visualization only
```

**Verification:** `python -m src.train.train_lstm` runs end-to-end without Jupyter. Output CSV matches notebook output.

---

## Phase 7 — Long-Format Data Migration
**Goal:** Convert the wide-format CSVs (year as row, months as columns, Buddhist Era years) to standard long-format CSVs (`date`, `price`, Gregorian dates). Eliminates the `melt` + BE conversion boilerplate from all train scripts.

**Dependency:** Phase 6 complete (train scripts centralize the melt logic before we remove it).

**Files to create:**
- `src/data preparation/migrate_to_long_format.py` — One-time migration script. Reads from `data/fix_year/` (already CE years), melts to long format, writes to `data/long_format/{crop}/price_avg.csv`.
- `data/long_format/` directory (4 crop CSVs, each ~252 rows: 21 years × 12 months)

**Files to modify:**
- `src/util/data_path.py` — Add `cassava_long`, `corn_long`, `green_bean_long`, `soybean_long` pointing to `data/long_format/`
- `src/train/train_lstm.py` (and transformer/arima) — Replace 8-line melt/date block with single `pd.read_csv(data_file, index_col="date", parse_dates=True)`

**Old wide-format files kept** in `data/data_processed/` and `data/fix_year/` — do not delete until all consumers confirmed updated.

**Verification:** `pd.read_csv(cassava_long, index_col="date", parse_dates=True)` returns 252 rows, `2004-01-01` to `2024-12-01`, single `price` column.

---

## Phase 8 — Dependency Management Cleanup
**Goal:** Replace the 144-entry flat `requirements.txt` (with Windows-only packages) with a minimal split.

**Files to create:**
- `requirements-core.txt` — Direct ML dependencies only (torch, numpy, pandas, scikit-learn, statsforecast, statsmodels, matplotlib, pyyaml, flask)
- `requirements-dev.txt` — `-r requirements-core.txt` + jupyter, jupyterlab, ipywidgets

**Files to modify:**
- `requirements.txt` — Replace with comment + `-r requirements-dev.txt` pointer + PyTorch CUDA install instructions

**Note:** `pywin32` and `pywinpty` removed from tracked deps (Windows-only; Jupyter installs them automatically on Windows).

**Verification:** `pip install -r requirements-core.txt` completes on a CPU-only Linux machine (with CPU PyTorch variant manually installed).

---

## Phase 9 — Remove Dead Code and Root-Level Clutter
**Goal:** Final cleanup after all other phases are stable.

**Files to delete:**
- `src/model2 (notuse)/` — Entire directory (3 deprecated 5-year experiment notebooks)
- `src/util/parse_loc.py` — No longer imported after Phase 5
- `src/data preparation/raw_data_path.py` — Already replaced in Phase 1
- Old `.txt` forecast/error files (already excluded from git by Phase 0 `.gitignore`; delete from working tree)

**Files to check and possibly delete (confirm first):**
- `src/(3) LSTM Model.ipynb` — Appears to be a draft; confirm it duplicates model1 content
- `src/(4) LSTM 3 Layer.ipynb` — Same

**Files to move:**
- `GIL-TEST.py` → `src/tools/gil_test.py`
- `machine_pre.py` → `src/tools/machine_check.py`

**Files to update:**
- `CLAUDE.md` — Update commands and directory structure sections

**Verification:** `git status` is clean. Project tree matches documented structure in `CLAUDE.md`.

---

## Phase 0b — Move `figs/` to Project Root

**Goal:** Relocate `src/figs/` to the project root so all generated output directories (`model/`, `figs/`, `data/`) live at the top level rather than scattered inside `src/`. Also fixes the path-level inconsistency where notebooks construct relative paths that break if Jupyter is launched from a directory other than `src/`.

**Dependency:** Can be done standalone, before or after Phase 0. If Phase 0 runs first, set the `.gitignore` entry to `figs/` (root) instead of `src/figs/`.

### Why `./figs/` is fragile

`src/Data Analytical Trends.ipynb` constructs all save paths as `./figs/…` (relative strings). This resolves correctly only when the Jupyter kernel's working directory is `src/`. If the notebook is opened from the project root (e.g., `jupyter notebook` run at root), every `plt.savefig()` silently writes to a `figs/` folder at the root while the creation check looks in `src/figs/` — or raises `FileNotFoundError`. Using absolute paths from `data_path.py` eliminates this entirely.

### Files to modify

**`src/util/data_path.py`** — Add one line after `model_save`:
```python
figs_path = project_root / "figs"
```
This gives all consumers an absolute `Path` object that is correct regardless of working directory.

**`src/Data Analytical Trends.ipynb`** — Three categories of changes:

1. **Import block** (add to the first code cell, or create a new cell before `create_directories`):
   ```python
   import sys
   from pathlib import Path
   # Ensure util package is importable when kernel CWD is src/ or project root
   _src = Path(__file__).parent if "__file__" in dir() else Path().resolve()
   if str(_src) not in sys.path:
       sys.path.insert(0, str(_src))
   from util.data_path import figs_path
   ```
   > Note: Jupyter notebooks do not have `__file__`. The fallback `Path().resolve()` is the kernel CWD. Because the notebook lives in `src/`, and Jupyter is normally launched from `src/`, this resolves correctly. The import of `util.data_path` then uses `__file__` internally, giving the true absolute path.

2. **`create_directories()` / `create_crop_directories()` calls** (cells 5 and 19):
   ```python
   # BEFORE
   directories = ["./figs", "./reports"]

   # AFTER
   directories = [figs_path, Path("./reports")]
   ```

3. **All `fig_path` assignments** (cells 8 and 19 — 10 total `savefig` calls):
   ```python
   # BEFORE
   fig_path = f"./figs/{basename}_monthly_trend.png"

   # AFTER
   fig_path = figs_path / f"{basename}_monthly_trend.png"
   ```
   ```python
   # BEFORE (crop-level)
   crop_figs_dir = Path(f"./figs/{crop_name}")

   # AFTER
   crop_figs_dir = figs_path / crop_name
   ```
   `plt.savefig()` accepts `pathlib.Path` objects directly — no `str()` cast needed.

4. **Print / display strings** (cells 10, 11, 19, 21, 22) — update human-readable messages from `./figs/` to `figs/` (root-relative display):
   ```python
   # BEFORE
   print(f"• Figures saved to: ./figs/")
   # AFTER
   print(f"• Figures saved to: {figs_path}")
   ```

### Files to move

```
src/figs/  →  figs/          (move entire directory)
```
Subdirectory structure is preserved:
```
figs/
├── cassava/
├── corn/
├── green_bean/
├── soybean/
├── price_avg_correlation_heatmap.png
├── price_avg_monthly_trend.png
├── price_avg_smoothed_trend.png
├── price_avg_yearly_trend.png
└── price_avg_yoy_change.png
```

### `.gitignore` impact

If Phase 0 has not yet run: add `figs/` to `.gitignore` (root-level entry).
If Phase 0 already ran with `src/figs/`: change that entry to `figs/`.

### Verification

```python
# Run in a notebook cell or python -c after the move:
from util.data_path import figs_path
assert figs_path.exists(), f"figs_path not found: {figs_path}"
assert figs_path.parent.name != "src", "figs is still inside src/ — move incomplete"
print("OK:", figs_path)
```
Then open `src/Data Analytical Trends.ipynb`, run all cells, and confirm images appear in root `figs/` (not `src/figs/`).

---

## Recommended Session Breakdown

| Session | Phases | Theme |
|---|---|---|
| 1 | 0 + 0b + 1 + 8 | Housekeeping — no ML logic touched |
| 2 | 2 + 3 | Class consolidation + config |
| 3 | 4 + 5 | Reproducibility + output format |
| 4 | 6 | Training script extraction (largest effort) |
| 5 | 7 + 9 | Data format migration + dead code removal |

---

## Critical Files

| File | Role |
|---|---|
| `src/util/data_path.py` | Central path registry — all other path imports converge here |
| `src/model1/(2) LSTM Model.ipynb` | Primary notebook; contains the `targ[:, 0]` training bug and all inline logic to extract |
| `src/util/lstm_cust_class.py` | To be replaced by `lstm_model.py` |
| `src/util/manystep_lstm_class.py` | Canonical multi-step design to preserve in `lstm_model.py` |
| `.gitignore` | First file to fix |
| `config.yaml` | To be created in Phase 3 |
| `src/util/output_io.py` | To be created in Phase 5 |
| `src/train/train_lstm.py` | To be created in Phase 6 |
| `figs/` | Root-level visualization output (moved from `src/figs/` in Phase 0b) |
