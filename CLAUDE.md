# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Crop Land-Use Analysis and Price Forecasting - a machine learning project for analyzing and forecasting Thai agricultural commodity prices (cassava, corn, green beans, soybean) using LSTM, Transformer, and ARIMA models.

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
# Run Jupyter notebooks for model training
jupyter notebook "src/model1/(2) LSTM Model.ipynb"
jupyter notebook "src/model1/(2) Transformer Model.ipynb"
jupyter notebook "src/model1/(2) ARIMA Model.ipynb"

# Analysis notebooks
jupyter notebook "src/Data Analytical.ipynb"
jupyter notebook "src/Error Analytical.ipynb"
jupyter notebook "src/Gantt chart.ipynb"
```

## Architecture

### Data Pipeline
1. **Raw Data** (`data/raw/`) - Excel/CSV files with Thai Buddhist Era dates
2. **Preprocessing** (`src/data preparation/`) - Cleans data, handles Thai date formats
3. **Processed Data** (`data/data_processed/`, `data/fix_year/`) - Ready for modeling
4. **Model Output**:
   - Forecasts: `model/forecast_price/{MODEL_TYPE}/`
   - Error metrics: `model/error_record/{MODEL_TYPE}/`
   - Visualizations: `src/image/`

### Critical Path Management
**Always use `src/util/data_path.py` for file paths** - never hardcode paths.

```python
from src.util.data_path import cassava_price_avg, LSTM_for, LSTM_err
df = pd.read_csv(cassava_price_avg)
```

Key path variables:
- `cassava_price_avg`, `corn_price_avg`, `green_bean_price_avg`, `soybean_price_avg` - processed price data
- `LSTM_for`, `Transformer_for`, `ARIMA_for` - forecast output directories
- `LSTM_err`, `Transformer_err`, `ARIMA_err` - error metrics directories
- `*_5_for`, `*_5_err` - 5-year forecast variants

### Model Classes
- `src/util/lstm_cust_class.py` - `LSTMRegressor` (2-layer LSTM) and `SeqDataset`
- `src/util/transformer_cust_class.py` - `TransformerRegressor` (self-attention with positional encoding) and `SeqDataset`

Both use:
- `seq_len=12` (12 months input)
- `pred_len=12` (12 months output)
- MinMaxScaler normalization

### Directory Structure
- `src/model1/` - Active model notebooks (LSTM, Transformer, ARIMA)
- `src/model2 (notuse)/` - Deprecated/experimental notebooks (5-year variants)
- `src/util/` - Shared utilities and custom model classes
- `src/data preparation/` - Data cleaning and plotting utilities

## Data Format

CSV format with Thai Buddhist Era years:
```csv
year,1,2,3,4,5,6,7,8,9,10,11,12
2547,0.99,0.95,0.96,1.04,...
```
- Columns 1-12 = months (January-December)
- Years in BE (subtract 543 for CE: 2547 BE = 2004 CE)
- Prices in Thai Baht

## Key Dependencies

- PyTorch 2.7+ (CUDA 12.6 for GPU)
- pandas, numpy, matplotlib
- scikit-learn (MinMaxScaler)
- statsmodels, statsforecast (ARIMA)
- Flask (web interface)
