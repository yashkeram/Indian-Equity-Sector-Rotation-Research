import os
import pandas as pd
try:
    import matplotlib
    # Use a non-interactive backend if display isn't available
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:
    # Fallback: create a dummy plt with minimal API to avoid hard failure in editors
    class _DummyPlt:
        def figure(self, *a, **k):
            return None
        def savefig(self, *a, **k):
            return None
        def show(self, *a, **k):
            return None
    plt = _DummyPlt()

# Read all sector files
DATA_FOLDER = "../Data/Raw"

monthly_returns = {}

for file in os.listdir(DATA_FOLDER):

    if file.endswith(".csv"):

        df = pd.read_csv(os.path.join(DATA_FOLDER, file))

        df["Date"] = pd.to_datetime(df["Date"])

        df.set_index("Date", inplace=True)

        monthly_close = df["Close"].resample("ME").last()

        monthly_return = monthly_close.pct_change() * 100

        monthly_returns[file.replace(".csv", "")] = monthly_return

# Create DataFrame
returns = pd.DataFrame(monthly_returns)

# Select April 2026
april = returns.loc["2026-04-30"]

# Sort sectors
april = april.sort_values()

# Plot
plt.figure(figsize=(10,6))

april.plot(kind="bar")

plt.title("Sector Performance - April 2026")

plt.ylabel("Monthly Return (%)")

plt.xlabel("Sector")

plt.tight_layout()

# Save chart
os.makedirs("../Charts", exist_ok=True)

plt.savefig("../Charts/april_2026_sector_performance.png", dpi=300)

plt.show()