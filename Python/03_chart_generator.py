import os
import pandas as pd

try:
    import matplotlib

    # Use a non-interactive backend
    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

except Exception:
    class _DummyPlt:
        def figure(self, *args, **kwargs):
            return None

        def savefig(self, *args, **kwargs):
            return None

        def show(self, *args, **kwargs):
            return None

    plt = _DummyPlt()


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FOLDER = os.path.join(BASE_DIR, "..", "Data", "Raw")
CHARTS_FOLDER = os.path.join(BASE_DIR, "..", "Charts")

os.makedirs(CHARTS_FOLDER, exist_ok=True)


# ============================================================
# SETTINGS
# ============================================================

TARGET_MONTH = "2026-07-31"


# ============================================================
# CHECK DATA FOLDER
# ============================================================

if not os.path.exists(DATA_FOLDER):
    raise FileNotFoundError(
        f"Data folder not found:\n{os.path.abspath(DATA_FOLDER)}"
    )


# ============================================================
# READ ALL SECTOR FILES
# ============================================================

monthly_returns = {}

for file in os.listdir(DATA_FOLDER):

    if not file.endswith(".csv"):
        continue

    file_path = os.path.join(DATA_FOLDER, file)

    df = pd.read_csv(file_path)

    if "Date" not in df.columns or "Close" not in df.columns:
        print(f"Skipping invalid file: {file}")
        continue

    df["Date"] = pd.to_datetime(df["Date"])

    df.set_index("Date", inplace=True)

    monthly_close = df["Close"].resample("ME").last()

    monthly_return = monthly_close.pct_change() * 100

    sector_name = file.replace(".csv", "")

    monthly_returns[sector_name] = monthly_return


# ============================================================
# CREATE RETURNS DATAFRAME
# ============================================================

returns = pd.DataFrame(monthly_returns)

if returns.empty:
    raise ValueError("No sector return data was generated.")


# ============================================================
# SELECT JULY 2026
# ============================================================

target_date = pd.Timestamp(TARGET_MONTH)

if target_date not in returns.index:
    raise ValueError(
        f"{TARGET_MONTH} not found in available monthly data.\n"
        f"Available dates: {list(returns.index)}"
    )

july = returns.loc[target_date].dropna()

# Remove NIFTY 50 from sector-only chart
sector_returns = july.drop(
    labels=["nifty50"],
    errors="ignore"
)

# Sort from worst to best
sector_returns = sector_returns.sort_values()


# ============================================================
# CHART 1 — JULY SECTOR PERFORMANCE
# ============================================================

plt.figure(figsize=(10, 6))

sector_returns.plot(kind="bar")

plt.axhline(0, linewidth=0.8)

plt.title("Indian Equity Sector Performance — July 2026")
plt.ylabel("Monthly Return (%)")
plt.xlabel("Sector")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()


chart_path = os.path.join(
    CHARTS_FOLDER,
    "july_2026_sector_performance.png"
)

plt.savefig(
    chart_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(f"Saved: {chart_path}")


# ============================================================
# CHART 2 — NIFTY 50 + SECTORS
# ============================================================

comparison = july.sort_values()

plt.figure(figsize=(11, 6))

comparison.plot(kind="bar")

plt.axhline(0, linewidth=0.8)

plt.title("Indian Equity Market Performance — July 2026")
plt.ylabel("Monthly Return (%)")
plt.xlabel("Index / Sector")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()


comparison_path = os.path.join(
    CHARTS_FOLDER,
    "july_2026_sector_analysis.png"
)

plt.savefig(
    comparison_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(f"Saved: {comparison_path}")


# ============================================================
# COMPLETE
# ============================================================

print("\n===================================")
print("Chart Generation Completed")
print("===================================")
print(f"Output folder: {os.path.abspath(CHARTS_FOLDER)}")