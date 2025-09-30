import pathlib

project_root = pathlib.Path(__file__).parent.parent.parent.absolute()
data_path = project_root / "data" / "data_processed"

cassava_path = data_path / "cassava"
corn_path = data_path / "corn"
green_bean_path = data_path / "green_bean"
soybean_path = data_path / "soybean"

cassava_price_avg = cassava_path / "price_avg.csv"
corn_price_avg = corn_path / "price_avg.csv"
green_bean_price_avg = green_bean_path / "price_avg.csv"
soybean_price_avg = soybean_path / "price_avg.csv"


if __name__ == "__main__":
    print(cassava_path)
    print(corn_path)
    print(green_bean_path)
    print(soybean_path)

    print(cassava_price_avg)
    print(corn_price_avg)
    print(green_bean_price_avg)
    print(soybean_price_avg)

    print("Data paths initialized successfully.")
    print(f"Project root: {project_root}")
