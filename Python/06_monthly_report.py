
from pathlib import Path
import sys
import json

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "Data"
PROCESSED_DIR = DATA_DIR / "Processed"
SUMMARY_DIR = DATA_DIR / "Summary"
REPORT_DIR = DATA_DIR / "Reports"

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONFIGURATION
# ============================================================

YEAR = 2026

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
    "December",
]

# Expected sector index names.
EXPECTED_SECTORS = [
    "auto",
    "bank",
    "it",
    "pharma",
    "fmcg",
    "metal",
    "realty",
]

# Existing JSON field names are preserved for Module 07.
REPORT_VERSION = "2.0"


# ============================================================
# MONTH INPUT
# ============================================================

def get_target_month():

    if len(sys.argv) != 2:

        print(
            "\nUsage: python Python/06_monthly_report.py October"
        )

        print("\nValid months:")

        for month in MONTHS:
            print(f" - {month}")

        raise SystemExit(1)

    month_name = sys.argv[1].strip().capitalize()

    if month_name not in MONTHS:
        raise ValueError(
            f"Invalid month: {month_name}"
        )

    return month_name


# ============================================================
# LOAD SECTOR RETURNS
# ============================================================

def load_sector_returns(month_name):

    file_path = PROCESSED_DIR / "sector_returns.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Sector returns file not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError(
            "Sector returns file is empty."
        )

    if "Date" not in df.columns:
        # Support older CSV files where Date was saved as index.
        first_column = df.columns[0]

        if first_column.startswith("Unnamed"):
            df = df.rename(
                columns={first_column: "Date"}
            )
        else:
            raise ValueError(
                "Date column not found in sector_returns.csv."
            )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Date"]
    )

    if df.empty:
        raise ValueError(
            "No valid dates found in sector_returns.csv."
        )

    df = df.sort_values("Date")

    target_month_number = (
        MONTHS.index(month_name) + 1
    )

    matching = df[
        (df["Date"].dt.year == YEAR)
        & (df["Date"].dt.month == target_month_number)
    ]

    if matching.empty:
        raise ValueError(
            f"No sector returns found for {month_name} {YEAR}."
        )

    latest = matching.iloc[-1]

    numeric_values = latest.drop(
        labels=["Date"],
        errors="ignore"
    )

    numeric_values = pd.to_numeric(
        numeric_values,
        errors="coerce"
    )

    numeric_values = numeric_values.dropna()

    if numeric_values.empty:
        raise ValueError(
            f"No valid sector returns for {month_name} {YEAR}."
        )

    return numeric_values


# ============================================================
# VALIDATE SECTOR RETURNS
# ============================================================

def validate_sector_returns(latest):

    warnings = []

    available_sectors = [
        str(column).lower()
        for column in latest.index
    ]

    expected_indices = [
        "nifty50",
        *EXPECTED_SECTORS
    ]

    missing_indices = [
        sector
        for sector in expected_indices
        if sector not in available_sectors
    ]

    if missing_indices:
        warnings.append(
            "Missing index returns: "
            + ", ".join(missing_indices)
        )

    if "nifty50" not in available_sectors:
        raise ValueError(
            "NIFTY 50 return is missing. "
            "Cannot create the monthly report."
        )

    available_sector_values = latest.drop(
        labels=["nifty50"],
        errors="ignore"
    )

    if available_sector_values.empty:
        raise ValueError(
            "No sector returns available."
        )

    return warnings, available_sector_values


# ============================================================
# LOAD STOCK SUMMARIES
# ============================================================

def load_stock_summaries(month_name):

    month_folder = SUMMARY_DIR / month_name

    if not month_folder.exists():
        raise FileNotFoundError(
            f"{month_name} summary folder not found: "
            f"{month_folder}\n"
            "Run Module 05 first."
        )

    summary_files = sorted(
        month_folder.glob("*_summary.csv")
    )

    if not summary_files:
        raise FileNotFoundError(
            f"No summary CSV files found in: {month_folder}"
        )

    top_stocks = {}
    bottom_stocks = {}

    loaded_sectors = []
    warnings = []

    for file_path in summary_files:

        sector = file_path.stem.replace(
            "_summary",
            ""
        ).lower()

        try:

            df = pd.read_csv(file_path)

            required_columns = [
                "Company",
                "Return",
                "Rank",
            ]

            missing_columns = [
                column
                for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:
                raise ValueError(
                    f"Missing columns: {missing_columns}"
                )

            df["Company"] = (
                df["Company"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            df["Return"] = pd.to_numeric(
                df["Return"],
                errors="coerce"
            )

            df["Rank"] = (
                df["Rank"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            df = df[
                (df["Company"] != "")
                & df["Return"].notna()
            ]

            top = df[
                df["Rank"].str.startswith("Top")
            ]

            bottom = df[
                df["Rank"].str.startswith("Bottom")
            ]

            if top.empty and bottom.empty:
                raise ValueError(
                    "No valid Top or Bottom stock entries."
                )

            top_stocks[sector] = (
                top["Company"].tolist()
            )

            bottom_stocks[sector] = (
                bottom["Company"].tolist()
            )

            loaded_sectors.append(sector)

            print(
                f"{sector.upper():<12} summary loaded"
            )

        except Exception as error:

            warnings.append(
                f"{file_path.name}: {error}"
            )

            print(
                f"WARNING: Could not process "
                f"{file_path.name}: {error}"
            )

    return (
        top_stocks,
        bottom_stocks,
        loaded_sectors,
        warnings,
        len(summary_files),
    )


# ============================================================
# BUILD REPORT
# ============================================================

def build_report(month_name, latest, sector_only,
                 top_stocks, bottom_stocks,
                 loaded_sectors, warnings,
                 summary_file_count):

    best_sector = sector_only.idxmax()
    worst_sector = sector_only.idxmin()

    nifty50_return = float(
        latest["nifty50"]
    )

    sector_returns_dict = {}

    for sector, value in latest.items():

        sector_returns_dict[str(sector)] = round(
            float(value),
            2
        )

    expected_sector_count = len(EXPECTED_SECTORS)

    missing_summaries = [
        sector
        for sector in EXPECTED_SECTORS
        if sector not in loaded_sectors
    ]

    if missing_summaries:
        warnings.append(
            "Missing or unprocessed stock summaries: "
            + ", ".join(missing_summaries)
        )

    if summary_file_count < expected_sector_count:
        warnings.append(
            f"Expected {expected_sector_count} sector summary files, "
            f"but found {summary_file_count}."
        )

    complete = (
        len(missing_summaries) == 0
        and all(
            sector in sector_returns_dict
            for sector in EXPECTED_SECTORS
        )
    )

    report = {

        # ----------------------------------------------------
        # EXISTING FIELDS - KEEP FOR MODULE 07
        # ----------------------------------------------------

        "month": f"{month_name} {YEAR}",

        "year": YEAR,

        "nifty50_return": round(
            nifty50_return,
            2
        ),

        "best_sector": str(best_sector),

        "best_sector_return": round(
            float(sector_only.max()),
            2
        ),

        "worst_sector": str(worst_sector),

        "worst_sector_return": round(
            float(sector_only.min()),
            2
        ),

        "sector_returns": sector_returns_dict,

        "top_stocks": top_stocks,

        "bottom_stocks": bottom_stocks,

        # ----------------------------------------------------
        # ADDITIONAL DATA QUALITY METADATA
        # ----------------------------------------------------

        "report_version": REPORT_VERSION,

        "data_quality": {

            "status": (
                "complete"
                if complete
                else "incomplete"
            ),

            "expected_sector_count": expected_sector_count,

            "available_sector_count": sum(
                sector in sector_returns_dict
                for sector in EXPECTED_SECTORS
            ),

            "expected_summary_count": expected_sector_count,

            "loaded_summary_count": len(loaded_sectors),

            "missing_summaries": missing_summaries,

            "warnings": warnings,
        },
    }

    return report


# ============================================================
# SAVE JSON REPORT
# ============================================================

def save_report(report, month_name):

    report_path = (
        REPORT_DIR /
        f"{month_name}_{YEAR}.json"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
            allow_nan=False
        )

    return report_path


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 55)
    print("INDIAN EQUITY SECTOR ROTATION RESEARCH")
    print("MODULE 06 - MONTHLY REPORT GENERATOR")
    print("=" * 55)

    month_name = get_target_month()

    print(f"\nTarget month: {month_name} {YEAR}")

    # Load sector returns.
    latest = load_sector_returns(
        month_name
    )

    # Validate sector returns.
    warnings, sector_only = validate_sector_returns(
        latest
    )

    # Load stock summaries.
    (
        top_stocks,
        bottom_stocks,
        loaded_sectors,
        summary_warnings,
        summary_file_count,
    ) = load_stock_summaries(
        month_name
    )

    warnings.extend(summary_warnings)

    # Build report.
    report = build_report(
        month_name,
        latest,
        sector_only,
        top_stocks,
        bottom_stocks,
        loaded_sectors,
        warnings,
        summary_file_count,
    )

    # Save report.
    report_path = save_report(
        report,
        month_name
    )

    # Display results.
    print("\n" + "=" * 55)
    print("MONTHLY REPORT GENERATED")
    print("=" * 55)

    print(
        f"\nMonth: {report['month']}"
    )

    print(
        f"NIFTY 50: {report['nifty50_return']:.2f}%"
    )

    print(
        f"Best sector: {report['best_sector']} "
        f"({report['best_sector_return']:.2f}%)"
    )

    print(
        f"Worst sector: {report['worst_sector']} "
        f"({report['worst_sector_return']:.2f}%)"
    )

    print(
        f"\nData quality: "
        f"{report['data_quality']['status'].upper()}"
    )

    print(
        f"Sector summaries loaded: "
        f"{report['data_quality']['loaded_summary_count']}/"
        f"{report['data_quality']['expected_summary_count']}"
    )

    if warnings:

        print("\nWarnings:")

        for warning in warnings:
            print(f"- {warning}")

    print(
        f"\nReport saved to: {report_path}"
    )

    print("\nMODULE 06 COMPLETED")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
