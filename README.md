# AI Crop Land-Use Analysis and Price Forecasting

A machine learning project for analyzing and forecasting crop prices, specifically focusing on cassava and corn agricultural commodities in Thailand. This project combines data preprocessing, visualization, and deep learning models to predict future crop prices based on historical data.

## 🌾 Project Overview

This project aims to:
- Analyze historical crop price data for cassava and corn
- Clean and preprocess agricultural price data
- Visualize price trends and patterns
- Develop neural network models for price forecasting
- Provide insights for agricultural decision-making

## 📁 Project Structure

```
Ai Crop Land-Used/
├── GIL-TEST.py                     # Python GIL status testing utility
├── README.md
├── requirements.txt
├── data/
│   ├── data_processed/
│   │   ├── cassava/
│   │   │   ├── price_avg.csv          # Processed cassava price data
│   │   │   └── price_low_high.csv     # Processed cassava min-max price data
│   │   ├── corn/
│   │   │   ├── price_avg.csv          # Processed corn price data
│   │   │   └── price_low_high.csv     # Processed corn min-max price data
│   │   └── weather/                   # Weather data directory
│   └── raw/
│       ├── cassava/
│       │   ├── price_avg.xls          # Raw cassava price data (Excel)
│       │   └── price_min-max.xls      # Cassava min-max price data (Excel)
│       ├── corn/
│       │   ├── price_avg.xls          # Raw corn price data (Excel)
│       │   └── price_min-max.xls      # Corn min-max price data (Excel)
│       └── weather/                   # Raw weather data directory
├── src/
│   ├── data preparation/
│   │   ├── data_cleanup.py            # Data cleaning utilities
│   │   └── data_plot.py               # Data visualization tools
│   └── model/
│       ├── ARIMA Model.ipynb          # Statistical forecasting model notebook
│       ├── LSTM Model.ipynb           # Deep learning forecasting model notebook
│       ├── Transformer Model.ipynb    # Transformer-based forecasting model notebook
│       ├── image/
│       │   ├── cassava_prices_forecast.png # Cassava forecast visualization
│       │   └── corn_prices_forecast.png    # Corn forecast visualization
│       └── util/
│           ├── __init__.py
│           ├── data_path.py           # Data path utilities
│           ├── lstm_cust_class.py     # Custom LSTM model class
│           └── transformer_cust_class.py # Custom Transformer model class
```

## 🚀 Features

- **Data Preprocessing**: Clean and prepare raw agricultural price data
- **Data Visualization**: Generate plots for price trend analysis
- **Time Series Forecasting**: 
  - LSTM-based neural network for price prediction
  - Transformer-based model for advanced sequence analysis
  - ARIMA statistical model for comparison
- **Multi-Crop Support**: Handles both cassava and corn price data
- **Thai Date Processing**: Handles Thai Buddhist calendar dates
- **Scalable Architecture**: Modular design for easy extension to other crops

## 📊 Data Description

The project works with Thai agricultural price data:
- **Time Period**: 2547-2568 BE (2004-2025 CE)
- **Frequency**: Monthly price data
- **Crops**: Cassava and Corn
- **Price Types**: Average, minimum, and maximum prices
- **Currency**: Thai Baht (THB)
- **Additional Data**: Weather data for correlation analysis

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "Ai Crop Land-Used"
   ```

2. **Create Python Environment (version 3.12.10)**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the environment**:
   - Windows:
   ```bash
   .venv\Scripts\activate
   ```
   - Linux/Mac:
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify installation**:
   ```bash
   python -c "import torch; print(torch.__version__)"
   ```

6. **Check GIL and Python status** (Optional):
   ```bash
   python GIL-TEST.py
   ```

## 💻 Usage

### Price Forecasting

1. **Open the Jupyter notebook for preferred model**:
   ```bash
   jupyter notebook "src/model/LSTM Model.ipynb"
   # or
   jupyter notebook "src/model/Transformer Model.ipynb"
   # or
   jupyter notebook "src/model/ARIMA Model.ipynb"
   ```

2. **Run the forecasting model**:
   - Execute all cells in the notebook
   - The model will train on historical data and generate predictions
   - Results will be saved as visualizations

### Key Components

#### Data Cleaning (`data_cleanup.py`)
- Removes unwanted Thai language columns
- Standardizes data format
- Prepares data for analysis

#### Data Visualization (`data_plot.py`)
- Generates price trend plots
- Handles Thai date format conversion
- Provides statistical summaries

#### Forecasting Models
**LSTM Model** (`LSTM Model.ipynb`)
- LSTM neural network implementation
- Time series preprocessing with MinMaxScaler
- 12-month sequence input for 12-month prediction
- PyTorch-based deep learning pipeline

**Transformer Model** (`Transformer Model.ipynb`)
- Self-attention based sequence model
- Advanced pattern recognition capabilities
- Parallelized computation for faster training
- State-of-the-art neural network architecture

**ARIMA Model** (`ARIMA Model.ipynb`) 
- Statistical time series forecasting
- Auto-regressive Integrated Moving Average
- Traditional statistical approach for comparison

## 🧠 Model Architecture

The project implements three forecasting approaches:

**LSTM Model:**
- **Input**: 12 months of historical price data
- **Architecture**: LSTM (Long Short-Term Memory) neural network
- **Output**: 12 months of future price predictions
- **Framework**: PyTorch (v2.7.0)
- **Preprocessing**: MinMaxScaler for data normalization

**Transformer Model:**
- **Input**: Historical price data sequence
- **Architecture**: Self-attention mechanism with encoding layers
- **Output**: Future price predictions with confidence intervals
- **Framework**: PyTorch (v2.7.0)
- **Advantages**: Better at capturing long-range dependencies in time series data

**ARIMA Model:**
- **Input**: Historical time series data
- **Method**: Auto-Regressive Integrated Moving Average
- **Components**: AR (auto-regression), I (differencing), MA (moving average)
- **Libraries**: statsmodels, statsforecast

## 📈 Results

The models generate:
- Price forecasts for the next 12 months
- Visualization of predicted vs. actual prices
- Performance metrics and validation results
- Saved forecast plots in the `src/model/image` directory
- Comparative analysis between statistical and deep learning approaches

![LSTM](src/model/image/cassava_prices_forecast.png)

## 🔧 Technical Requirements

- **Python**: 3.12.10
- **PyTorch**: 2.7.0 (with CUDA 12.6 support)
- **Key Libraries**:
  - pandas: 2.2.3 (Data manipulation)
  - numpy: 2.2.6 (Numerical computing)
  - matplotlib: 3.10.3 (Visualization)
  - scikit-learn: 1.6.1 (Data preprocessing)
  - statsmodels: 0.14.4 (Statistical modeling)
  - jupyter: 1.1.1 (Interactive development)
  - fugue: 0.9.1 (Data processing)
  - coreforecast: 0.0.16 (Forecasting utilities)

## 📝 Data Format

### Input Data Format (CSV)
```csv
year,1,2,3,4,5,6,7,8,9,10,11,12
2547,0.99,0.95,0.96,1.04,1.13,1.18,1.21,1.21,1.17,1.11,1.19,1.30
```
- Columns 1-12 represent months (January-December)
- Years in Thai Buddhist calendar (BE)
- Prices in Thai Baht

## 🙏 Acknowledgments

- Thai agricultural data sources
- PyTorch community for deep learning framework
- Agricultural research institutions for domain expertise

## 📞 Contact

For questions or collaboration opportunities, please open an issue or contact the project maintainers.

---

*Built with ❤️ for sustainable agriculture and data-driven farming decisions*

*Last updated: June 4, 2025*