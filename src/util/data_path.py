import pathlib

project_root = pathlib.Path(__file__).parent.parent.parent.absolute()
data_path = project_root / "data" / "data_processed"
fix_data_path = project_root / "data" / "fix_year"

cassava_path = data_path / "cassava"
corn_path = data_path / "corn"
green_bean_path = data_path / "green_bean"
soybean_path = data_path / "soybean"

cassava_price_avg = cassava_path / "price_avg.csv"
corn_price_avg = corn_path / "price_avg.csv"
green_bean_price_avg = green_bean_path / "price_avg.csv"
soybean_price_avg = soybean_path / "price_avg.csv"


model_save = project_root / "model"
figs_path = project_root / "figs"
weights_path = project_root / "model" / "weights"

error_record = model_save / "error_record"
forecasted_record = model_save / "forecast_price"

ARIMA_5_err = error_record / "(5)-ARIMA"
LSTM_5_err = error_record / "(5)-LSTM"
Transformer_5_err = error_record / "(5)-Transformer"

ARIMA_err = error_record / "ARIMA"
LSTM_err = error_record / "LSTM"
Transformer_err = error_record / "Transformer"

ARIMA_5_for = forecasted_record / "(5)-ARIMA"
LSTM_5_for = forecasted_record / "(5)-LSTM"
Transformer_5_for = forecasted_record / "(5)-Transformer"

ARIMA_for = forecasted_record / "ARIMA"
LSTM_for = forecasted_record / "LSTM"
Transformer_for = forecasted_record / "Transformer"

LSTM_5T_for = forecasted_record / "LSTM-5T"
LSTM_5T_err = error_record / "LSTM-5T"

cassava_path_year_fix = fix_data_path / "cassava"
corn_path_year_fix = fix_data_path / "corn"
green_bean_year_fix = fix_data_path / "green_bean"
soybean_path_year_fix = fix_data_path / "soybean"

cassava_price_avg_year_fix = cassava_path_year_fix / "price_avg.csv"
corn_price_avg_year_fix = corn_path_year_fix / "price_avg.csv"
green_bean_price_avg_year_fix = green_bean_year_fix / "price_avg.csv"
soybean_price_avg_year_fix = soybean_path_year_fix / "price_avg.csv"

# Raw data paths (previously in src/data preparation/raw_data_path.py)
raw_data_path = project_root / "data" / "raw"

cassava_raw_path = raw_data_path / "cassava"
corn_raw_path = raw_data_path / "corn"
weather_raw_path = raw_data_path / "weather"

cassava_raw_price_avg = cassava_raw_path / "price_avg.csv"
cassava_raw_price_low_high = cassava_raw_path / "price_low_high.csv"

corn_raw_price_avg = corn_raw_path / "price_avg.csv"
corn_raw_price_low_high = corn_raw_path / "price_low_high.csv"


if __name__ == "__main__":
    print(cassava_path_year_fix)
    print(corn_path_year_fix)
    print(green_bean_year_fix)
    print(soybean_path_year_fix)

    print(cassava_price_avg_year_fix)
    print(corn_price_avg_year_fix)
    print(green_bean_price_avg_year_fix)
    print(soybean_price_avg_year_fix)

    print("Data paths initialized successfully.")
    print(f"Project root: {project_root}")
