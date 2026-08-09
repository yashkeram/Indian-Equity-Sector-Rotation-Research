import os
import pandas as pd
import yfinance as yf

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UNIVERSE_FOLDER = os.path.join(
    BASE_DIR, "..", "Data", "Universe"
)

PROCESSED_FOLDER = os.path.join(
    BASE_DIR, "..", "Data", "Processed"
)

MONTH = "Jul"

START_DATE = "2026-07-01"
END_DATE = "2026-08-01"

# ============================================================
# CREATE / VALIDATE DIRECTORIES
# ============================================================

os.makedirs(PROCESSED_FOLDER, exist_ok=True)

if not os.path.exists(UNIVERSE_FOLDER):
    raise FileNotFoundError(
        f"Universe folder not found:\n{UNIVERSE_FOLDER}"
    )

# ============================================================
# FIND UNIVERSE FILES
# ============================================================

universe_files = [
    file
    for file in os.listdir(UNIVERSE_FOLDER)
    if file.endswith(".csv")
]

if not universe_files:
    raise FileNotFoundError(
        f"No CSV files found in:\n{UNIVERSE_FOLDER}"
    )

print("==========================================")
print("MODULE 04 - JULY STOCK ANALYSIS")
print("==========================================")
print()

# ============================================================
# IDENTIFY COLUMNS
# ============================================================

def find_column(df, possible_names):

    for column in possible_names:
        if column in df.columns:
            return column

    return None


# ============================================================
# PROCESS EACH SECTOR
# ============================================================

for universe_file in sorted(universe_files):

    sector = universe_file.replace(".csv", "")

    universe_path = os.path.join(
        UNIVERSE_FOLDER,
        universe_file
    )

    print("------------------------------------------")
    print(f"Processing sector: {sector.upper()}")
    print("------------------------------------------")

    # --------------------------------------------------------
    # LOAD UNIVERSE
    # --------------------------------------------------------

    universe = pd.read_csv(universe_path)

    company_column = find_column(
        universe,
        [
            "Company",
            "company",
            "Name",
            "name",
            "Stock",
            "stock"
        ]
    )

    ticker_column = find_column(
        universe,
        [
            "Ticker",
            "ticker",
            "Symbol",
            "symbol",
            "Code",
            "code"
        ]
    )

    if ticker_column is None:
        print(
            f"No ticker column found in {universe_file}. Skipping."
        )
        continue

    if company_column is None:
        print(
            f"No company column found in {universe_file}. "
            "Using ticker as company name."
        )

        universe["Company"] = universe[ticker_column]

        company_column = "Company"

    # --------------------------------------------------------
    # CLEAN UNIVERSE
    # --------------------------------------------------------

    universe = universe[
        [company_column, ticker_column]
    ].copy()

    universe.columns = [
        "Company",
        "Ticker"
    ]

    universe = universe.dropna(
        subset=["Ticker"]
    )

    universe["Ticker"] = (
        universe["Ticker"]
        .astype(str)
        .str.strip()
    )

    universe = universe[
        universe["Ticker"] != ""
    ]

    universe = universe.drop_duplicates(
        subset=["Ticker"]
    )

    print(
        f"Stocks in universe: {len(universe)}"
    )

    # --------------------------------------------------------
    # LOAD EXISTING RANKING FILE
    # --------------------------------------------------------

    ranking_file = os.path.join(
        PROCESSED_FOLDER,
        f"{sector}_ranking.csv"
    )

    if os.path.exists(ranking_file):

        ranking = pd.read_csv(
            ranking_file
        )

        print(
            f"Existing ranking file found: "
            f"{sector}_ranking.csv"
        )

    else:

        print(
            "Existing ranking file not found. "
            "Creating new file."
        )

        ranking = universe.copy()

    # --------------------------------------------------------
    # DOWNLOAD JULY RETURNS
    # --------------------------------------------------------

    results = []

    for _, row in universe.iterrows():

        company = row["Company"]
        ticker = row["Ticker"]

        print(
            f"  Downloading {company} ({ticker})..."
        )

        try:

            data = yf.download(
                ticker,
                start=START_DATE,
                end=END_DATE,
                auto_adjust=True,
                progress=False
            )

            if data.empty:
                print(
                    f"    No data available for {ticker}"
                )
                continue

            # ------------------------------------------------
            # Handle yfinance MultiIndex
            # ------------------------------------------------

            if isinstance(
                data.columns,
                pd.MultiIndex
            ):

                try:
                    close = data[
                        ("Close", ticker)
                    ]

                except Exception:

                    close = data[
                        "Close"
                    ]

                    if isinstance(
                        close,
                        pd.DataFrame
                    ):
                        close = close.iloc[:, 0]

            else:

                close = data["Close"]

            close = pd.to_numeric(
                close,
                errors="coerce"
            )

            close = close.dropna()

            if close.empty:
                print(
                    f"    No valid closing prices for {ticker}"
                )
                continue

            # ------------------------------------------------
            # July first available close
            # ------------------------------------------------

            july_start_close = float(
                close.iloc[0]
            )

            # ------------------------------------------------
            # July last available close
            # ------------------------------------------------

            july_end_close = float(
                close.iloc[-1]
            )

            # ------------------------------------------------
            # July return
            # ------------------------------------------------

            july_return = (
                (
                    july_end_close
                    /
                    july_start_close
                ) - 1
            ) * 100

            results.append(
                {
                    "Company": company,
                    "Ticker": ticker,
                    "Jul": round(
                        july_return,
                        2
                    )
                }
            )

            print(
                f"    July return: "
                f"{july_return:.2f}%"
            )

        except Exception as error:

            print(
                f"    Error downloading "
                f"{ticker}: {error}"
            )

    # ========================================================
    # CHECK RESULTS
    # ========================================================

    if not results:

        print(
            f"No July results generated for {sector}."
        )

        continue

    july_results = pd.DataFrame(
        results
    )

    # ========================================================
    # UPDATE EXISTING RANKING FILE
    # ========================================================

    # Remove old Jul column if it exists
    if MONTH in ranking.columns:

        ranking = ranking.drop(
            columns=[MONTH]
        )

    # Merge July returns
    ranking = ranking.merge(
        july_results[
            ["Company", "Ticker", MONTH]
        ],
        on=["Company", "Ticker"],
        how="left"
    )

    # ========================================================
    # SORT BY JULY PERFORMANCE
    # ========================================================

    ranking[MONTH] = pd.to_numeric(
        ranking[MONTH],
        errors="coerce"
    )

    ranking = ranking.sort_values(
        by=MONTH,
        ascending=False,
        na_position="last"
    )

    # ========================================================
    # SAVE
    # ========================================================

    ranking.to_csv(
        ranking_file,
        index=False
    )

    print()
    print(
        f"Updated: {ranking_file}"
    )

    print(
        f"July stocks calculated: "
        f"{ranking[MONTH].notna().sum()}"
    )

    print()

# ============================================================
# COMPLETE
# ============================================================

print("==========================================")
print("MODULE 04 COMPLETED")
print("==========================================")
print()
print("July returns have been added to the")
print("existing *_ranking.csv files.")
print()
print("No July-specific ranking CSV was created.")
print()