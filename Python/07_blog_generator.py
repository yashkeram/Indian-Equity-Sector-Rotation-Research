import os
import sys
import json


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.getcwd()

REPORTS_FOLDER = os.path.join(
    BASE_DIR,
    "Outputs",
    "Reports"
)

BLOGS_FOLDER = os.path.join(
    BASE_DIR,
    "Outputs",
    "Blogs",
    "2026"
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    BLOGS_FOLDER,
    exist_ok=True
)


# ============================================================
# MONTH INPUT
# ============================================================

if len(sys.argv) != 2:

    print("Usage:")
    print("python Python\\07_blog_generator.py July")

    raise SystemExit


MONTH_NAME = sys.argv[1]


VALID_MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


if MONTH_NAME not in VALID_MONTHS:

    print(
        "Invalid month."
    )

    print(
        "Valid months:",
        ", ".join(VALID_MONTHS)
    )

    raise SystemExit


# ============================================================
# FILE NAMES
# ============================================================

REPORT_FILE = (
    f"{MONTH_NAME.lower()}_2026.json"
)

BLOG_FILE = (
    f"{MONTH_NAME.lower()}_2026.md"
)


REPORT_PATH = os.path.join(
    REPORTS_FOLDER,
    REPORT_FILE
)

BLOG_PATH = os.path.join(
    BLOGS_FOLDER,
    BLOG_FILE
)


# ============================================================
# VALIDATE REPORT
# ============================================================

if not os.path.exists(REPORT_PATH):

    raise FileNotFoundError(
        f"Monthly report not found:\n{REPORT_PATH}\n\n"
        f"Run Module 06 first."
    )


# ============================================================
# LOAD REPORT
# ============================================================

with open(
    REPORT_PATH,
    "r",
    encoding="utf-8"
) as file:

    report = json.load(file)


# ============================================================
# EXTRACT DATA
# ============================================================

month = report["month"]

nifty50_return = report.get(
    "nifty50_return"
)

best_sector = report.get(
    "best_sector",
    "N/A"
)

best_sector_return = report.get(
    "best_sector_return"
)

worst_sector = report.get(
    "worst_sector",
    "N/A"
)

worst_sector_return = report.get(
    "worst_sector_return"
)

sector_returns = report.get(
    "sector_returns",
    {}
)

top_stocks = report.get(
    "top_stocks",
    {}
)


# ============================================================
# BUILD SECTOR TABLE
# ============================================================

sector_table = ""

for sector, value in sector_returns.items():

    if sector.lower() == "nifty50":
        continue

    sector_table += (
        f"| {sector.title()} | "
        f"{float(value):.2f}% |\n"
    )


# ============================================================
# BUILD TOP STOCKS SECTION
# ============================================================

stock_sections = ""

for sector, companies in top_stocks.items():

    stock_sections += (
        f"### {sector.title()}\n\n"
    )

    if not companies:

        stock_sections += (
            "No ranked stock data available.\n\n"
        )

        continue

    for company in companies:

        stock_sections += (
            f"- {company}\n"
        )

    stock_sections += "\n"


# ============================================================
# DETERMINE MARKET LEADERSHIP
# ============================================================

sorted_sectors = sorted(
    [
        (sector, float(value))
        for sector, value in sector_returns.items()
        if sector.lower() != "nifty50"
    ],
    key=lambda x: x[1],
    reverse=True
)


leadership_section = ""

if sorted_sectors:

    leadership_section += (
        "The strongest sector leadership during "
        f"{month} was concentrated in "
        f"**{sorted_sectors[0][0].title()}**, "
        f"which returned "
        f"**{sorted_sectors[0][1]:.2f}%**."
    )

    if len(sorted_sectors) >= 2:

        leadership_section += (
            f" **{sorted_sectors[1][0].title()}** "
            f"was the second-strongest sector with "
            f"a return of "
            f"**{sorted_sectors[1][1]:.2f}%**."
        )

else:

    leadership_section = (
        "Sector leadership data was not available."
    )


# ============================================================
# BUILD BLOG
# ============================================================

markdown = f"""# Indian Equity Sector Rotation Research

## {month}

> A systematic review of Indian equity sector performance, leadership, and relative strength.

---

## Market Overview

The **NIFTY 50** returned **{nifty50_return:.2f}%** during {month}.

The strongest sector was **{best_sector.title()}**, which gained **{best_sector_return:.2f}%**.

The weakest sector was **{worst_sector.title()}**, which returned **{worst_sector_return:.2f}%**.

---

## Sector Performance

| Sector | Monthly Return |
|--------|----------------|
{sector_table}

---

## Sector Leadership

{leadership_section}

The dispersion between the strongest and weakest sectors provides an important indication of the degree of sector rotation during the month.

The system tracks these relative performance differences to identify where market leadership is strengthening and where momentum is weakening.

---

## Top Stocks by Sector

{stock_sections}

---

## What Stood Out This Month

### 1. Technology Leadership

The **{best_sector.title()}** sector was the strongest-performing sector during {month}, significantly outperforming the broader NIFTY 50.

This suggests that technology stocks were an important source of market strength during the month.

### 2. Sector Dispersion

The difference between the strongest and weakest sectors highlights meaningful dispersion across the Indian equity market.

Rather than treating the market as a single asset class, sector rotation analysis allows investors and researchers to examine where returns are actually being generated.

### 3. Relative Performance Matters

A sector can generate a positive return while still underperforming the broader market.

For this reason, the research framework evaluates sector performance relative to the NIFTY 50 rather than looking only at absolute returns.

---

## Key Takeaways

- **NIFTY 50:** {nifty50_return:.2f}%
- **Best sector:** {best_sector.title()} ({best_sector_return:.2f}%)
- **Weakest sector:** {worst_sector.title()} ({worst_sector_return:.2f}%)
- Sector performance showed meaningful differences across industries.
- Technology was the dominant sector during the month.
- Sector rotation remains an important framework for monitoring changing market leadership.

---

## Methodology

This article was generated from the **Indian Equity Sector Rotation Research** pipeline.

The research workflow consists of:

1. Market data collection
2. Sector return calculation
3. Sector ranking
4. Stock-level analysis
5. Monthly performance analysis
6. Automated report generation
7. Automated research article generation

The objective is to create a reproducible framework for studying changing sector leadership in the Indian equity market.

---

## Disclaimer

This research is for **educational and informational purposes only**.

It does not constitute investment advice, a recommendation to buy or sell securities, or a guarantee of future performance.

Historical returns and rankings do not guarantee future results.

---

*Generated automatically by the Indian Equity Sector Rotation Research System.*
"""


# ============================================================
# SAVE BLOG
# ============================================================

with open(
    BLOG_PATH,
    "w",
    encoding="utf-8"
) as file:

    file.write(markdown)


# ============================================================
# COMPLETE
# ============================================================

print()
print("===================================")
print("BLOG GENERATED SUCCESSFULLY")
print("===================================")

print()
print(f"Month: {month}")

print()
print("Blog saved to:")

print(BLOG_PATH)

print()
print("You can now open the Markdown file and")
print("manually edit it before publishing to Medium.")