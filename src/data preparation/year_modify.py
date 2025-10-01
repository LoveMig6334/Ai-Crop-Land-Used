import os
from pathlib import Path

import pandas as pd


def buddhist_to_christian_year(buddhist_year):
    return buddhist_year - 543


def process_crop_data(input_folder, output_folder, crop_name):
    # Define input and output paths
    input_file = os.path.join(input_folder, crop_name, "price_avg.csv")
    output_dir = os.path.join(output_folder, crop_name)
    output_file = os.path.join(output_dir, "price_avg.csv")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Warning: Input file not found: {input_file}")
        return False

    try:
        # Read the CSV file
        df = pd.read_csv(input_file)

        # Convert years from Buddhist to Christian
        if "year" in df.columns:
            df["year"] = df["year"].apply(buddhist_to_christian_year)
            print(
                f"Converted years for {crop_name}: {df['year'].min()} - {df['year'].max()}"
            )
        else:
            print(f"Warning: No 'year' column found in {input_file}")
            return False

        # Save the modified data
        df.to_csv(output_file, index=False)
        print(f"Successfully saved: {output_file}")
        return True

    except Exception as e:
        print(f"Error processing {crop_name}: {str(e)}")
        return False


def modify_all_years(base_path=None):
    if base_path is None:
        # Get the project root directory (two levels up from this file)
        current_file = Path(__file__).resolve()
        base_path = current_file.parent.parent.parent

    # Define paths
    input_folder = os.path.join(base_path, "data", "data_processed")
    output_folder = os.path.join(base_path, "data", "fix_year")

    # List of crops to process
    crops = ["cassava", "corn", "green_bean", "soybean"]

    print("Starting year conversion from Buddhist to Christian calendar...")
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    print("-" * 60)

    # Process each crop
    success_count = 0
    for crop in crops:
        print(f"Processing {crop}...")
        if process_crop_data(input_folder, output_folder, crop):
            success_count += 1
        print()

    print("-" * 60)
    print(
        f"Conversion completed: {success_count}/{len(crops)} crops processed successfully"
    )

    return success_count == len(crops)


def preview_conversion(base_path=None):
    if base_path is None:
        current_file = Path(__file__).resolve()
        base_path = current_file.parent.parent.parent

    input_folder = os.path.join(base_path, "data", "data_processed")
    crops = ["cassava", "corn", "green_bean", "soybean"]

    print("Year Conversion Preview (Buddhist → Christian)")
    print("=" * 50)

    for crop in crops:
        input_file = os.path.join(input_folder, crop, "price_avg.csv")

        if os.path.exists(input_file):
            try:
                df = pd.read_csv(input_file)
                if "year" in df.columns:
                    first_years = df["year"].head(3).tolist()
                    converted_years = [
                        buddhist_to_christian_year(year) for year in first_years
                    ]

                    print(f"{crop.capitalize()}:")
                    for buddhist, christian in zip(first_years, converted_years):
                        print(f"  {buddhist} → {christian}")
                    print()
                else:
                    print(f"{crop.capitalize()}: No 'year' column found")
            except Exception as e:
                print(f"{crop.capitalize()}: Error reading file - {str(e)}")
        else:
            print(f"{crop.capitalize()}: File not found")


if __name__ == "__main__":
    # Show preview first
    print("=" * 60)
    preview_conversion()

    # Ask user confirmation
    response = (
        input("Do you want to proceed with the conversion? (y/n): ").lower().strip()
    )

    if response in ["y", "yes"]:
        print("\nProceeding with conversion...")
        success = modify_all_years()

        if success:
            print("\n✅ All datasets have been successfully converted!")
        else:
            print(
                "\n❌ Some errors occurred during conversion. Check the messages above."
            )
    else:
        print("\nConversion cancelled.")
