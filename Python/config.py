from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "Data"
RAW_DATA_DIR = DATA_DIR / "Raw"
PROCESSED_DATA_DIR = DATA_DIR / "Processed"

CHARTS_DIR = PROJECT_ROOT / "Charts"
REPORTS_DIR = PROJECT_ROOT / "Reports"
BLOGS_DIR = PROJECT_ROOT / "Blogs"

for directory in [
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    CHARTS_DIR,
    REPORTS_DIR,
    BLOGS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATA SETTINGS
# ============================================================

DATA_START_DATE = "2026-01-01"


# ============================================================
# INDEX DEFINITIONS
# ============================================================

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


INDEX_DISPLAY_NAMES = {
    "nifty50": "NIFTY 50",
    "bank": "NIFTY Bank",
    "it": "NIFTY IT",
    "pharma": "NIFTY Pharma",
    "auto": "NIFTY Auto",
    "fmcg": "NIFTY FMCG",
    "metal": "NIFTY Metal",
    "realty": "NIFTY Realty",
}


# ============================================================
# DYNAMIC DATE FUNCTIONS
# ============================================================

def get_latest_available_date():
    """
    Returns tomorrow's date so that yfinance's exclusive
    end-date convention includes today's market data.
    """

    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    return tomorrow.strftime("%Y-%m-%d")


def get_latest_completed_month():
    """
    Returns the latest completed calendar month.
    """

    today = datetime.now().date()

    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)

    return pd.Period(last_day_previous_month, freq="M")


# ============================================================
# CURRENT ANALYSIS PERIOD
# ============================================================

CURRENT_MONTH = get_latest_completed_month()

CURRENT_MONTH_KEY = CURRENT_MONTH.strftime("%Y-%m")

CURRENT_MONTH_NAME = CURRENT_MONTH.strftime("%B")

CURRENT_YEAR = CURRENT_MONTH.year

DATA_END_DATE = get_latest_available_date()


# ============================================================
# FILE HELPERS
# ============================================================

def raw_file(filename):
    return RAW_DATA_DIR / filename


def processed_file(filename):
    return PROCESSED_DATA_DIR / filename


def chart_file(filename):
    return CHARTS_DIR / filename


def report_file(filename):
    return REPORTS_DIR / filename


def blog_file(filename):
    return BLOGS_DIR / str(CURRENT_YEAR) / filename


# ============================================================
# DEBUG INFORMATION
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("INDIAN EQUITY SECTOR ROTATION")
    print("DYNAMIC CONFIGURATION")
    print("=" * 60)

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data start date: {DATA_START_DATE}")
    print(f"Data end date: {DATA_END_DATE}")

    print(f"Latest completed month: {CURRENT_MONTH_NAME}")
    print(f"Latest completed year: {CURRENT_YEAR}")
    print(f"Month key: {CURRENT_MONTH_KEY}")

    print("\nIndices:")

    for key, ticker in INDICES.items():
        print(f"  {key:10} {ticker}")

    print("=" * 60)