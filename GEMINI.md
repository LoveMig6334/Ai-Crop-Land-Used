# AI Crop Land-Use Analysis and Price Forecasting

## Project Overview
This project uses machine learning (LSTM, Transformer, ARIMA) to analyze and forecast agricultural commodity prices (cassava, corn, green beans, soybean) in Thailand. It includes data preprocessing, visualization, and income analysis components.

## Architecture & Data Flow

### Data Pipeline
1.  **Raw Data**: Stored in `data/raw/` (Excel/CSV).
2.  **Preprocessing**: Scripts in `src/data preparation/` clean and convert data.
3.  **Processed Data**: Saved to `data/data_processed/` and `data/fix_year/`.
4.  **Model Input**: Models read processed data using paths defined in `src/util/data_path.py`.
5.  **Model Output**:
    *   **Forecasts**: Saved in `model/forecast_price/`.
    *   **Metrics**: Saved in `model/error_record/`.
    *   **Visualizations**: Saved in `src/image/` (or `model/image` depending on script).

### Key Models
*   **LSTM**: `(2) LSTM Model.ipynb` / `(3) LSTM Model.ipynb` (Standard & 5-Year variants).
*   **Transformer**: `(2) Transformer Model.ipynb`.
*   **ARIMA**: `(2) ARIMA Model.ipynb`.

## Key Directories & Files

*   **`src/`**: Main source code and notebooks.
    *   `util/data_path.py`: **CRITICAL**. Central registry for all file paths. Always use this to resolve paths.
    *   `data preparation/`: Utilities for data cleaning (`data_cleanup.py`) and plotting (`data_plot.py`).
    *   `model1/`: Contains active model notebooks (ARIMA, LSTM, Transformer).
    *   `model2 (notuse)/`: Deprecated/experimental notebooks.
*   **`data/`**:
    *   `raw/`: Original datasets.
    *   `data_processed/`: Cleaned CSVs used for modeling.
*   **`model/`**:
    *   `forecast_price/`: Text files containing model predictions.
    *   `error_record/`: Performance metrics.

## Development Conventions

*   **Path Management**: *Never* hardcode paths. Import paths from `src.util.data_path`.
    ```python
    from src.util.data_path import cassava_price_avg
    df = pd.read_csv(cassava_price_avg)
    ```
*   **Data Handling**: Use `pandas` for tabular data.
*   **Deep Learning**: Use `torch` (PyTorch) for LSTM/Transformer models.
*   **Notebooks**: Primary development environment for models.
*   **Date Formats**: Be aware of Thai Buddhist Era (BE) years (e.g., 2568) vs Common Era (AD).

## Setup & Execution

1.  **Environment**: Python 3.12+ (managed via `.venv`).
    ```bash
    # Activate
    .venv\Scripts\activate  # Windows
    source .venv/bin/activate  # Linux/Mac
    ```
2.  **Dependencies**: `pip install -r requirements.txt`
3.  **Running Models**: Execute the respective Jupyter Notebooks in `src/` or `src/model1/`.
4.  **Web App**: `python src/app.py` (Flask-based interface).
