import os

import matplotlib.pyplot as plt
import pandas as pd


def get_file_path() -> str:
    folder_path = os.path.join(
        os.path.dirname(os.path.join(os.path.dirname(__file__))), "data"
    )
    file_path = os.path.join(folder_path, "PriceDay.csv")
    print(file_path)

    return file_path


def price_reading(file_path) -> None:
    df = pd.read_csv(file_path)
    print(df.head())
    print(df.describe())
    print(df.info())


def plot_data(file_path):
    df = pd.read_csv(file_path)

    min_price = df["min-price"]
    max_price = df["max-price"]

    x_axis = list(range(len(min_price)))

    # Plotting the data
    plt.plot(x_axis, min_price, label="Min Price", color="blue")
    plt.plot(x_axis, max_price, label="Max Price", color="red")

    plt.title("Price Data")
    plt.xlabel("Index")
    plt.ylabel("Price")
    plt.legend()
    plt.show()


def print_year(file_path: str) -> None:
    df = pd.read_csv(file_path)
    date = df["date"]

    month_dict = {
        "ม.ค.": 1,
        "ก.พ.": 2,
        "มี.ค.": 3,
        "เม.ย.": 4,
        "พ.ค.": 5,
        "มิ.ย.": 6,
        "ก.ค.": 7,
        "ส.ค.": 8,
        "ก.ย.": 9,
        "ต.ค.": 10,
        "พ.ย.": 11,
        "ธ.ค.": 12,
    }

    for date_str in date:
        day, month, year = date_str.split(" ")
        print(f"Day: {day}, Month: {month_dict[month]}, Year: {year}")


def main() -> None:
    data_path = get_file_path()

    price_reading(data_path)

    plot_data(data_path)

    print_year(data_path)


if __name__ == "__main__":
    main()
