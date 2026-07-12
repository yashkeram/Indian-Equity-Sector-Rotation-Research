import os
import json

# =====================================
# PATHS
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REPORTS_FOLDER = os.path.join(BASE_DIR, "..", "Data", "Reports")
BLOGS_FOLDER = os.path.join(BASE_DIR, "..", "Blogs", "2026")

os.makedirs(BLOGS_FOLDER, exist_ok=True)

# =====================================
# SETTINGS
# =====================================

import sys

# =====================================
# MONTH INPUT
# =====================================

if len(sys.argv) != 2:
    print("Usage: python 07_blog_generator.py <Month>")
    print("Example: python 07_blog_generator.py June")
    exit()

MONTH_NAME = sys.argv[1]

REPORT_FILE = f"{MONTH_NAME}_2026.json"
BLOG_FILE = f"{MONTH_NAME}.md"

# =====================================
# LOAD REPORT
# =====================================

with open(os.path.join(REPORTS_FOLDER, REPORT_FILE), "r") as f:
    report = json.load(f)

# =====================================
# BUILD MARKDOWN
# =====================================

markdown = f"""# Indian Equity Sector Rotation Report

## {report["month"]}

---

## Market Overview

The NIFTY 50 returned **{report["nifty50_return"]:.2f}%** during {report["month"]}.

The **{report["best_sector"].title()}** sector was the best performer with a return of **{report["best_sector_return"]:.2f}%**.

The **{report["worst_sector"].title()}** sector was the weakest performer with a return of **{report["worst_sector_return"]:.2f}%**.

---

## Sector Performance

| Sector | Return |
|--------|--------|
"""

# Add sector table
for sector, value in report["sector_returns"].items():

    if sector == "nifty50":
        continue

    markdown += f"| {sector.title()} | {value:.2f}% |\n"

# Top Stocks

markdown += "\n---\n\n## Top Performing Stocks\n\n"

for sector, companies in report["top_stocks"].items():

    markdown += f"### {sector.title()}\n\n"

    for company in companies:
        markdown += f"- {company}\n"

    markdown += "\n"

# Closing section

markdown += """---

## Key Takeaways

- Review the month's sector rotation.
- Compare sector performance with NIFTY 50.
- Observe leadership changes among sectors.

---

*Generated automatically using the Indian Equity Sector Rotation Research Pipeline.*
"""

# =====================================
# SAVE BLOG
# =====================================

blog_path = os.path.join(BLOGS_FOLDER, BLOG_FILE)

with open(blog_path, "w", encoding="utf-8") as f:
    f.write(markdown)

print("Blog generated successfully!")
print(blog_path)