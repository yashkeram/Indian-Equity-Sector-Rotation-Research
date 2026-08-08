import os
import json
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.getcwd()

PROCESSED_FOLDER = os.path.join(
    BASE_DIR,
    "Data",
    "Processed"
)

REPORT_FOLDER = os.path.join(
    BASE_DIR,
    "Outputs",
    "Reports"
)


# ============================================================
# MONTH INPUT
# ============================================================

import sys


if len(sys.argv) != 2:

    print("Usage:")
    print("python Python\\06_monthly_report.py July")
    raise SystemExit


MONTH_NAME = sys.argv[1]


MONTH_MAP = {
    "January": 0,
    "February": 1,
    "March": 2,
    "April": 3,
    "May": 4,
    "June": 5,
    "July": 6,
    "August": 7,
    "September": 8,
    "October": 9,
    "November": 10,
    "December": 11
}


if MONTH_NAME not in MONTH_MAP:

    print("Invalid month!")

    print(
        "Valid months:",
        ", ".join(MONTH_MAP.keys())
    )

    raise SystemExit


MONTH_INDEX = MONTH_MAP[MONTH_NAME]


# ============================================================
# REPORT FILE
# ============================================================

REPORT_FILE = f"{MONTH_NAME.lower()}_2026.json"


# ============================================================
# CREATE REPORT DIRECTORY
# ============================================================

os.makedirs(
    REPORT_FOLDER,
    exist_ok=True
)


# ============================================================
# VALIDATE PROCESSED DATA
# ============================================================

if not os.path.exists(PROCESSED_FOLDER):

    raise FileNotFoundError(
        f"Processed folder not found:\n{PROCESSED_FOLDER}"
    )


print()
print("===================================")
print("MONTHLY SECTOR ROTATION REPORT")
print("===================================")

print(
    "Processed Folder:",
    PROCESSED_FOLDER
)

print(
    "Report Folder:",
    REPORT_FOLDER
)

print(
    "Month:",
    MONTH_NAME,
    "2026"
)


# ============================================================
# READ SECTOR RETURNS
# ============================================================

sector_file = os.path.join(
    PROCESSED_FOLDER,
    "sector_returns.csv"
)


if not os.path.exists(sector_file):

    raise FileNotFoundError(
        f"sector_returns.csv not found:\n{sector_file}"
    )


sector_returns = pd.read_csv(
    sector_file,
    index_col=0
)


# Convert index into datetime where possible

try:

    sector_returns.index = pd.to_datetime(
        sector_returns.index
    )

except Exception:

    pass


# ============================================================
# FIND TARGET MONTH
# ============================================================

target_date = pd.Timestamp(
    f"2026-{MONTH_INDEX + 1:02d}-01"
)


target_rows = sector_returns[
    sector_returns.index.month == target_date.month
]


if target_rows.empty:

    raise ValueError(
        f"No sector return data available for "
        f"{MONTH_NAME} 2026."
    )


latest = target_rows.iloc[-1].dropna()


# Convert values to numeric

latest = pd.to_numeric(
    latest,
    errors="coerce"
).dropna()


# ============================================================
# BEST / WORST SECTOR
# ============================================================

if latest.empty:

    raise ValueError(
        f"No valid sector returns found for "
        f"{MONTH_NAME} 2026."
    )


best_sector = latest.idxmax()

best_sector_return = float(
    latest.max()
)


worst_sector = latest.idxmin()

worst_sector_return = float(
    latest.min()
)


# ============================================================
# NIFTY 50
# ============================================================

nifty50_return = None


if "nifty50" in latest.index:

    nifty50_return = float(
        latest["nifty50"]
    )


# ============================================================
# SECTOR RETURNS
# ============================================================

sector_return_dict = {}

for sector, value in latest.items():

    sector_return_dict[
        str(sector)
    ] = round(
        float(value),
        2
    )


# ============================================================
# EXISTING STOCK RANKINGS
# ============================================================

top_stocks = {}


ranking_files = [
    file
    for file in os.listdir(PROCESSED_FOLDER)
    if file.endswith("_ranking.csv")
]


for file in ranking_files:

    sector = file.replace(
        "_ranking.csv",
        ""
    )

    file_path = os.path.join(
        PROCESSED_FOLDER,
        file
    )

    try:

        df = pd.read_csv(
            file_path
        )

        # Try to identify company column

        company_column = None

        for column in [
            "Company",
            "company",
            "Stock",
            "stock",
            "Symbol",
            "symbol",
            "Ticker",
            "ticker"
        ]:

            if column in df.columns:

                company_column = column

                break


        if company_column is None:

            continue


        # Take the first three stocks
        # from the ranking file

        top3 = df.head(3)

        top_stocks[sector] = (
            top3[company_column]
            .dropna()
            .astype(str)
            .tolist()
        )


    except Exception as error:

        print(
            f"Warning: Could not read {file}: "
            f"{error}"
        )


# ============================================================
# CREATE REPORT
# ============================================================

report = {

    "month": f"{MONTH_NAME} 2026",

    "nifty50_return":
        round(nifty50_return, 2)
        if nifty50_return is not None
        else None,

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
        sector_return_dict,

    "top_stocks":
        top_stocks
}


# ============================================================
# SAVE JSON REPORT
# ============================================================

report_path = os.path.join(
    REPORT_FOLDER,
    REPORT_FILE
)


with open(
    report_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        report,
        file,
        indent=4
    )


# ============================================================
# DISPLAY SUMMARY
# ============================================================

print()
print("===================================")
print("MONTHLY REPORT CREATED SUCCESSFULLY")
print("===================================")

print()

print(
    f"Month: {MONTH_NAME} 2026"
)

print(
    f"NIFTY 50: "
    f"{nifty50_return:.2f}%"
    if nifty50_return is not None
    else "NIFTY 50: N/A"
)

print(
    f"Best Sector: "
    f"{best_sector} "
    f"({best_sector_return:.2f}%)"
)

print(
    f"Worst Sector: "
    f"{worst_sector} "
    f"({worst_sector_return:.2f}%)"
)

print()

print(
    f"Report saved to:"
)

print(
    report_path
)

print()