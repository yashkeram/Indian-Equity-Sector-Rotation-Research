import os
import sys
import json
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

PROCESSED_FOLDER = os.path.join(
    PROJECT_DIR,
    "Data",
    "Processed"
)

SUMMARY_FOLDER = os.path.join(
    PROJECT_DIR,
    "Data",
    "Summary"
)

REPORT_FOLDER = os.path.join(
    PROJECT_DIR,
    "Data",
    "Reports"
)


# ============================================================
# MONTHS
# ============================================================

VALID_MONTHS = [
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


# ============================================================
# MONTH INPUT
# ============================================================

if len(sys.argv) != 2:
    print()
    print("Usage:")
    print("python Python\\06_monthly_report.py <Month>")
    print()
    print("Example:")
    print("python Python\\06_monthly_report.py July")
    print()
    sys.exit(1)


MONTH_NAME = sys.argv[1].strip().capitalize()


if MONTH_NAME not in VALID_MONTHS:
    print()
    print(f"Invalid month: {MONTH_NAME}")
    print()
    print("Valid months:")
    print(", ".join(VALID_MONTHS))
    print()
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
print("==============================================")
print("INDIAN EQUITY SECTOR ROTATION - MONTHLY REPORT")
print("==============================================")
print()
print("Project Directory :", PROJECT_DIR)
print("Processed Folder  :", PROCESSED_FOLDER)
print("Summary Folder    :", SUMMARY_FOLDER)
print("Report Folder     :", REPORT_FOLDER)
print("Month             :", f"{MONTH_NAME} 2026")
print()


# ============================================================
# CHECK PROCESSED FOLDER
# ============================================================

if not os.path.exists(PROCESSED_FOLDER):
    raise FileNotFoundError(
        f"Processed folder not found:\n{PROCESSED_FOLDER}"
    )


# ============================================================
# CHECK SECTOR RETURNS FILE
# ============================================================

SECTOR_RETURNS_FILE = os.path.join(
    PROCESSED_FOLDER,
    "sector_returns.csv"
)

if not os.path.exists(SECTOR_RETURNS_FILE):
    raise FileNotFoundError(
        f"sector_returns.csv not found:\n{SECTOR_RETURNS_FILE}"
    )


# ============================================================
# READ SECTOR RETURNS
# ============================================================

sector_returns = pd.read_csv(
    SECTOR_RETURNS_FILE
)

if sector_returns.empty:
    raise ValueError(
        "sector_returns.csv is empty."
    )


# ============================================================
# IDENTIFY DATE COLUMN
# ============================================================

date_column = sector_returns.columns[0]

sector_returns[date_column] = pd.to_datetime(
    sector_returns[date_column],
    errors="coerce"
)

sector_returns = sector_returns.dropna(
    subset=[date_column]
)

sector_returns.set_index(
    date_column,
    inplace=True
)


# ============================================================
# FIND REQUESTED MONTH
# ============================================================

target_year = 2026
target_month = pd.Timestamp(
    year=target_year,
    month=VALID_MONTHS.index(MONTH_NAME) + 1,
    day=1
)


matching_rows = sector_returns[
    (sector_returns.index.year == target_year)
    &
    (sector_returns.index.month == target_month.month)
]


if matching_rows.empty:
    raise ValueError(
        f"No sector-return data found for {MONTH_NAME} 2026."
    )


# Use the last available observation for that month.
latest = matching_rows.iloc[-1].copy()


# ============================================================
# CLEAN NUMERIC VALUES
# ============================================================

latest = pd.to_numeric(
    latest,
    errors="coerce"
).dropna()


if latest.empty:
    raise ValueError(
        f"No valid sector-return values found for {MONTH_NAME} 2026."
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

sector_only = latest.drop(
    labels=["nifty50"],
    errors="ignore"
)


if sector_only.empty:
    raise ValueError(
        "No sector data available after removing NIFTY 50."
    )


# ============================================================
# BEST SECTOR
# ============================================================

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
# MONTHLY STOCK SUMMARIES
# ============================================================

month_folder = os.path.join(
    SUMMARY_FOLDER,
    MONTH_NAME
)


top_stocks = {}


if os.path.exists(month_folder):

    for filename in sorted(
        os.listdir(month_folder)
    ):

        if not filename.endswith(
            "_summary.csv"
        ):
            continue

        sector = filename.replace(
            "_summary.csv",
            ""
        )

        summary_path = os.path.join(
            month_folder,
            filename
        )

        try:

            df = pd.read_csv(
                summary_path
            )

            if (
                "Rank" not in df.columns
                or "Company" not in df.columns
            ):
                print(
                    f"Warning: Missing Rank/Company columns in {filename}"
                )
                continue

            rank_values = (
                df["Rank"]
                .astype(str)
                .str.strip()
            )

            top_rows = df[
                rank_values.str.contains(
                    "Top",
                    case=False,
                    na=False
                )
            ]

            companies = (
                top_rows["Company"]
                .dropna()
                .astype(str)
                .tolist()
            )

            if companies:
                top_stocks[sector] = companies

        except Exception as error:

            print(
                f"Warning: Could not process {filename}: {error}"
            )

else:

    print(
        f"Warning: Summary folder not found:\n{month_folder}"
    )


# ============================================================
# CONVERT SECTOR RETURNS TO DICTIONARY
# ============================================================

sector_returns_dict = {
    str(sector): round(
        float(value),
        2
    )
    for sector, value in latest.items()
}


# ============================================================
# CREATE REPORT
# ============================================================

report = {

    "month": f"{MONTH_NAME} 2026",

    "nifty50_return": (
        round(nifty50_return, 2)
        if nifty50_return is not None
        else None
    ),

    "best_sector": str(
        best_sector
    ),

    "best_sector_return": round(
        best_sector_return,
        2
    ),

    "worst_sector": str(
        worst_sector
    ),

    "worst_sector_return": round(
        worst_sector_return,
        2
    ),

    "sector_returns": sector_returns_dict,

    "top_stocks": top_stocks
}


# ============================================================
# CREATE REPORT FOLDER
# ============================================================

os.makedirs(
    REPORT_FOLDER,
    exist_ok=True
)


# ============================================================
# SAVE JSON
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
# FINAL OUTPUT
# ============================================================

print()
print("==============================================")
print("MONTHLY REPORT CREATED SUCCESSFULLY")
print("==============================================")
print()
print(
    f"Month        : {MONTH_NAME} 2026"
)

if nifty50_return is not None:
    print(
        f"NIFTY 50     : {nifty50_return:.2f}%"
    )

print(
    f"Best Sector  : {best_sector}"
    f" ({best_sector_return:.2f}%)"
)

print(
    f"Worst Sector : {worst_sector}"
    f" ({worst_sector_return:.2f}%)"
)

print()
print("Report saved to:")
print(REPORT_PATH)
print()