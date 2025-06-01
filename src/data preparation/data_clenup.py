import os

import pandas as pd


def get_file_path() -> str:
    folder_path = os.path.join(
        os.path.dirname(os.path.join(os.path.dirname(__file__))), "data"
    )
    file_path = os.path.join(folder_path, "PriceDay.csv")
    print(file_path)

    return file_path


def remove_unwanted_columns(file_path, columns_name: str) -> None:
    df = pd.read_csv(file_path)
    df.drop(columns_name, axis=1, inplace=True)
    df.to_csv(file_path, index=False)
    print(f"Removed columns: {columns_name}")


def main() -> None:
    data_path = get_file_path()

    unwanted_columns = ["ประเภท", "สินค้า", "หน่วย"]

    for column in unwanted_columns:
        remove_unwanted_columns(data_path, column)


if __name__ == "__main__":
    main()
