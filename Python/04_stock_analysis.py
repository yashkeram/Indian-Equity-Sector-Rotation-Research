
from pathlib import Path
import sys
import calendar

import pandas as pd
import yfinance as yf


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

UNIVERSE_DIR = BASE_DIR / "Data" / "Universe"
PROCESSED_DIR = BASE_DIR / "Data" / "Processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_TARGET_MONTH = "2026-10"
LOOKBACK_DAYS = 15


# ============================================================
# MONTH INPUT
# ============================================================

def parse_target_month():

    if len(sys.argv) > 2:
        raise ValueError(
            "Please provide only one month. "
            "Example: python Python/04_stock_analysis.py September"
        )

    month_input = (
        sys.argv[1].strip()
        if len(sys.argv) == 2
        else DEFAULT_TARGET_MONTH
    )

    try:
        # Accept YYYY-MM format.
        if (
            len(month_input) == 7
            and month_input[4] == "-"
        ):
            period = pd.Period(month_input, freq="M")

        else:
            # Accept full month names and abbreviations.
            month_name = month_input.strip().lower()

            month_number = None

            for number in range(1, 13):
                full_name = calendar.month_name[number].lower()
                short_name = calendar.month_abbr[number].lower()

                if month_name in (full_name, short_name):
                    month_number = number
                    break

            if month_number is None:
                raise ValueError("Invalid month name.")

            period = pd.Period(
                year=2026,
                month=month_number,
                freq="M"
            )

        return period

    except Exception as error:
        raise ValueError(
            "Invalid month input. Use a month name, "
            "abbreviation, or YYYY-MM format."
        ) from error


target_period = parse_target_month()

MONTH_COLUMN = target_period.strftime("%b")

START_DATE = (
    target_period.start_time.normalize()
    - pd.Timedelta(days=LOOKBACK_DAYS)
).strftime("%Y-%m-%d")

END_DATE = (
    (target_period + 1).start_time
).strftime("%Y-%m-%d")


# ============================================================
# VALIDATE PROJECT DATA
# ============================================================

if not UNIVERSE_DIR.exists():
    raise FileNotFoundError(
        f"Universe folder not found: {UNIVERSE_DIR}"
    )

universe_files = sorted(
    UNIVERSE_DIR.glob("*.csv")
)

if not universe_files:
    raise FileNotFoundError(
        f"No universe CSV files found in: {UNIVERSE_DIR}"
    )


# ============================================================
# IDENTIFY UNIVERSE COLUMNS
# ============================================================

def find_column(df, possible_names):

    for column in possible_names:
        if column in df.columns:
            return column

    return None


# ============================================================
# LOAD AND CLEAN UNIVERSE
# ============================================================

def load_universe(file_path):

    universe = pd.read_csv(file_path)

    if universe.empty:
        raise ValueError("Universe file is empty.")

    company_column = find_column(
        universe,
        ["Company", "company", "Name", "name", "Stock", "stock"]
    )

    ticker_column = find_column(
        universe,
        ["Ticker", "ticker", "Symbol", "symbol", "Code", "code"]
    )

    if ticker_column is None:
        raise ValueError("No ticker column found.")

    if company_column is None:
        universe["Company"] = universe[ticker_column]
        company_column = "Company"

    universe = universe[
        [company_column, ticker_column]
    ].copy()

    universe.columns = ["Company", "Ticker"]

    universe["Company"] = (
        universe["Company"]
        .fillna(universe["Ticker"])
        .astype(str)
        .str.strip()
    )

    universe["Ticker"] = (
        universe["Ticker"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    universe = universe[
        universe["Ticker"] != ""
    ]

    universe = universe.drop_duplicates(
        subset=["Ticker"],
        keep="first"
    )

    if universe.empty:
        raise ValueError("No valid stock tickers found.")

    return universe


# ============================================================
# DOWNLOAD STOCK PRICES
# ============================================================

def download_stock_return(ticker):

    data = yf.download(
        ticker,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        raise ValueError("No price data returned.")

    # Handle yfinance MultiIndex columns.
    if isinstance(data.columns, pd.MultiIndex):

        if "Close" not in data.columns.get_level_values(0):
            raise ValueError("Close price column not found.")

        close = data["Close"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

    else:

        if "Close" not in data.columns:
            raise ValueError("Close price column not found.")

        close = data["Close"]

    close = pd.to_numeric(
        close,
        errors="coerce"
    )

    close.index = pd.to_datetime(
        close.index,
        errors="coerce"
    )

    close = close.dropna()
    close = close[close.index.notna()]
    close = close[close > 0]
    close = close.sort_index()

    close = close[
        ~close.index.duplicated(keep="last")
    ]

    if close.empty:
        raise ValueError("No valid positive closing prices.")

    # Previous month's final available close.
    previous_month_prices = close[
        close.index < target_period.start_time
    ]

    # Target month's available prices.
    target_month_prices = close[
        close.index.to_period("M") == target_period
    ]

    if previous_month_prices.empty:
        raise ValueError(
            "Previous month's closing price unavailable."
        )

    if target_month_prices.empty:
        raise ValueError(
            "Target month's price data unavailable."
        )

    previous_close = float(
        previous_month_prices.iloc[-1]
    )

    current_close = float(
        target_month_prices.iloc[-1]
    )

    monthly_return = (
        (current_close / previous_close) - 1
    ) * 100

    return round(monthly_return, 2)


# ============================================================
# LOAD EXISTING RANKING SAFELY
# ============================================================

def load_existing_ranking(ranking_file, universe):

    if ranking_file.exists():

        ranking = pd.read_csv(ranking_file)

        if "Company" not in ranking.columns:
            raise ValueError(
                f"Company column missing in {ranking_file.name}"
            )

        if "Ticker" not in ranking.columns:
            raise ValueError(
                f"Ticker column missing in {ranking_file.name}"
            )

        ranking["Ticker"] = (
            ranking["Ticker"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # Preserve existing rows and their historical values.
        ranking = ranking.drop_duplicates(
            subset=["Ticker"],
            keep="first"
        )

        existing_tickers = set(
            ranking["Ticker"]
        )

        # Add only genuinely new universe stocks.
        new_stocks = universe[
            ~universe["Ticker"].isin(existing_tickers)
        ]

        ranking = pd.concat(
            [ranking, new_stocks],
            ignore_index=True
        )

    else:

        ranking = universe.copy()

    return ranking


# ============================================================
# PROCESS SECTORS
# ============================================================

def process_sector(universe_file):

    sector = universe_file.stem.lower()

    ranking_file = (
        PROCESSED_DIR /
        f"{sector}_ranking.csv"
    )

    print("\n" + "-" * 55)
    print(f"SECTOR: {sector.upper()}")
    print("-" * 55)

    universe = load_universe(universe_file)

    print(f"Stocks in universe: {len(universe)}")

    # Load existing ranking without wiping history.
    ranking = load_existing_ranking(
        ranking_file,
        universe
    )

    # Ensure target month column exists.
    if MONTH_COLUMN not in ranking.columns:
        ranking[MONTH_COLUMN] = pd.NA

    # Download monthly returns.
    results = []

    successful = 0
    failed = 0

    for _, row in universe.iterrows():

        company = row["Company"]
        ticker = row["Ticker"]

        print(
            f"\nDownloading {company} ({ticker})..."
        )

        try:

            monthly_return = download_stock_return(
                ticker
            )

            results.append({
                "Ticker": ticker,
                MONTH_COLUMN: monthly_return
            })

            successful += 1

            print(
                f"Return: {monthly_return:.2f}%"
            )

        except Exception as error:

            failed += 1

            print(
                f"FAILED: {ticker} — {error}"
            )

    # Validate results before saving.
    if not results:
        raise RuntimeError(
            f"No stock returns generated for {sector}. "
            "Existing ranking file was not changed."
        )

    monthly_results = pd.DataFrame(results)

    # Update only successfully downloaded tickers.
    # Failed downloads retain their previous values.
    ranking = ranking.set_index("Ticker")

    monthly_results = monthly_results.set_index("Ticker")

    for ticker, result in monthly_results.iterrows():
        ranking.loc[ticker, MONTH_COLUMN] = result[MONTH_COLUMN]

    ranking = ranking.reset_index()

    # Keep Company and Ticker first.
    first_columns = ["Company", "Ticker"]

    other_columns = [
        column
        for column in ranking.columns
        if column not in first_columns
    ]

    ranking = ranking[
        first_columns + other_columns
    ]

    ranking[MONTH_COLUMN] = pd.to_numeric(
        ranking[MONTH_COLUMN],
        errors="coerce"
    )

    ranking = ranking.sort_values(
        by=MONTH_COLUMN,
        ascending=False,
        na_position="last"
    )

    # Save ranking.
    ranking.to_csv(
        ranking_file,
        index=False
    )

    print("\nSector summary:")
    print(f"Successful downloads: {successful}")
    print(f"Failed downloads: {failed}")

    print(
        f"Stocks with returns: "
        f"{ranking[MONTH_COLUMN].notna().sum()}"
    )

    print(
        f"Updated ranking: {ranking_file}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 55)
    print("INDIAN EQUITY SECTOR ROTATION RESEARCH")
    print("MODULE 04 - STOCK ANALYSIS")
    print("=" * 55)

    print(
        f"\nTarget month: "
        f"{target_period.strftime('%B %Y')}"
    )

    print(f"Month column: {MONTH_COLUMN}")
    print(f"Download start: {START_DATE}")
    print(f"Download end: {END_DATE}")

    successful_sectors = 0
    failed_sectors = 0

    for universe_file in universe_files:

        try:

            process_sector(universe_file)
            successful_sectors += 1

        except Exception as error:

            failed_sectors += 1

            print(
                f"\nSECTOR FAILED: {universe_file.stem}"
            )

            print(f"Reason: {error}")

    print("\n" + "=" * 55)
    print("MODULE 04 SUMMARY")
    print("=" * 55)

    print(f"Successful sectors: {successful_sectors}")
    print(f"Failed sectors: {failed_sectors}")

    print(
        f"Target month: "
        f"{target_period.strftime('%B %Y')}"
    )

    print("\nMODULE 04 COMPLETED")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
