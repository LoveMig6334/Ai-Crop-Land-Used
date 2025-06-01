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
├── README.md
├── requirements.txt
├── data/
│   ├── data_processed/
│   │   └── cassava/
│   │       └── price_avg.csv          # Processed cassava price data
│   └── raw/
│       ├── cassava/
│       │   ├── price_avg.csv          # Raw cassava price data
│       │   └── price_min-max.csv      # Min-max price data
│       └── corn/
│           ├── price avg/             # Corn average price data
│           └── price min-max/         # Corn min-max price data
├── src/
│   ├── data preparation/
│   │   ├── data_cleanup.py            # Data cleaning utilities
│   │   └── data_plot.py              # Data visualization tools
│   └── model/
│       ├── example.ipynb             # Main forecasting model notebook
│       └── cassava_prices_forecast.png # Generated forecast visualization
```

## 🚀 Features

- **Data Preprocessing**: Clean and prepare raw agricultural price data
- **Data Visualization**: Generate plots for price trend analysis
- **Time Series Forecasting**: LSTM-based neural network for price prediction
- **Multi-Crop Support**: Handles both cassava and corn price data
- **Thai Date Processing**: Handles Thai Buddhist calendar dates
- **Scalable Architecture**: Modular design for easy extension to other crops

## 📊 Data Description

The project works with Thai agricultural price data:
- **Time Period**: 2547-2567 BE (2004-2024 CE)
- **Frequency**: Monthly price data
- **Crops**: Cassava and Corn
- **Price Types**: Average, minimum, and maximum prices
- **Currency**: Thai Baht (THB)

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

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python -c "import torch; print(torch.__version__)"
   ```

## 💻 Usage

### Price Forecasting

1. **Open the Jupyter notebook**:
   ```bash
   jupyter notebook "src/model/LSTM Model.ipynb"
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

#### Forecasting Model (`example.ipynb`)
- LSTM neural network implementation
- Time series preprocessing with MinMaxScaler
- 12-month sequence input for 12-month prediction
- PyTorch-based deep learning pipeline

## 🧠 Model Architecture

The forecasting model uses:
- **Input**: 12 months of historical price data
- **Architecture**: LSTM (Long Short-Term Memory) neural network
- **Output**: 12 months of future price predictions
- **Framework**: PyTorch
- **Preprocessing**: MinMaxScaler for data normalization

## 📈 Results

The model generates:
- Price forecasts for the next 12 months
- Visualization of predicted vs. actual prices
- Performance metrics and validation results
- Saved forecast plots in the `src/model/` directory

## 🔧 Technical Requirements

- **Python**: 3.12.10
- **PyTorch**: 2.7.0 (with CUDA support)
- **Key Libraries**:
  - pandas: Data manipulation
  - numpy: Numerical computing
  - matplotlib: Visualization
  - scikit-learn: Data preprocessing
  - jupyter: Interactive development
  - PyTorch: AI training class framework

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