import os
import sys
import json


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..")
)

REPORTS_FOLDER = os.path.join(
    PROJECT_DIR,
    "Data",
    "Reports"
)

BLOGS_FOLDER = os.path.join(
    PROJECT_DIR,
    "Blogs",
    "2026"
)


# ============================================================
# MONTHS
# ============================================================

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


# ============================================================
# MONTH INPUT
# ============================================================

if len(sys.argv) != 2:

    print()
    print("Usage:")
    print("python Python\\07_blog_generator.py <Month>")
    print()
    print("Example:")
    print("python Python\\07_blog_generator.py July")
    print()

    sys.exit(1)


MONTH_NAME = sys.argv[1].strip().capitalize()


if MONTH_NAME not in VALID_MONTHS:

    print()
    print(f"Invalid month: {MONTH_NAME}")
    print()
    print("Valid months:")
    print(", ".join(VALID_MONTHS))
    print()

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
print("==============================================")
print("INDIAN EQUITY SECTOR ROTATION - BLOG GENERATOR")
print("==============================================")
print()

print(
    "Report Source :",
    REPORT_PATH
)

print(
    "Blog Output   :",
    BLOG_PATH
)

print()


# ============================================================
# CHECK REPORT
# ============================================================

if not os.path.exists(REPORT_PATH):

    print(
        "Monthly report not found."
    )

    print(
        "Run Module 06 first:"
    )

    print(
        f"python Python\\06_monthly_report.py {MONTH_NAME}"
    )

    print()

    sys.exit(1)


# ============================================================
# LOAD JSON REPORT
# ============================================================

try:

    with open(
        REPORT_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        report = json.load(file)

except json.JSONDecodeError as error:

    raise ValueError(
        f"Invalid JSON report:\n{error}"
    )


# ============================================================
# REQUIRED DATA
# ============================================================

month = report.get(
    "month",
    f"{MONTH_NAME} 2026"
)

nifty50_return = report.get(
    "nifty50_return"
)

best_sector = report.get(
    "best_sector",
    "Unknown"
)

best_sector_return = report.get(
    "best_sector_return"
)

worst_sector = report.get(
    "worst_sector",
    "Unknown"
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
# FORMAT HELPERS
# ============================================================

def format_return(value):
    """
    Format a numerical return as a percentage.
    """

    if value is None:
        return "N/A"

    return f"{float(value):.2f}%"


def title_sector(sector):
    """
    Convert sector identifier into readable title.
    """

    return str(
        sector
    ).replace(
        "_",
        " "
    ).title()


# ============================================================
# BUILD BLOG
# ============================================================

markdown = f"""# Indian Equity Sector Rotation Report

## {month}

---

## Market Overview

The NIFTY 50 returned **{format_return(nifty50_return)}** during {month}.

The **{title_sector(best_sector)}** sector was the strongest-performing sector, returning **{format_return(best_sector_return)}**.

The **{title_sector(worst_sector)}** sector was the weakest-performing sector, returning **{format_return(worst_sector_return)}**.

---

## Sector Performance

| Sector | Monthly Return |
|--------|----------------|
"""


# ============================================================
# SECTOR TABLE
# ============================================================

for sector, value in sector_returns.items():

    # NIFTY 50 is the benchmark,
    # not a sector.

    if str(sector).lower() == "nifty50":
        continue

    markdown += (
        f"| {title_sector(sector)} "
        f"| {format_return(value)} |\n"
    )


# ============================================================
# TOP STOCKS
# ============================================================

markdown += """
---

## Top Performing Stocks

"""


if top_stocks:

    for sector, companies in top_stocks.items():

        markdown += (
            f"### {title_sector(sector)}\n\n"
        )

        if companies:

            for company in companies:

                markdown += (
                    f"- {company}\n"
                )

        else:

            markdown += (
                "- No top stocks available.\n"
            )

        markdown += "\n"

else:

    markdown += (
        "No monthly stock-ranking data "
        "was available for this report.\n\n"
    )


# ============================================================
# KEY TAKEAWAYS
# ============================================================

markdown += f"""---

## Key Takeaways

- The NIFTY 50 returned **{format_return(nifty50_return)}** during {month}.
- **{title_sector(best_sector)}** was the strongest-performing sector at **{format_return(best_sector_return)}**.
- **{title_sector(worst_sector)}** was the weakest-performing sector at **{format_return(worst_sector_return)}**.
- Sector performance showed differing levels of leadership and weakness across the market.

These observations are based on the monthly sector-return data generated by the research pipeline and do not represent a prediction of future market performance.

---

## Methodology

This report was generated using the **Indian Equity Sector Rotation Research Pipeline**.

The pipeline is designed to:

1. Collect market and sector data.
2. Calculate monthly sector returns.
3. Analyze and rank stocks within sector universes.
4. Generate structured monthly research reports.
5. Automatically convert the monthly report into a Markdown research article.

The analysis is based on the data available to the research pipeline for the selected month.

---

*Generated automatically using the Indian Equity Sector Rotation Research Pipeline.*
"""


# ============================================================
# CREATE BLOG DIRECTORY
# ============================================================

os.makedirs(
    BLOGS_FOLDER,
    exist_ok=True
)


# ============================================================
# SAVE BLOG
# ============================================================

with open(
    BLOG_PATH,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        markdown
    )


# ============================================================
# FINAL OUTPUT
# ============================================================

print("==============================================")
print("BLOG GENERATED SUCCESSFULLY")
print("==============================================")
print()

print("Source report:")
print(REPORT_PATH)

print()

print("Blog saved to:")
print(BLOG_PATH)

print()