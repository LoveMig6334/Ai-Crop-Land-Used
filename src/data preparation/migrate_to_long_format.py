"""One-time migration: wide-format fix_year CSVs → long-format CSVs.

Reads data/fix_year/{crop}/price_avg.csv (year as row, months 1-12 as columns,
CE years 2004-2024) and writes data/long_format/{crop}/price_avg.csv with two
columns: date (YYYY-MM-DD, first of month) and price.

Uses only stdlib so it can be run with any Python interpreter.
"""
import csv
import pathlib

project_root = pathlib.Path(__file__).parent.parent.parent.absolute()
fix_year_path = project_root / "data" / "fix_year"
long_format_path = project_root / "data" / "long_format"

CROPS = ["cassava", "corn", "green_bean", "soybean"]
MONTHS = [str(m) for m in range(1, 13)]


def migrate_crop(crop: str) -> None:
    src = fix_year_path / crop / "price_avg.csv"
    dst_dir = long_format_path / crop
    dst = dst_dir / "price_avg.csv"

    rows = []
    with open(src, newline="") as f:
        reader = csv.DictReader(f)
        for record in reader:
            year = int(record["year"])
            for month in MONTHS:
                date = f"{year}-{int(month):02d}-01"
                price = record[month]
                rows.append((date, price))

    rows.sort(key=lambda r: r[0])

    dst_dir.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "price"])
        writer.writerows(rows)

    print(f"{crop}: {len(rows)} rows -> {dst}")
    print(f"  first: date={rows[0][0]}, price={rows[0][1]}")
    print(f"  last:  date={rows[-1][0]}, price={rows[-1][1]}")


if __name__ == "__main__":
    for crop in CROPS:
        migrate_crop(crop)
    print("\nMigration complete.")
