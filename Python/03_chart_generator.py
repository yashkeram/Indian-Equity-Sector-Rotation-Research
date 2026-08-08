import os
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FOLDER = "Data/Raw"
OUTPUT_FOLDER = "Outputs/Charts"

TARGET_MONTH = "2026-07-31"
MONTH_NAME = "July 2026"

OUTPUT_FILE = "july_2026_sector_performance.png"


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ============================================================
# READ SECTOR DATA
# ============================================================

monthly_returns = {}

for file in os.listdir(DATA_FOLDER):

    if not file.endswith(".csv"):
        continue

    file_path = os.path.join(DATA_FOLDER, file)

    df = pd.read_csv(file_path)

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


# ============================================================
# CHECK TARGET MONTH
# ============================================================

if TARGET_MONTH not in returns.index.strftime("%Y-%m-%d"):
    raise ValueError(
        f"{TARGET_MONTH} is not available in the calculated monthly returns."
    )


july = returns.loc[TARGET_MONTH]

july = july.dropna()

july = july.sort_values()


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print(f"Sector Performance - {MONTH_NAME}")
print("--------------------------------")
print(july.round(2))
print()


# ============================================================
# CREATE CHART
# ============================================================

plt.figure(figsize=(10, 6))

july.plot(kind="bar")

plt.title(f"Sector Performance - {MONTH_NAME}")
plt.ylabel("Monthly Return (%)")
plt.xlabel("Sector")

plt.axhline(0, linewidth=0.8)

plt.tight_layout()


# ============================================================
# SAVE CHART
# ============================================================

output_path = os.path.join(
    OUTPUT_FOLDER,
    OUTPUT_FILE
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# COMPLETE
# ============================================================

print("Chart saved successfully!")
print(f"Output: {output_path}")