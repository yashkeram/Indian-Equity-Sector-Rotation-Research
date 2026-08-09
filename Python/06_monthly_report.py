import os
import sys
import json
import pandas as pd


# ============================================================
# MODULE 06 - MONTHLY REPORT GENERATOR
# ============================================================


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.abspath(
    os.path.join(BASE_DIR, "..")
)

DATA_FOLDER = os.path.join(
    PROJECT_ROOT,
    "Data"
)

PROCESSED_FOLDER = os.path.join(
    DATA_FOLDER,
    "Processed"
)

SUMMARY_FOLDER = os.path.join(
    DATA_FOLDER,
    "Summary"
)

REPORT_FOLDER = os.path.join(
    DATA_FOLDER,
    "Reports"
)


# Create Reports folder if it does not exist
os.makedirs(
    REPORT_FOLDER,
    exist_ok=True
)


# ============================================================
# MONTH INPUT
# ============================================================

if len(sys.argv) != 2:

    print()
    print("Usage:")
    print("python Python\\06_monthly_report.py July")
    print()

    sys.exit(1)


MONTH_NAME = sys.argv[1].strip().capitalize()


# ============================================================
# MONTH CONFIGURATION
# ============================================================

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


if MONTH_NAME not in MONTHS:

    print()
    print(f"Invalid month: {MONTH_NAME}")
    print()
    print("Valid months:")

    for month in MONTHS:
        print(f" - {month}")

    sys.exit(1)


# ============================================================
# REPORT FILE
# ============================================================

REPORT_FILE = f"{MONTH_NAME}_2026.json"

REPORT_PATH = os.path.join(
    REPORT_FOLDER,
    REPORT_FILE
)


# ============================================================
# DISPLAY PATHS
# ============================================================

print()
print("==========================================")
print("MODULE 06 - MONTHLY REPORT GENERATOR")
print("==========================================")
print()

print(
    f"Project Root   : {PROJECT_ROOT}"
)

print(
    f"Processed Data : {PROCESSED_FOLDER}"
)

print(
    f"Summary Folder : {SUMMARY_FOLDER}"
)

print(
    f"Report Folder  : {REPORT_FOLDER}"
)

print(
    f"Month          : {MONTH_NAME} 2026"
)

print()


# ============================================================
# VALIDATE PROCESSED FOLDER
# ============================================================

if not os.path.exists(PROCESSED_FOLDER):

    raise FileNotFoundError(
        f"Processed folder not found:\n"
        f"{PROCESSED_FOLDER}"
    )


# ============================================================
# VALIDATE SUMMARY FOLDER
# ============================================================

if not os.path.exists(SUMMARY_FOLDER):

    raise FileNotFoundError(
        f"Summary folder not found:\n"
        f"{SUMMARY_FOLDER}"
    )


# ============================================================
# MONTH SUMMARY FOLDER
# ============================================================

MONTH_SUMMARY_FOLDER = os.path.join(
    SUMMARY_FOLDER,
    MONTH_NAME
)


if not os.path.exists(MONTH_SUMMARY_FOLDER):

    raise FileNotFoundError(
        f"{MONTH_NAME} summary folder not found:\n"
        f"{MONTH_SUMMARY_FOLDER}\n\n"
        f"Run Module 05 first."
    )


# ============================================================
# READ SECTOR RETURNS
# ============================================================

SECTOR_RETURNS_FILE = os.path.join(
    PROCESSED_FOLDER,
    "sector_returns.csv"
)


if not os.path.exists(SECTOR_RETURNS_FILE):

    raise FileNotFoundError(
        "sector_returns.csv not found:\n"
        f"{SECTOR_RETURNS_FILE}"
    )


print("Loading sector returns...")


sector_returns = pd.read_csv(
    SECTOR_RETURNS_FILE,
    index_col=0
)


# ============================================================
# CONVERT INDEX TO DATES
# ============================================================

sector_returns.index = pd.to_datetime(
    sector_returns.index,
    errors="coerce"
)


# Remove invalid dates
sector_returns = sector_returns[
    sector_returns.index.notna()
]


# ============================================================
# FIND REQUESTED MONTH
# ============================================================

target_month_number = (
    MONTHS.index(MONTH_NAME) + 1
)


matching_rows = sector_returns[
    (sector_returns.index.year == 2026)
    &
    (
        sector_returns.index.month
        == target_month_number
    )
]


if matching_rows.empty:

    raise ValueError(
        f"No sector return data found for "
        f"{MONTH_NAME} 2026.\n\n"
        f"Available dates:\n"
        f"{list(sector_returns.index.strftime('%Y-%m-%d'))}"
    )


# Use the latest available row for that month
latest = matching_rows.iloc[-1]


# Convert values to numeric
latest = pd.to_numeric(
    latest,
    errors="coerce"
)


latest = latest.dropna()


# ============================================================
# VALIDATE MONTH DATA
# ============================================================

if latest.empty:

    raise ValueError(
        f"No valid sector returns available "
        f"for {MONTH_NAME} 2026."
    )


# ============================================================
# BEST SECTOR
# ============================================================

# Exclude NIFTY 50 from sector ranking
sector_only = latest.drop(
    labels=["nifty50"],
    errors="ignore"
)


if sector_only.empty:

    raise ValueError(
        "No sector data available after "
        "excluding NIFTY 50."
    )


best_sector = sector_only.idxmax()

best_sector_return = float(
    sector_only.max()
)


# ============================================================
# WORST SECTOR
# ============================================================

worst_sector = sector_only.idxmin()

worst_sector_return = float(
    sector_only.min()
)


# ============================================================
# NIFTY 50
# ============================================================

if "nifty50" in latest.index:

    nifty50_return = float(
        latest["nifty50"]
    )

else:

    nifty50_return = None


# ============================================================
# READ MODULE 05 SUMMARIES
# ============================================================

print()
print(
    f"Reading {MONTH_NAME} stock summaries..."
)
print()


top_stocks = {}

bottom_stocks = {}


summary_files = [
    file
    for file in os.listdir(
        MONTH_SUMMARY_FOLDER
    )
    if file.endswith("_summary.csv")
]


if not summary_files:

    print(
        f"Warning: No summary CSV files found in "
        f"{MONTH_SUMMARY_FOLDER}"
    )


# ============================================================
# PROCESS EACH SECTOR SUMMARY
# ============================================================

for file in sorted(summary_files):

    sector = file.replace(
        "_summary.csv",
        ""
    )


    file_path = os.path.join(
        MONTH_SUMMARY_FOLDER,
        file
    )


    try:

        df = pd.read_csv(
            file_path
        )


        # ====================================================
        # TOP STOCKS
        # ====================================================

        if (
            "Rank" in df.columns
            and "Company" in df.columns
        ):

            top = df[
                df["Rank"]
                .astype(str)
                .str.startswith("Top")
            ]


            top_stocks[sector] = (
                top["Company"]
                .dropna()
                .tolist()
            )


            # =================================================
            # BOTTOM STOCKS
            # =================================================

            bottom = df[
                df["Rank"]
                .astype(str)
                .str.startswith("Bottom")
            ]


            bottom_stocks[sector] = (
                bottom["Company"]
                .dropna()
                .tolist()
            )


        print(
            f"{sector.upper():<10} summary loaded"
        )


    except Exception as error:

        print(
            f"Warning: Could not process "
            f"{file}: {error}"
        )


# ============================================================
# CREATE SECTOR RETURNS DICTIONARY
# ============================================================

sector_returns_dict = {}


for sector, value in latest.items():

    sector_returns_dict[
        str(sector)
    ] = round(
        float(value),
        2
    )


# ============================================================
# CREATE REPORT
# ============================================================

report = {

    "month":
        f"{MONTH_NAME} 2026",

    "year":
        2026,

    "nifty50_return":
        nifty50_return,

    "best_sector":
        str(best_sector),

    "best_sector_return":
        round(
            best_sector_return,
            2
        ),

    "worst_sector":
        str(worst_sector),

    "worst_sector_return":
        round(
            worst_sector_return,
            2
        ),

    "sector_returns":
        sector_returns_dict,

    "top_stocks":
        top_stocks,

    "bottom_stocks":
        bottom_stocks
}


# ============================================================
# SAVE JSON REPORT
# ============================================================

with open(
    REPORT_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        report,
        file,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("==========================================")
print("MONTHLY REPORT CREATED SUCCESSFULLY")
print("==========================================")
print()


print(
    f"Month       : {MONTH_NAME} 2026"
)


if nifty50_return is not None:

    print(
        f"NIFTY 50    : "
        f"{nifty50_return:.2f}%"
    )


print(
    f"Best Sector : "
    f"{str(best_sector).title()} "
    f"({best_sector_return:.2f}%)"
)


print(
    f"Worst Sector: "
    f"{str(worst_sector).title()} "
    f"({worst_sector_return:.2f}%)"
)


print()


print(
    f"Sector data : "
    f"{len(sector_returns_dict)} sectors"
)


print(
    f"Summaries   : "
    f"{len(summary_files)} sectors"
)


print()


print("Report saved to:")

print(
    REPORT_PATH
)

print()