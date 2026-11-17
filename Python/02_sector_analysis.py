
from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "Data" / "Raw"
PROCESSED_DIR = BASE_DIR / "Data" / "Processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = PROCESSED_DIR / "sector_returns.csv"


# ============================================================
# CONFIGURATION
# ============================================================

INDEX_FILES = {
    "nifty50": "nifty50.csv",
    "bank": "bank.csv",
    "it": "it.csv",
    "pharma": "pharma.csv",
    "auto": "auto.csv",
    "fmcg": "fmcg.csv",
    "metal": "metal.csv",
    "realty": "realty.csv",
}


# ============================================================
# LOAD AND VALIDATE DATA
# ============================================================

def load_index_data(name, filename):

    file_path = RAW_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("Dataset is empty.")

    required_columns = ["Date", "Close"]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # Convert dates.
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # Convert closing prices.
    df["Close"] = pd.to_numeric(
        df["Close"],
        errors="coerce"
    )

    # Remove invalid observations.
    df = df.dropna(
        subset=["Date", "Close"]
    )

    if df.empty:
        raise ValueError(
            "No valid Date and Close observations."
        )

    # Sort and remove duplicate dates.
    df = (
        df.sort_values("Date")
        .drop_duplicates(
            subset=["Date"],
            keep="last"
        )
    )

    return df


# ============================================================
# CALCULATE MONTHLY RETURNS
# ============================================================

def calculate_monthly_returns(df):

    df = df.set_index("Date")

    # Last available closing price of each month.
    monthly_close = (
        df["Close"]
        .resample("ME")
        .last()
    )

    # Calculate percentage returns.
    monthly_returns = (
        monthly_close.pct_change() * 100
    )

    return monthly_returns


# ============================================================
# MAIN ANALYSIS
# ============================================================

def main():

    print("=" * 55)
    print("INDIAN EQUITY SECTOR ROTATION RESEARCH")
    print("MODULE 02 - SECTOR ANALYSIS")
    print("=" * 55)

    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"Raw data directory not found: {RAW_DIR}"
        )

    results = pd.DataFrame()

    successful = 0
    failed = 0

    for name, filename in INDEX_FILES.items():

        print(f"\nProcessing {name.upper()}...")

        try:

            df = load_index_data(
                name,
                filename
            )

            monthly_returns = calculate_monthly_returns(
                df
            )

            results[name] = monthly_returns

            successful += 1

            print(
                f"  Records processed: {len(df)}"
            )

            print(
                f"  Latest observation: "
                f"{df['Date'].max().date()}"
            )

        except Exception as error:

            failed += 1

            print(
                f"  FAILED: {name.upper()}"
            )

            print(
                f"  Reason: {error}"
            )

    # --------------------------------------------------------
    # CHECK RESULTS
    # --------------------------------------------------------

    if results.empty:
        raise RuntimeError(
            "No index data could be processed."
        )

    # --------------------------------------------------------
    # EXCLUDE INCOMPLETE CURRENT MONTH
    # --------------------------------------------------------

    current_month_start = (
        pd.Timestamp.today()
        .to_period("M")
        .to_timestamp()
    )

    results = results[
        results.index < current_month_start
    ]

    # --------------------------------------------------------
    # ROUND RESULTS
    # --------------------------------------------------------

    results = results.sort_index().round(2)

    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    results.index.name = "Date"

    results.to_csv(OUTPUT_FILE)

    # --------------------------------------------------------
    # DISPLAY SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 55)
    print("MONTHLY SECTOR RETURNS")
    print("=" * 55)

    print(results.to_string())

    print("\n" + "=" * 55)
    print("ANALYSIS SUMMARY")
    print("=" * 55)

    print(f"Successful datasets: {successful}")
    print(f"Failed datasets: {failed}")

    print(
        f"First month: {results.index.min().strftime('%B %Y')}"
    )

    print(
        f"Last month: {results.index.max().strftime('%B %Y')}"
    )

    print(f"\nSaved to: {OUTPUT_FILE}")

    print("\nMODULE 02 COMPLETED")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
