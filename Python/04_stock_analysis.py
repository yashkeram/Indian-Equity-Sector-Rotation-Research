import os
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

UNIVERSE_FOLDER = "Data/Universe"
RAW_FOLDER = "Data/Raw"
PROCESSED_FOLDER = "Data/Processed"
CHART_FOLDER = "Outputs/Charts"

TARGET_DATE = "2026-07-31"


# ============================================================
# CREATE OUTPUT DIRECTORIES
# ============================================================

os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(CHART_FOLDER, exist_ok=True)


# ============================================================
# VALIDATE INPUT DIRECTORIES
# ============================================================

if not os.path.exists(UNIVERSE_FOLDER):
    raise FileNotFoundError(
        f"Universe folder not found: {UNIVERSE_FOLDER}"
    )

if not os.path.exists(RAW_FOLDER):
    raise FileNotFoundError(
        f"Raw data folder not found: {RAW_FOLDER}"
    )


# ============================================================
# LOAD UNIVERSE
# ============================================================

universe_files = [
    file
    for file in os.listdir(UNIVERSE_FOLDER)
    if file.endswith(".csv")
]

if not universe_files:
    raise FileNotFoundError(
        f"No CSV files found in {UNIVERSE_FOLDER}"
    )


print("Loading stock universe...")

universe_data = []

for universe_file in universe_files:

    file_path = os.path.join(
        UNIVERSE_FOLDER,
        universe_file
    )

    df = pd.read_csv(file_path)

    df["source_file"] = universe_file

    universe_data.append(df)


universe = pd.concat(
    universe_data,
    ignore_index=True
)


print(f"Universe records loaded: {len(universe)}")


# ============================================================
# DISPLAY UNIVERSE COLUMNS
# ============================================================

print()
print("Universe columns:")
print(list(universe.columns))
print()


# ============================================================
# IDENTIFY STOCK/TICKER COLUMN
# ============================================================

ticker_column = None

possible_ticker_columns = [
    "Ticker",
    "ticker",
    "Symbol",
    "symbol",
    "Stock",
    "stock",
    "Code",
    "code"
]

for column in possible_ticker_columns:

    if column in universe.columns:
        ticker_column = column
        break


# ============================================================
# LOAD RAW SECTOR DATA
# ============================================================

print("Loading sector data...")

sector_results = []

raw_files = [
    file
    for file in os.listdir(RAW_FOLDER)
    if file.endswith(".csv")
]


for file in raw_files:

    file_path = os.path.join(
        RAW_FOLDER,
        file
    )

    try:

        df = pd.read_csv(file_path)

        if "Date" not in df.columns:
            continue

        if "Close" not in df.columns:
            continue

        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

        df["Close"] = pd.to_numeric(
            df["Close"],
            errors="coerce"
        )

        df = df.dropna(
            subset=["Date", "Close"]
        )

        if df.empty:
            continue

        df = df.sort_values("Date")

        # July month-end price
        july_data = df[
            df["Date"] <= pd.Timestamp(TARGET_DATE)
        ]

        if july_data.empty:
            continue

        july_close = july_data.iloc[-1]["Close"]

        # Previous month-end
        previous_data = df[
            df["Date"] < pd.Timestamp("2026-07-01")
        ]

        if previous_data.empty:
            continue

        previous_close = previous_data.iloc[-1]["Close"]

        july_return = (
            (july_close / previous_close) - 1
        ) * 100

        sector_name = file.replace(
            ".csv",
            ""
        )

        sector_results.append(
            {
                "sector": sector_name,
                "june_close": previous_close,
                "july_close": july_close,
                "july_return_pct": july_return
            }
        )

    except Exception as error:

        print(
            f"Skipping {file}: {error}"
        )


# ============================================================
# CREATE SECTOR ANALYSIS DATAFRAME
# ============================================================

if not sector_results:

    raise ValueError(
        "No valid sector data was found for July 2026."
    )


sector_analysis = pd.DataFrame(
    sector_results
)


sector_analysis = sector_analysis.sort_values(
    "july_return_pct",
    ascending=False
)


# ============================================================
# SAVE SECTOR ANALYSIS
# ============================================================

sector_output = os.path.join(
    PROCESSED_FOLDER,
    "july_2026_sector_analysis.csv"
)


sector_analysis.to_csv(
    sector_output,
    index=False
)


# ============================================================
# DISPLAY SECTOR RESULTS
# ============================================================

print()
print("==========================================")
print("JULY 2026 SECTOR ANALYSIS")
print("==========================================")
print(
    sector_analysis[
        [
            "sector",
            "july_return_pct"
        ]
    ].round(2)
)
print()


# ============================================================
# IDENTIFY STRONGEST / WEAKEST SECTORS
# ============================================================

strongest_sector = sector_analysis.iloc[0]

weakest_sector = sector_analysis.iloc[-1]


print(
    f"Strongest sector: "
    f"{strongest_sector['sector']} "
    f"({strongest_sector['july_return_pct']:.2f}%)"
)

print(
    f"Weakest sector: "
    f"{weakest_sector['sector']} "
    f"({weakest_sector['july_return_pct']:.2f}%)"
)


# ============================================================
# CREATE SECTOR PERFORMANCE CHART
# ============================================================

plt.figure(figsize=(10, 6))

plot_data = sector_analysis.sort_values(
    "july_return_pct"
)

plt.bar(
    plot_data["sector"],
    plot_data["july_return_pct"]
)

plt.axhline(
    0,
    linewidth=0.8
)

plt.title(
    "Sector Performance - July 2026"
)

plt.xlabel("Sector")

plt.ylabel(
    "July Return (%)"
)

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()


chart_output = os.path.join(
    CHART_FOLDER,
    "july_2026_sector_analysis.png"
)


plt.savefig(
    chart_output,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# SAVE SUMMARY
# ============================================================

summary = pd.DataFrame(
    [
        {
            "month": TARGET_DATE,
            "strongest_sector":
                strongest_sector["sector"],
            "strongest_return_pct":
                strongest_sector["july_return_pct"],
            "weakest_sector":
                weakest_sector["sector"],
            "weakest_return_pct":
                weakest_sector["july_return_pct"],
            "sectors_analyzed":
                len(sector_analysis)
        }
    ]
)


summary_output = os.path.join(
    PROCESSED_FOLDER,
    "july_2026_analysis_summary.csv"
)


summary.to_csv(
    summary_output,
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("Module 04 completed successfully.")
print()
print("Generated files:")
print(f" - {sector_output}")
print(f" - {summary_output}")
print(f" - {chart_output}")
print()