# DEPRECATED: All paths have been consolidated into src/util/data_path.py.
# This shim re-exports the canonical names for backwards compatibility.
# Remove this file once all consumers have been updated to import from util.data_path.

from util.data_path import (
    raw_data_path as data_path,
    cassava_raw_path as cassava_path,
    corn_raw_path as corn_path,
    weather_raw_path as weather_path,
    cassava_raw_price_avg as cassava_price_avg,
    cassava_raw_price_low_high as cassava_price_low_high,
    corn_raw_price_avg as corn_price_avg,
    corn_raw_price_low_high as corn_price_low_high,
)
