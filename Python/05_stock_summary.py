import os
import pandas as pd

# -----------------------------
# Folder Paths
# -----------------------------

RANKING_FOLDER = "../Data/Processed"
SUMMARY_FOLDER = "../Data/Summary"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

MONTH_NAMES = {
    "Jan": "January",
    "Feb": "February",
    "Mar": "March",
    "Apr": "April",
    "May": "May",
    "Jun": "June"
}

# -----------------------------
# Read every ranking file
# -----------------------------

for file in os.listdir(RANKING_FOLDER):

    if not file.endswith("_ranking.csv"):
        continue

    sector = file.replace("_ranking.csv", "")

    df = pd.read_csv(os.path.join(RANKING_FOLDER, file))

    print(f"\nProcessing {sector.upper()}")

    for month in MONTHS:

        if month not in df.columns:
            continue

        temp = df[["Company", month]].copy()

        temp = temp.dropna()

        temp = temp.sort_values(
            by=month,
            ascending=False
        )

        top3 = temp.head(3).copy()
        top3["Rank"] = [
            "Top 1",
            "Top 2",
            "Top 3"
        ]

        bottom3 = temp.tail(3).copy()
        bottom3 = bottom3.sort_values(
            by=month,
            ascending=True
        )

        bottom3["Rank"] = [
            "Bottom 1",
            "Bottom 2",
            "Bottom 3"
        ]

        summary = pd.concat(
            [top3, bottom3],
            ignore_index=True
        )

        output_folder = os.path.join(
            SUMMARY_FOLDER,
            MONTH_NAMES[month]
        )

        os.makedirs(output_folder, exist_ok=True)

        output_file = os.path.join(
            output_folder,
            f"{sector}_summary.csv"
        )

        summary.to_csv(
            output_file,
            index=False
        )

print("\nAll summaries created successfully.")