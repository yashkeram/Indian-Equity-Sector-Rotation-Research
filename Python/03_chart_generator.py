
from pathlib import Path

import pandas as pd
import matplotlib

# Use a non-interactive backend.
matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "Data" / "Processed"
CHARTS_DIR = BASE_DIR / "Charts"

INPUT_FILE = PROCESSED_DIR / "sector_returns.csv"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

# Change this value to generate charts for another month.
# Format: YYYY-MM
TARGET_MONTH = "2026-10"


# ============================================================
# LOAD MONTHLY RETURNS
# ============================================================

def load_monthly_returns():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Monthly returns file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        raise ValueError(
            "The monthly returns file is empty."
        )

    if "Date" not in df.columns:
        raise ValueError(
            "The monthly returns file must contain a Date column."
        )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df = df.dropna(subset=["Date"])

    if df.empty:
        raise ValueError(
            "No valid dates were found in the monthly returns file."
        )

    df = (
        df.sort_values("Date")
        .drop_duplicates(subset=["Date"], keep="last")
        .set_index("Date")
    )

    df = df.apply(
        pd.to_numeric,
        errors="coerce"
    )

    return df


# ============================================================
# SELECT TARGET MONTH
# ============================================================

def select_month(df):

    try:
        target_period = pd.Period(
            TARGET_MONTH,
            freq="M"
        )
    except ValueError:
        raise ValueError(
            "Invalid TARGET_MONTH format. Use YYYY-MM."
        )

    matching_rows = (
        df.index.to_period("M") == target_period
    )

    if not matching_rows.any():
        available_months = sorted(
            df.index.to_period("M").astype(str).unique()
        )

        raise ValueError(
            f"No data found for {TARGET_MONTH}.\n"
            f"Available months: {available_months}"
        )

    monthly_data = df.loc[matching_rows].iloc[-1]

    monthly_data = monthly_data.dropna()

    if monthly_data.empty:
        raise ValueError(
            f"No valid returns found for {TARGET_MONTH}."
        )

    return monthly_data


# ============================================================
# GENERATE CHARTS
# ============================================================

def generate_charts(monthly_data):

    month_label = pd.Period(
        TARGET_MONTH,
        freq="M"
    ).strftime("%B %Y")

    filename_month = pd.Period(
        TARGET_MONTH,
        freq="M"
    ).strftime("%B_%Y").lower()

    # --------------------------------------------------------
    # CHART 1: SECTOR PERFORMANCE
    # --------------------------------------------------------

    sector_returns = monthly_data.drop(
        labels=["nifty50"],
        errors="ignore"
    )

    sector_returns = sector_returns.sort_values()

    if sector_returns.empty:
        raise ValueError(
            "No sector return data available for the chart."
        )

    plt.figure(figsize=(10, 6))

    sector_returns.plot(kind="bar")

    plt.axhline(0, linewidth=0.8)

    plt.title(
        f"Indian Equity Sector Performance — {month_label}"
    )

    plt.ylabel("Monthly Return (%)")
    plt.xlabel("Sector")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    sector_chart = (
        CHARTS_DIR /
        f"{filename_month}_sector_performance.png"
    )

    plt.savefig(
        sector_chart,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # --------------------------------------------------------
    # CHART 2: NIFTY 50 AND SECTOR COMPARISON
    # --------------------------------------------------------

    comparison = monthly_data.sort_values()

    plt.figure(figsize=(11, 6))

    comparison.plot(kind="bar")

    plt.axhline(0, linewidth=0.8)

    plt.title(
        f"Indian Equity Market Performance — {month_label}"
    )

    plt.ylabel("Monthly Return (%)")
    plt.xlabel("Index / Sector")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    comparison_chart = (
        CHARTS_DIR /
        f"{filename_month}_market_comparison.png"
    )

    plt.savefig(
        comparison_chart,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # --------------------------------------------------------
    # VERIFY OUTPUT FILES
    # --------------------------------------------------------

    for chart in [sector_chart, comparison_chart]:

        if not chart.exists() or chart.stat().st_size == 0:
            raise RuntimeError(
                f"Chart generation failed: {chart}"
            )

        print(f"Saved: {chart}")


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 55)
    print("INDIAN EQUITY SECTOR ROTATION RESEARCH")
    print("MODULE 03 - CHART GENERATOR")
    print("=" * 55)

    print(f"\nTarget month: {TARGET_MONTH}")

    monthly_returns = load_monthly_returns()

    selected_month = select_month(
        monthly_returns
    )

    print("\nMonthly returns:")
    print(selected_month.round(2).to_string())

    generate_charts(selected_month)

    print("\n" + "=" * 55)
    print("CHART GENERATION COMPLETED")
    print("=" * 55)

    print(f"Output folder: {CHARTS_DIR}")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
