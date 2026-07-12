import os
import pandas as pd
import yfinance as yf

# ==========================================
# Folder Paths
# ==========================================

UNIVERSE_FOLDER = "../Data/Universe"
OUTPUT_FOLDER = "../Data/Processed"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==========================================
# Process Every Sector
# ==========================================

for universe_file in os.listdir(UNIVERSE_FOLDER):

    if not universe_file.endswith(".csv"):
        continue

    sector = universe_file.replace(".csv", "")

    print(f"\n{'='*60}")
    print(f"Processing {sector.upper()} Sector")
    print(f"{'='*60}")

    stocks = pd.read_csv(os.path.join(UNIVERSE_FOLDER, universe_file))

    results = []

    for _, row in stocks.iterrows():

        company = row["Company"]
        ticker = row["Ticker"]

        print(f"Downloading {company}...")

        try:

            df = yf.download(
                ticker,
                start="2026-01-01",
                end="2026-07-01",
                auto_adjust=True,
                progress=False
            )

            if df.empty:
                continue

            if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
                df.columns = df.columns.get_level_values(0)

            df.reset_index(inplace=True)

            df["Date"] = pd.to_datetime(df["Date"])
            df.set_index("Date", inplace=True)

            monthly_close = df["Close"].resample("ME").last()

            monthly_return = (
                monthly_close.pct_change() * 100
            ).round(2)

            row_data = {
                "Company": company,
                "Ticker": ticker
            }

            for date, value in monthly_return.items():

                if pd.isna(value):
                    continue

                month = date.strftime("%b")

                row_data[month] = value

            results.append(row_data)

        except Exception as e:
            print(company)
            print(e)

    ranking = pd.DataFrame(results)

    month_order = [
        "Company",
        "Ticker",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun"
    ]

    ranking = ranking.reindex(columns=month_order)

    # Sort using latest month
    ranking = ranking.sort_values(
        by="Jun",
        ascending=False
    )

    output = os.path.join(
        OUTPUT_FOLDER,
        f"{sector}_ranking.csv"
    )

    ranking.to_csv(output, index=False)

    print(f"Saved -> {output}")

print("\n")
print("="*70)
print("ALL SECTOR MONTHLY RANKINGS GENERATED")
print("="*70)