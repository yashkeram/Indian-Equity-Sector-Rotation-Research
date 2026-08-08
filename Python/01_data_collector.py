import os
import yfinance as yf

# Create Raw folder
os.makedirs("Data/Raw", exist_ok=True)

indices = {
    "nifty50": "^NSEI",
    "bank": "^NSEBANK",
    "it": "^CNXIT",
    "pharma": "^CNXPHARMA",
    "auto": "^CNXAUTO",
    "fmcg": "^CNXFMCG",
    "metal": "^CNXMETAL",
    "realty": "^CNXREALTY"
}

for name, ticker in indices.items():

    print(f"Downloading {name}...")

    df = yf.download(
        ticker,
        start="2026-01-01",
        end="2026-08-01",
        auto_adjust=True,
        progress=False
    )

    # Remove MultiIndex columns if present
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)

    df.reset_index(inplace=True)

    df.to_csv(f"Data/Raw/{name}.csv", index=False)

print("Done!")