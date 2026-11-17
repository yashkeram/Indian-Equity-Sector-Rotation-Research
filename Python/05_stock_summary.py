
from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RANKING_DIR = BASE_DIR / "Data" / "Processed"
SUMMARY_DIR = BASE_DIR / "Data" / "Summary"


# ============================================================
# CONFIGURATION
# ============================================================

YEAR = 2026

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
]

MONTH_NAMES = {
    "Jan": "January",
    "Feb": "February",
    "Mar": "March",
    "Apr": "April",
    "May": "May",
    "Jun": "June",
    "Jul": "July",
    "Aug": "August",
    "Sep": "September",
    "Oct": "October",
}

TOP_COUNT = 3
BOTTOM_COUNT = 3


# ============================================================
# VALIDATE INPUTS
# ============================================================

def validate_directories():

    if not RANKING_DIR.exists():
        raise FileNotFoundError(
            f"Ranking folder not found: {RANKING_DIR}"
        )

    ranking_files = sorted(
        RANKING_DIR.glob("*_ranking.csv")
    )

    if not ranking_files:
        raise FileNotFoundError(
            f"No ranking CSV files found in: {RANKING_DIR}"
        )

    SUMMARY_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    return ranking_files


# ============================================================
# LOAD RANKING DATA
# ============================================================

def load_ranking(file_path):

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("Ranking file is empty.")

    if "Company" not in df.columns:
        raise ValueError(
            "Required Company column is missing."
        )

    return df


# ============================================================
# CREATE MONTHLY SUMMARY
# ============================================================

def create_monthly_summary(df, month):

    if month not in df.columns:
        return None

    temp = df[
        ["Company", month]
    ].copy()

    temp["Company"] = (
        temp["Company"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    temp[month] = pd.to_numeric(
        temp[month],
        errors="coerce"
    )

    temp = temp[
        (temp["Company"] != "")
        & temp[month].notna()
    ]

    if temp.empty:
        return None

    # Remove duplicate company entries.
    temp = temp.drop_duplicates(
        subset=["Company"],
        keep="first"
    )

    temp = temp.sort_values(
        by=month,
        ascending=False
    )

    # --------------------------------------------------------
    # TOP PERFORMERS
    # --------------------------------------------------------

    top = temp.head(TOP_COUNT).copy()

    top["Rank"] = [
        f"Top {i}"
        for i in range(1, len(top) + 1)
    ]

    # --------------------------------------------------------
    # BOTTOM PERFORMERS
    # --------------------------------------------------------

    # Exclude top performers to prevent overlap.
    remaining = temp.iloc[TOP_COUNT:].copy()

    bottom = (
        remaining
        .sort_values(
            by=month,
            ascending=True
        )
        .head(BOTTOM_COUNT)
        .copy()
    )

    bottom["Rank"] = [
        f"Bottom {i}"
        for i in range(1, len(bottom) + 1)
    ]

    # --------------------------------------------------------
    # COMBINE RESULTS
    # --------------------------------------------------------

    summary = pd.concat(
        [top, bottom],
        ignore_index=True
    )

    summary = summary.rename(
        columns={month: "Return"}
    )

    summary = summary[
        ["Company", "Return", "Rank"]
    ]

    return summary


# ============================================================
# PROCESS ONE SECTOR
# ============================================================

def process_sector(file_path):

    sector = file_path.stem.replace(
        "_ranking",
        ""
    )

    print("\n" + "-" * 55)
    print(f"PROCESSING: {sector.upper()}")
    print("-" * 55)

    df = load_ranking(file_path)

    print(
        f"Stocks in ranking file: {len(df)}"
    )

    generated = 0
    skipped = 0

    for month in MONTHS:

        summary = create_monthly_summary(
            df,
            month
        )

        if summary is None:

            print(
                f"{MONTH_NAMES[month]}: "
                "No valid data - skipped"
            )

            skipped += 1
            continue

        month_name = MONTH_NAMES[month]

        output_folder = SUMMARY_DIR / month_name

        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = (
            output_folder /
            f"{sector}_summary.csv"
        )

        summary.to_csv(
            output_file,
            index=False
        )

        generated += 1

        print(
            f"{month_name:<12} -> "
            f"{output_file.name}"
        )

    print(
        f"\nSummaries generated: {generated}"
    )

    print(
        f"Months skipped: {skipped}"
    )

    return generated


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 55)
    print("INDIAN EQUITY SECTOR ROTATION RESEARCH")
    print("MODULE 05 - STOCK SUMMARY")
    print("=" * 55)

    print(f"\nAnalysis year: {YEAR}")
    print(f"Months configured: {len(MONTHS)}")

    ranking_files = validate_directories()

    successful = 0
    failed = 0
    total_summaries = 0

    for file_path in ranking_files:

        try:

            generated = process_sector(
                file_path
            )

            successful += 1
            total_summaries += generated

        except Exception as error:

            failed += 1

            print(
                f"\nFAILED: {file_path.name}"
            )

            print(
                f"Reason: {error}"
            )

    print("\n" + "=" * 55)
    print("MODULE 05 SUMMARY")
    print("=" * 55)

    print(
        f"Successful sectors: {successful}"
    )

    print(
        f"Failed sectors: {failed}"
    )

    print(
        f"Total monthly summaries generated: "
        f"{total_summaries}"
    )

    print(
        f"\nOutput folder: {SUMMARY_DIR}"
    )

    print("\nMODULE 05 COMPLETED")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
