import pathlib

project_root = pathlib.Path(__file__).parent.parent.parent.parent.absolute()
data_path = project_root / "data" / "data_processed"

cassava_path = data_path / "cassava" / "price_avg.csv"
corn_path = data_path / "corn" / "price_avg.csv"

if __name__ == "__main__":
    print(cassava_path)
    print(corn_path)
