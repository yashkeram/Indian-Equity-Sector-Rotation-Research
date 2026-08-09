import os
import sys
import json


# ============================================================
# MODULE 07 - BLOG GENERATOR
# ============================================================


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.abspath(
    os.path.join(BASE_DIR, "..")
)

REPORTS_FOLDER = os.path.join(
    PROJECT_ROOT,
    "Data",
    "Reports"
)

BLOGS_FOLDER = os.path.join(
    PROJECT_ROOT,
    "Blogs",
    "2026"
)


# Create blog directory
os.makedirs(
    BLOGS_FOLDER,
    exist_ok=True
)


# ============================================================
# MONTH INPUT
# ============================================================

if len(sys.argv) != 2:

    print()
    print("Usage:")
    print("python Python\\07_blog_generator.py July")
    print()

    sys.exit(1)


MONTH_NAME = sys.argv[1].strip().capitalize()


MONTHS = [
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


if MONTH_NAME not in MONTHS:

    print(
        f"Invalid month: {MONTH_NAME}"
    )

    sys.exit(1)


# ============================================================
# FILE NAMES
# ============================================================

REPORT_FILE = f"{MONTH_NAME}_2026.json"

BLOG_FILE = f"{MONTH_NAME}.md"


REPORT_PATH = os.path.join(
    REPORTS_FOLDER,
    REPORT_FILE
)

BLOG_PATH = os.path.join(
    BLOGS_FOLDER,
    BLOG_FILE
)


# ============================================================
# DISPLAY
# ============================================================

print()
print("==========================================")
print("MODULE 07 - BLOG GENERATOR")
print("==========================================")
print()

print(
    f"Project Root : {PROJECT_ROOT}"
)

print(
    f"Report       : {REPORT_PATH}"
)

print(
    f"Blog Folder  : {BLOGS_FOLDER}"
)

print(
    f"Month        : {MONTH_NAME} 2026"
)

print()


# ============================================================
# VALIDATE REPORT
# ============================================================

if not os.path.exists(REPORT_PATH):

    raise FileNotFoundError(
        f"Report not found:\n{REPORT_PATH}\n\n"
        f"Run Module 06 first."
    )


# ============================================================
# LOAD REPORT
# ============================================================

print("Loading monthly report...")


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

bottom_stocks = report.get(
    "bottom_stocks",
    {}
)


# ============================================================
# BLOG HEADER
# ============================================================

markdown = f"""# Indian Equity Sector Rotation Report — {month}

## Market Overview

The Indian equity market delivered a mixed performance during **{month}**, with different sectors showing significant differences in momentum.

"""


# ============================================================
# NIFTY 50
# ============================================================

if nifty50_return is not None:

    markdown += f"""
### NIFTY 50 Performance

The **NIFTY 50** returned **{nifty50_return:.2f}%** during {month}.

This provides the benchmark against which sector performance can be evaluated.

"""


# ============================================================
# SECTOR LEADERSHIP
# ============================================================

markdown += f"""
## Sector Leadership

The strongest-performing sector during {month} was **{best_sector.title()}**, delivering a monthly return of **{best_sector_return:.2f}%**.

The weakest-performing sector was **{worst_sector.title()}**, which returned **{worst_sector_return:.2f}%**.

This dispersion between sector leaders and laggards is particularly important from a sector-rotation perspective because it highlights where market momentum was concentrated.

"""


# ============================================================
# SECTOR PERFORMANCE TABLE
# ============================================================

markdown += """## Sector Performance

| Sector | Monthly Return |
|---|---:|
"""


# Sort sectors by performance
sorted_sectors = sorted(
    sector_returns.items(),
    key=lambda x: x[1],
    reverse=True
)


for sector, value in sorted_sectors:

    if sector.lower() == "nifty50":
        continue

    markdown += (
        f"| {sector.title()} | "
        f"{float(value):.2f}% |\n"
    )


markdown += "\n"


# ============================================================
# SECTOR ROTATION ANALYSIS
# ============================================================

markdown += """## Sector Rotation Analysis

The monthly return distribution shows where market leadership was concentrated.

Strong-performing sectors can indicate areas receiving stronger investor interest, while weaker sectors may indicate relative underperformance or rotation away from previous leadership.

Rather than looking at individual stocks in isolation, sector rotation analysis helps identify broader market trends and changes in relative strength.

"""


# ============================================================
# TOP STOCKS
# ============================================================

markdown += """## Top-Performing Stocks by Sector

The following stocks were the top performers within each sector according to the project's monthly stock-ranking analysis.

"""


for sector in sorted(
    top_stocks.keys()
):

    companies = top_stocks[sector]

    markdown += (
        f"### {sector.title()}\n\n"
    )

    if companies:

        for rank, company in enumerate(
            companies,
            start=1
        ):

            markdown += (
                f"{rank}. {company}\n"
            )

    else:

        markdown += (
            "No stock-level data available.\n"
        )

    markdown += "\n"


# ============================================================
# BOTTOM STOCKS
# ============================================================

markdown += """## Weakest-Performing Stocks by Sector

The weakest stocks provide another perspective on the dispersion within each sector.

"""


for sector in sorted(
    bottom_stocks.keys()
):

    companies = bottom_stocks[sector]

    markdown += (
        f"### {sector.title()}\n\n"
    )

    if companies:

        for rank, company in enumerate(
            companies,
            start=1
        ):

            markdown += (
                f"{rank}. {company}\n"
            )

    else:

        markdown += (
            "No stock-level data available.\n"
        )

    markdown += "\n"


# ============================================================
# KEY TAKEAWAYS
# ============================================================

markdown += """## Key Takeaways

- Sector performance varied significantly during the month.
- The strongest sector represented the month's primary area of relative strength.
- The weakest sector represented the month's main area of relative weakness.
- Stock-level rankings help identify the companies driving sector performance.
- Comparing sector returns against the NIFTY 50 provides useful context for evaluating relative performance.
- Tracking these changes month after month can help identify longer-term sector-rotation regimes.

"""


# ============================================================
# METHODOLOGY
# ============================================================

markdown += """## Methodology

This report is generated automatically using the **Indian Equity Sector Rotation Research** pipeline.

The pipeline combines:

- Indian equity index data
- Monthly sector returns
- Stock-level monthly returns
- Sector-wise stock rankings
- Top and bottom stock summaries
- Automated monthly reporting

The analysis is intended for research and educational purposes and should not be interpreted as investment advice.

"""


# ============================================================
# FOOTER
# ============================================================

markdown += f"""---

*Generated automatically by the Indian Equity Sector Rotation Research Pipeline.*

**Report:** {month}

**Data period:** 2026

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
print("==========================================")
print("BLOG GENERATED SUCCESSFULLY")
print("==========================================")
print()

print(
    f"Blog saved to:"
)

print(
    BLOG_PATH
)

print()