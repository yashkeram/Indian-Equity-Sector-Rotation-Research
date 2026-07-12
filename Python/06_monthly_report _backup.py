import os
import json
import pandas as pd

# =====================================
# PATHS
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FOLDER = os.path.join(BASE_DIR, "..", "Data")
PROCESSED_FOLDER = os.path.join(DATA_FOLDER, "Processed")
SUMMARY_FOLDER = os.path.join(DATA_FOLDER, "Summary")
REPORT_FOLDER = os.path.join(DATA_FOLDER, "Reports")

# =====================================
# SETTINGS
# =====================================

MONTH = "Jun"
MONTH_NAME = "June"
REPORT_FILE = "June_2026.json"

# =====================================
# CHECK FOLDERS
# =====================================

print("Current Directory :", BASE_DIR)
print("Processed Folder  :", PROCESSED_FOLDER)
print("Summary Folder    :", SUMMARY_FOLDER)
print("Reports Folder    :", REPORT_FOLDER)

if not os.path.exists(PROCESSED_FOLDER):
    raise FileNotFoundError(f"Processed folder not found:\n{PROCESSED_FOLDER}")

if not os.path.exists(SUMMARY_FOLDER):
    raise FileNotFoundError(f"Summary folder not found:\n{SUMMARY_FOLDER}")

if not os.path.exists(REPORT_FOLDER):
    os.makedirs(REPORT_FOLDER)

# =====================================
# READ SECTOR RETURNS
# =====================================

sector_file = os.path.join(PROCESSED_FOLDER, "sector_returns.csv")

if not os.path.exists(sector_file):
    raise FileNotFoundError("sector_returns.csv not found!")

sector_returns = pd.read_csv(sector_file, index_col=0)

latest = sector_returns.iloc[-1]

# =====================================
# BEST / WORST SECTOR
# =====================================

best_sector = latest.idxmax()
best_sector_return = float(latest.max())

worst_sector = latest.idxmin()
worst_sector_return = float(latest.min())

# =====================================
# READ MONTHLY SUMMARIES
# =====================================

month_folder = os.path.join(SUMMARY_FOLDER, MONTH_NAME)

if not os.path.exists(month_folder):
    raise FileNotFoundError(f"{MONTH_NAME} folder not found:\n{month_folder}")

top_stocks = {}

for file in os.listdir(month_folder):

    if not file.endswith("_summary.csv"):
        continue

    sector = file.replace("_summary.csv", "")

    df = pd.read_csv(os.path.join(month_folder, file))

    top3 = df[df["Rank"].str.contains("Top")]

    top_stocks[sector] = top3["Company"].tolist()

# =====================================
# CREATE REPORT
# =====================================

report = {
    "month": "June 2026",
    "nifty50_return": float(latest["nifty50"]),
    "best_sector": best_sector,
    "best_sector_return": best_sector_return,
    "worst_sector": worst_sector,
    "worst_sector_return": worst_sector_return,
    "sector_returns": latest.to_dict(),
    "top_stocks": top_stocks
}

# =====================================
# SAVE JSON
# =====================================

report_path = os.path.join(REPORT_FOLDER, REPORT_FILE)

with open(report_path, "w") as f:
    json.dump(report, f, indent=4)

print("\n===================================")
print("Monthly Report Created Successfully")
print("===================================")
print(report_path)