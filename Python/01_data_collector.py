
from pathlib import Path

import pandas as pd
import yfinance as yf


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "Data" / "Raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

START_DATE = "2025-12-01"
END_DATE = "2026-11-01"  # Exclusive: includes October 2026

INDICES = {
    "nifty50": "^NSEI",
    "bank": "^NSEBANK",
    "it": "^CNXIT",
    "pharma": "^CNXPHARMA",
    "auto": "^CNXAUTO",
    "fmcg": "^CNXFMCG",
    "metal": "^CNXMETAL",
    "realty": "^CNXREALTY",
}


# ============================================================
# DOWNLOAD AND VALIDATE DATA
# ============================================================

def download_index(name, ticker):

    print("\n" + "-" * 50)
    print(f"Downloading {name.upper()} ({ticker})...")
    print("-" * 50)

    try:

        df = yf.download(
            ticker,
            start=START_DATE,
            end=END_DATE,
            auto_adjust=True,
            progress=False,
            group_by="column",
        )

        if df.empty:
            raise ValueError("Yahoo Finance returned no data.")

        # Handle yfinance MultiIndex columns.
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if "Close" not in df.columns:
            raise ValueError("Close column not found.")

        # Reset index to create Date column.
        df = df.reset_index()

        if "Date" not in df.columns:
            df = df.rename(
                columns={df.columns[0]: "Date"}
            )

        # Validate dates.
        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

        df = df.dropna(subset=["Date"])

        if df.empty:
            raise ValueError("No valid dates found.")

        # Sort and remove duplicate dates.
        df = (
            df.sort_values("Date")
            .drop_duplicates(
                subset=["Date"],
                keep="last"
            )
        )

        # Validate closing prices.
        df["Close"] = pd.to_numeric(
            df["Close"],
            errors="coerce"
        )

        df = df.dropna(subset=["Close"])

        if df.empty:
            raise ValueError("No valid closing prices found.")

        output_file = RAW_DIR / f"{name}.csv"

        # ----------------------------------------------------
        # MERGE WITH EXISTING DATA
        # ----------------------------------------------------

        if output_file.exists():

            print("Existing dataset found. Checking its contents...")

            try:
                existing = pd.read_csv(output_file)

                if existing.empty:
                    print("Existing file has no records. Using fresh download.")

                elif "Date" not in existing.columns or "Close" not in existing.columns:
                    print("Existing file has an invalid structure. Using fresh download.")

                else:

                    existing["Date"] = pd.to_datetime(
                        existing["Date"],
                        errors="coerce"
                    )

                    existing["Close"] = pd.to_numeric(
                        existing["Close"],
                        errors="coerce"
                    )

                    existing = existing.dropna(
                        subset=["Date", "Close"]
                    )

                    if existing.empty:
                        print("Existing file has no valid records. Using fresh download.")

                    else:

                        print("Valid historical data found. Merging...")

                        df = pd.concat(
                            [existing, df],
                            ignore_index=True,
                            sort=False
                        )

                        # New downloaded records take priority.
                        df = (
                            df.sort_values("Date")
                            .drop_duplicates(
                                subset=["Date"],
                                keep="last"
                            )
                        )

            except pd.errors.EmptyDataError:
                print("Existing file is empty. Using fresh download.")

        # ----------------------------------------------------
        # SAVE DATA
        # ----------------------------------------------------

        df.to_csv(
            output_file,
            index=False
        )

        print(f"Saved: {output_file.relative_to(BASE_DIR)}")
        print(f"Total records: {len(df)}")
        print(f"First date: {df['Date'].min().date()}")
        print(f"Latest date: {df['Date'].max().date()}")

        return True

    except Exception as error:

        print(f"FAILED: {name.upper()}")
        print(f"Reason: {error}")

        return False


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():

    print("=" * 55)
    print("INDIAN EQUITY SECTOR ROTATION RESEARCH")
    print("MODULE 01 - DATA COLLECTOR")
    print("=" * 55)

    print(f"\nStart date: {START_DATE}")
    print("End date: October 31, 2026 (exclusive boundary: Nov 1)")

    successful = 0
    failed = 0

    for name, ticker in INDICES.items():

        result = download_index(
            name,
            ticker
        )

        if result:
            successful += 1
        else:
            failed += 1

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 55)
    print("DATA COLLECTION SUMMARY")
    print("=" * 55)

    print(f"Total indices: {len(INDICES)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\nAll index datasets updated successfully.")
    else:
        print(
            "\nSome datasets could not be updated. "
            "Review the errors above."
        )

    print("=" * 55)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
