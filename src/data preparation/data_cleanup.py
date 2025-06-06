import pandas as pd


def file_xls_to_csv(file_path: str, output_path: str) -> None:
    """
    Convert an Excel file to CSV format.

    :param file_path: Path to the input Excel file.
    :param output_path: Path where the output CSV file will be saved.
    """
    df = pd.read_excel(file_path)
    df.to_csv(output_path, index=False)


def remove_unwanted_columns(df: pd.DataFrame, columns_name: str) -> pd.DataFrame:
    df.drop(columns=columns_name, axis=1, inplace=True)
    return df


def remove_unwanted_rows(
    df: pd.DataFrame, column_name: str, value: str
) -> pd.DataFrame:
    df = df[df[column_name] != value]
    return df
