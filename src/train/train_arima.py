"""ARIMA training and forecasting pipeline with JSON order sidecar caching."""
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error
from statsforecast import StatsForecast
from statsforecast.models import ARIMA, AutoARIMA

from util.config import CFG
from util.data_path import ARIMA_err, ARIMA_for, weights_path
from util.data_utils import load_and_prepare
from util.output_io import save_error_csv, save_forecast_csv, save_summary_csv


def _build_sf_data(y_train: pd.Series, unique_id: str = "series") -> pd.DataFrame:
    """Convert a monthly price Series to the StatsForecast input format."""
    return (
        y_train.rename("y")
        .to_frame()
        .assign(ds=lambda df: df.index, unique_id=unique_id)
        .reset_index(drop=True)
    )


def _extract_arima_order(sf: StatsForecast) -> dict | None:
    """Try to extract the selected ARIMA order from a fitted StatsForecast model.

    Returns a dict with keys 'order' and 'seasonal_order', or None on failure.
    """
    try:
        fitted = sf.fitted_[0][0]
        arma = fitted.model_["arma"]
        # arma layout: [p, q, P, Q, m, d, D]
        return {
            "order": [int(arma[0]), int(arma[5]), int(arma[1])],
            "seasonal_order": [int(arma[2]), int(arma[6]), int(arma[3]), int(arma[4])],
        }
    except Exception:
        return None


def train_and_forecast(
    data_file: Path, force_retrain: bool = False
) -> tuple[pd.Series, pd.Series, None, pd.DataFrame]:
    """Full ARIMA pipeline: load data, fit AutoARIMA (or cached order), save outputs.

    Uses a JSON sidecar at model/weights/{crop}_arima_order.json to cache the
    selected model order. On subsequent runs the cached order is used directly,
    skipping expensive AutoARIMA model selection.

    Args:
        data_file:      Path to wide-format price CSV (e.g. corn_price_avg).
        force_retrain:  If True, ignore the JSON sidecar and re-run AutoARIMA.

    Returns:
        forecast : pd.Series, 12-month DatetimeIndex, name='forecast_price'
        actual   : pd.Series, 12-month DatetimeIndex (y_test in original scale)
        None     : placeholder for scaler (ARIMA uses raw price scale)
        long     : full long-format DataFrame (all years, column 'price')
    """
    data_file = Path(data_file)
    crop_name = data_file.parent.name

    train, future, series, scaler, long = load_and_prepare(data_file)

    y_train = train["price"].asfreq("MS")
    y_test = future["price"].asfreq("MS")

    weights_path.mkdir(parents=True, exist_ok=True)
    order_file = weights_path / f"{crop_name}_arima_order.json"

    sf_data = _build_sf_data(y_train, unique_id=crop_name)

    if order_file.exists() and not force_retrain:
        # Fast path: use the cached model order
        with open(order_file) as f:
            saved = json.load(f)
        order = tuple(saved["order"])
        season_order = tuple(saved["seasonal_order"])
        print(f"Loaded ARIMA order from {order_file.name}: {order} x {season_order}")
        sf = StatsForecast(
            models=[ARIMA(order=order, season_order=season_order)],
            freq="MS",
        )
        sf_forecasts = sf.fit_predict(df=sf_data, h=12)
        arima_col = "ARIMA"
    else:
        # Slow path: run AutoARIMA and try to cache the selected order
        sf = StatsForecast(
            models=[
                AutoARIMA(
                    season_length=12,
                    start_p=1,
                    start_q=1,
                    max_p=3,
                    max_q=3,
                    d=1,
                    seasonal=True,
                    stepwise=True,
                    trace=True,
                    approximation=False,
                )
            ],
            freq="MS",
        )
        sf_forecasts = sf.fit_predict(df=sf_data, h=12)
        arima_col = "AutoARIMA"

        # Attempt to save the selected order as a JSON sidecar
        saved_order = _extract_arima_order(sf)
        if saved_order is not None:
            with open(order_file, "w") as f:
                json.dump(saved_order, f, indent=2)
            print(f"Saved ARIMA order to {order_file.name}: {saved_order}")
        else:
            print("Could not extract ARIMA order; sidecar not written.")

    arima_series = sf_forecasts.set_index("ds")[arima_col]
    forecast = arima_series.rename("forecast_price")

    save_forecast_csv(forecast, ARIMA_for, crop_name)

    # Error metrics
    error = y_test - forecast
    abs_error = error.abs()
    denom = y_test.replace(0, pd.NA)
    abs_pct_error = (abs_error / denom) * 100
    mae = mean_absolute_error(y_test, forecast)
    mape = abs_pct_error.mean()

    error_df = pd.DataFrame(
        {
            "actual": y_test,
            "forecast": forecast,
            "error": error,
            "abs_error": abs_error,
            "abs_pct_error": abs_pct_error,
        }
    )
    save_error_csv(error_df, ARIMA_err, crop_name)

    accuracy = 100 - (mae / y_test.mean() * 100)
    summary = {
        "MAE": round(mae, 6),
        "MAPE": round(float(mape), 4),
        "accuracy_pct": round(accuracy, 2),
    }
    save_summary_csv(summary, ARIMA_err, crop_name)

    return forecast, y_test, None, long


if __name__ == "__main__":
    import argparse

    from util.data_path import (
        cassava_price_avg,
        corn_price_avg,
        green_bean_price_avg,
        soybean_price_avg,
    )

    crops = {
        "cassava": cassava_price_avg,
        "corn": corn_price_avg,
        "green_bean": green_bean_price_avg,
        "soybean": soybean_price_avg,
    }

    p = argparse.ArgumentParser(description="Fit ARIMA and forecast crop prices.")
    p.add_argument("--crop", default="corn", choices=list(crops))
    p.add_argument("--force-retrain", action="store_true")
    args = p.parse_args()

    train_and_forecast(crops[args.crop], force_retrain=args.force_retrain)
