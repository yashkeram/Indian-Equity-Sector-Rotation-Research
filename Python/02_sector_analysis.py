import os
import pandas as pd

# Folder containing sector CSV files
DATA_FOLDER = "Data/Raw"

# Get all CSV files
files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]

# Empty DataFrame to store results
results = pd.DataFrame()

for file in files:

    # Read CSV
    df = pd.read_csv(os.path.join(DATA_FOLDER, file))

    # Convert Date column
    df["Date"] = pd.to_datetime(df["Date"])

    # Set Date as index
    df.set_index("Date", inplace=True)

    # Calculate monthly closing price
    monthly_close = df["Close"].resample("ME").last()

    # Calculate monthly returns
    monthly_return = monthly_close.pct_change() * 100

    # Store in results
    sector_name = file.replace(".csv", "")
    results[sector_name] = monthly_return

# Round values
results = results.round(2)

print(results)

# Save results
results.to_csv("Data/Processed/sector_returns.csv")

print("Sector returns saved successfully!")

