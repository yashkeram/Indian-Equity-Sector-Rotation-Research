import os
import pandas as pd

# ============================================================
# MODULE 05 - STOCK SUMMARY
# ============================================================
#
# Reads:
#     Data/Processed/*_ranking.csv
#
# Creates:
#     Data/Summary/January/
#     Data/Summary/February/
#     ...
#     Data/Summary/July/
#
# Each month contains:
#     <sector>_summary.csv
#
# Each summary contains:
#     Company, Return, Rank
#
# ============================================================


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# FOLDERS
# ============================================================

RANKING_FOLDER = os.path.join(
    BASE_DIR,
    "Data",
    "Processed"
)

SUMMARY_FOLDER = os.path.join(
    BASE_DIR,
    "Data",
    "Summary"
)


# ============================================================
# MONTHS
# ============================================================

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul"
]


MONTH_NAMES = {
    "Jan": "January",
    "Feb": "February",
    "Mar": "March",
    "Apr": "April",
    "May": "May",
    "Jun": "June",
    "Jul": "July"
}


# ============================================================
# VALIDATE INPUT FOLDER
# ============================================================

if not os.path.exists(RANKING_FOLDER):
    raise FileNotFoundError(
        f"Ranking folder not found:\n{RANKING_FOLDER}"
    )


# ============================================================
# FIND RANKING FILES
# ============================================================

ranking_files = [
    file
    for file in os.listdir(RANKING_FOLDER)
    if file.endswith("_ranking.csv")
]


if not ranking_files:
    raise FileNotFoundError(
        f"No ranking CSV files found in:\n{RANKING_FOLDER}"
    )


# ============================================================
# START
# ============================================================

print()
print("============================================================")
print("MODULE 05 - STOCK SUMMARY")
print("============================================================")
print()

print(
    f"Ranking folder: {RANKING_FOLDER}"
)

print(
    f"Summary folder: {SUMMARY_FOLDER}"
)

print()

# ============================================================
# PROCESS EACH SECTOR
# ============================================================

for file in sorted(ranking_files):

    sector = file.replace(
        "_ranking.csv",
        ""
    )

    file_path = os.path.join(
        RANKING_FOLDER,
        file
    )

    print()
    print("------------------------------------------------------------")
    print(f"Processing sector: {sector.upper()}")
    print("------------------------------------------------------------")

    # --------------------------------------------------------
    # READ RANKING FILE
    # --------------------------------------------------------

    df = pd.read_csv(file_path)

    print(
        f"Stocks in ranking file: {len(df)}"
    )

    # --------------------------------------------------------
    # PROCESS EACH MONTH
    # --------------------------------------------------------

    for month in MONTHS:

        # ----------------------------------------------------
        # Check if month exists
        # ----------------------------------------------------

        if month not in df.columns:

            print(
                f"{month}: column not found - skipped"
            )

            continue

        # ----------------------------------------------------
        # Select company and monthly return
        # ----------------------------------------------------

        temp = df[
            [
                "Company",
                month
            ]
        ].copy()

        # ----------------------------------------------------
        # Convert return values to numbers
        # ----------------------------------------------------

        temp[month] = pd.to_numeric(
            temp[month],
            errors="coerce"
        )

        # ----------------------------------------------------
        # Remove missing values
        # ----------------------------------------------------

        temp = temp.dropna(
            subset=[month]
        )

        if temp.empty:

            print(
                f"{month}: no valid data - skipped"
            )

            continue

        # ----------------------------------------------------
        # Sort highest to lowest
        # ----------------------------------------------------

        temp = temp.sort_values(
            by=month,
            ascending=False
        )

        # ----------------------------------------------------
        # TOP 3
        # ----------------------------------------------------

        top3 = temp.head(3).copy()

        top3["Rank"] = [
            "Top 1",
            "Top 2",
            "Top 3"
        ][:len(top3)]

        # ----------------------------------------------------
        # BOTTOM 3
        # ----------------------------------------------------

        bottom3 = temp.tail(3).copy()

        bottom3 = bottom3.sort_values(
            by=month,
            ascending=True
        )

        bottom3["Rank"] = [
            "Bottom 1",
            "Bottom 2",
            "Bottom 3"
        ][:len(bottom3)]

        # ----------------------------------------------------
        # COMBINE
        # ----------------------------------------------------

        summary = pd.concat(
            [
                top3,
                bottom3
            ],
            ignore_index=True
        )

        # ----------------------------------------------------
        # Rename monthly return column
        # ----------------------------------------------------

        summary = summary.rename(
            columns={
                month: "Return"
            }
        )

        # ----------------------------------------------------
        # Keep clean output structure
        # ----------------------------------------------------

        summary = summary[
            [
                "Company",
                "Return",
                "Rank"
            ]
        ]

        # ----------------------------------------------------
        # MONTH OUTPUT FOLDER
        # ----------------------------------------------------

        month_name = MONTH_NAMES[month]

        output_folder = os.path.join(
            SUMMARY_FOLDER,
            month_name
        )

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        # ----------------------------------------------------
        # OUTPUT FILE
        # ----------------------------------------------------

        output_file = os.path.join(
            output_folder,
            f"{sector}_summary.csv"
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        summary.to_csv(
            output_file,
            index=False
        )

        print(
            f"{month_name:<10} -> "
            f"{os.path.basename(output_file)}"
        )


# ============================================================
# COMPLETE
# ============================================================

print()
print("============================================================")
print("MODULE 05 COMPLETED SUCCESSFULLY")
print("============================================================")
print()

print("Months processed:")
print(
    "January, February, March, April, May, June, July"
)

print()

print(
    "July summaries saved to:"
)

print(
    os.path.join(
        SUMMARY_FOLDER,
        "July"
    )
)

print()