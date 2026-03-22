import pathlib

project_root = pathlib.Path(__file__).parent.parent.parent.absolute()
fix_data_path = project_root / "data" / "fix_year"

model_save = project_root / "model"
weights_path = project_root / "model" / "weights"

# Centralized fig/ directory tree
fig_root             = project_root / "fig"
fig_model_forecast   = fig_root / "model" / "forecast"
fig_model_error      = fig_root / "model" / "error"
fig_analysis_image   = fig_root / "analysis" / "image"
fig_analysis_trans   = fig_root / "analysis" / "transitions"
fig_analysis_trends  = fig_root / "analysis" / "trends"
fig_analysis_overlap = fig_root / "analysis" / "overlap"
fig_final_lstm3      = fig_root / "final" / "lstm-3layer"
fig_final_gantt      = fig_root / "final" / "gantt chart"

figs_path    = fig_analysis_image        # was: project_root / "figs"
reports_path = project_root / "reports"

error_record = model_save / "error_record"
forecasted_record = model_save / "forecast_price"

ARIMA_err = error_record / "ARIMA"
LSTM_err = error_record / "LSTM"
Transformer_err = error_record / "Transformer"

ARIMA_for = forecasted_record / "ARIMA"
LSTM_for = forecasted_record / "LSTM"
Transformer_for = forecasted_record / "Transformer"

LSTM_3L_for = forecasted_record / "LSTM-3L"
LSTM_3L_err = error_record / "LSTM-3L"

long_format_path = project_root / "data" / "long_format"
cassava_long     = long_format_path / "cassava"    / "price_avg.csv"
corn_long        = long_format_path / "corn"       / "price_avg.csv"
green_bean_long  = long_format_path / "green_bean" / "price_avg.csv"
soybean_long     = long_format_path / "soybean"    / "price_avg.csv"

cassava_path_year_fix = fix_data_path / "cassava"
corn_path_year_fix = fix_data_path / "corn"
green_bean_year_fix = fix_data_path / "green_bean"
soybean_path_year_fix = fix_data_path / "soybean"

cassava_price_avg_year_fix = cassava_path_year_fix / "price_avg.csv"
corn_price_avg_year_fix = corn_path_year_fix / "price_avg.csv"
green_bean_price_avg_year_fix = green_bean_year_fix / "price_avg.csv"
soybean_price_avg_year_fix = soybean_path_year_fix / "price_avg.csv"
