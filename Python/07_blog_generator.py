
from pathlib import Path
import sys
import json


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

REPORT_DIR = BASE_DIR / "Data" / "Reports"
RANKING_DIR = BASE_DIR / "Data" / "Processed"
BLOG_DIR = BASE_DIR / "Blogs" / "2026"
CHART_DIR = BASE_DIR / "Charts"

BLOG_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

YEAR = 2026

MONTHS = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

SECTOR_NAMES = {
    "nifty50": "NIFTY 50",
    "auto": "Auto",
    "bank": "Bank",
    "fmcg": "FMCG",
    "it": "IT",
    "metal": "Metal",
    "pharma": "Pharma",
    "realty": "Realty",
}


# ============================================================
# MONTH INPUT
# ============================================================

def get_month():

    if len(sys.argv) != 2:
        print(
            "\nUsage:\n"
            "python Python/07_blog_generator.py October"
        )
        raise SystemExit(1)

    month = sys.argv[1].strip().capitalize()

    if month not in MONTHS:
        raise ValueError(f"Invalid month: {month}")

    return month


# ============================================================
# LOAD REPORT
# ============================================================

def load_report(month):

    report_path = REPORT_DIR / f"{month}_{YEAR}.json"

    if not report_path.exists():
        raise FileNotFoundError(
            f"Monthly report not found: {report_path}\n"
            "Run Module 06 first."
        )

    with open(report_path, "r", encoding="utf-8") as file:
        report = json.load(file)

    required_fields = [
        "month",
        "nifty50_return",
        "sector_returns",
        "top_stocks",
        "bottom_stocks",
    ]

    missing = [
        field for field in required_fields
        if field not in report
    ]

    if missing:
        raise ValueError(
            f"Report is missing required fields: {missing}"
        )

    return report


# ============================================================
# FORMATTING HELPERS
# ============================================================

def display_sector(sector):

    key = str(sector).lower()

    return SECTOR_NAMES.get(
        key,
        str(sector).title()
    )


def format_return(value):

    if value is None:
        return "N/A"

    return f"{float(value):+.2f}%"


def add_stock_section(markdown, heading, stock_data):

    markdown += f"## {heading}\n\n"

    for sector in sorted(stock_data):

        companies = stock_data[sector]

        markdown += (
            f"### {display_sector(sector)}\n\n"
        )

        if not companies:
            markdown += "No valid stock data available.\n\n"
            continue

        for rank, company in enumerate(companies, start=1):
            markdown += f"{rank}. {company}\n"

        markdown += "\n"

    return markdown


# ============================================================
# CHART REFERENCES
# ============================================================

def add_charts(markdown, month):

    month_slug = month.lower()

    charts = [
        (
            f"{month_slug}_{YEAR}_sector_performance.png",
            "Monthly sector performance",
        ),
        (
            f"{month_slug}_{YEAR}_market_comparison.png",
            "NIFTY 50 and sector performance comparison",
        ),
    ]

    available = []

    for filename, description in charts:

        chart_path = CHART_DIR / filename

        if chart_path.exists():
            available.append((filename, description))

    if not available:
        return markdown

    markdown += "## Performance Charts\n\n"

    for filename, description in available:

        relative_path = f"../../Charts/{filename}"

        markdown += (
            f"![{description}]({relative_path})\n\n"
        )

    return markdown


# ============================================================
# BUILD BLOG
# ============================================================

def build_blog(report, month):

    report_month = report["month"]

    nifty_return = float(report["nifty50_return"])

    sector_returns = report["sector_returns"]

    top_stocks = report["top_stocks"]

    bottom_stocks = report["bottom_stocks"]

    # Remove NIFTY 50 from sector rankings.
    sector_only = {
        sector: float(value)
        for sector, value in sector_returns.items()
        if sector.lower() != "nifty50"
        and value is not None
    }

    if not sector_only:
        raise ValueError("No sector returns available.")

    sorted_sectors = sorted(
        sector_only.items(),
        key=lambda item: item[1],
        reverse=True
    )

    best_sector = report["best_sector"]
    worst_sector = report["worst_sector"]

    best_return = float(report["best_sector_return"])
    worst_return = float(report["worst_sector_return"])

    best_relative = best_return - nifty_return
    worst_relative = worst_return - nifty_return

    markdown = f"""# Indian Equity Sector Rotation Report — {report_month}

## Market Overview

The Indian equity market delivered a mixed performance during **{report_month}**, with substantial differences in performance across sectors.

The monthly analysis examines the NIFTY 50 benchmark, sector-level returns and stock-level performance to identify areas of relative market strength and weakness.

## NIFTY 50 Performance

The **NIFTY 50 returned {format_return(nifty_return)}** during {report_month}.

This benchmark provides a reference point for evaluating the relative performance of individual sectors.

## Sector Leadership

The strongest-performing sector was **{display_sector(best_sector)}**, returning **{format_return(best_return)}**.

It outperformed the NIFTY 50 by **{best_relative:+.2f} percentage points**.

The weakest-performing sector was **{display_sector(worst_sector)}**, returning **{format_return(worst_return)}**.

It underperformed the NIFTY 50 by **{abs(worst_relative):.2f} percentage points**.

## Sector Performance

| Sector | Monthly Return | Difference vs NIFTY 50 |
|---|---:|---:|
"""

    for sector, value in sorted_sectors:

        relative = value - nifty_return

        markdown += (
            f"| {display_sector(sector)} "
            f"| {format_return(value)} "
            f"| {relative:+.2f} pp |\n"
        )

    markdown += """

## Sector Rotation Analysis

The monthly return distribution highlights differences in sector leadership.

Sectors outperforming the NIFTY 50 demonstrated stronger relative performance during the month, while underperforming sectors lagged behind the benchmark.

These differences provide useful observations for tracking changes in market leadership over time.

However, a single month's return does not establish a persistent sector-rotation trend. Multiple months of observations are needed to assess whether relative strength is sustained.

"""

    markdown = add_charts(markdown, month)

    markdown = add_stock_section(
        markdown,
        "Top-Performing Stocks by Sector",
        top_stocks
    )

    markdown = add_stock_section(
        markdown,
        "Weakest-Performing Stocks by Sector",
        bottom_stocks
    )

    # --------------------------------------------------------
    # DATA QUALITY
    # --------------------------------------------------------

    quality = report.get("data_quality", {})

    warnings = quality.get("warnings", [])

    missing_summaries = quality.get(
        "missing_summaries",
        []
    )

    markdown += """## Data Quality and Coverage

Stock-level rankings are based on stocks with valid monthly return observations in the processed ranking files. Stocks without valid price data may be excluded from the rankings.

"""

    if quality:

        markdown += (
            f"- Report data-quality status: "
            f"**{quality.get('status', 'Not specified')}**\n"
        )

        markdown += (
            f"- Sector summaries loaded: "
            f"**{quality.get('loaded_summary_count', 'N/A')}/"
            f"{quality.get('expected_summary_count', 'N/A')}**\n"
        )

        if missing_summaries:
            markdown += (
                "- Missing summaries: "
                + ", ".join(missing_summaries)
                + "\n"
            )

        if warnings:

            markdown += "\n**Warnings:**\n\n"

            for warning in warnings:
                markdown += f"- {warning}\n"

    else:

        markdown += (
            "Detailed data-quality metadata was not available "
            "in the monthly JSON report.\n"
        )

    markdown += """

## Key Takeaways

"""

    markdown += (
        f"- NIFTY 50 gained {format_return(nifty_return)}.\n"
        f"- {display_sector(best_sector)} led sector performance "
        f"with {format_return(best_return)}.\n"
        f"- {display_sector(worst_sector)} was the weakest sector "
        f"with {format_return(worst_return)}.\n"
        "- Sector-level comparisons revealed differences in relative strength.\n"
        "- Stock rankings provided additional insight into performance within each sector.\n"
        "- Continued monthly tracking can help identify persistent changes in sector leadership.\n"
    )

    markdown += f"""

## Methodology

This report was generated using the **Indian Equity Sector Rotation Research** pipeline.

The research workflow combines:

- Indian equity index price data
- Monthly sector return calculations
- Individual stock return analysis
- Sector-wise stock rankings
- Top and bottom stock summaries
- Automated monthly JSON reporting
- Markdown report generation

Monthly returns are calculated using closing-price observations. Sector returns are evaluated against the NIFTY 50 benchmark.

The analysis is intended for research and educational purposes and should not be interpreted as investment advice.

---

*Generated automatically by the Indian Equity Sector Rotation Research Pipeline.*

**Report:** {report_month}

**Data period:** {YEAR}

"""


    return markdown


# ============================================================
# SAVE BLOG
# ============================================================

def save_blog(markdown, month):

    output_path = BLOG_DIR / f"{month}.md"

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(markdown)

    return output_path


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 50)
    print("INDIAN EQUITY SECTOR ROTATION RESEARCH")
    print("MODULE 07 - BLOG GENERATOR")
    print("=" * 50)

    month = get_month()

    print(f"\nTarget month: {month} {YEAR}")

    report = load_report(month)

    markdown = build_blog(
        report,
        month
    )

    output_path = save_blog(
        markdown,
        month
    )

    print("\n" + "=" * 50)
    print("BLOG GENERATED SUCCESSFULLY")
    print("=" * 50)

    print(f"\nBlog saved to:\n{output_path}")

    print("\nMODULE 07 COMPLETED")


if __name__ == "__main__":
    main()
