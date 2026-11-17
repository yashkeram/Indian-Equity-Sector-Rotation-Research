import sys
import os
import subprocess
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

if (SCRIPT_DIR / "Python").exists():
    PROJECT_ROOT = SCRIPT_DIR
    PYTHON_DIR = SCRIPT_DIR / "Python"
else:
    PROJECT_ROOT = SCRIPT_DIR.parent
    PYTHON_DIR = SCRIPT_DIR

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

try:
    import config
    DEFAULT_MONTH = config.get_latest_completed_month().strftime("%B")
except Exception:
    DEFAULT_MONTH = "August"

if len(sys.argv) > 1:
    TARGET_MONTH = sys.argv[1].capitalize()
else:
    TARGET_MONTH = DEFAULT_MONTH

PIPELINE_STAGES = [
    ("01_data_collector.py", [], "Stage 01: Raw Index Data Scraping & Chaining"),
    ("02_sector_analysis.py", [], "Stage 02: Sector Return & Breadth Calculations"),
    ("03_chart_generator.py", [], "Stage 03: Monthly Sector & Benchmark Chart Generation"),
    ("04_stock_analysis.py", [TARGET_MONTH], f"Stage 04: Intra-Sector Stock Rankings ({TARGET_MONTH})"),
    ("05_stock_summary.py", [], "Stage 05: Top/Bottom Performer Summaries Aggregation"),
    ("06_monthly_report.py", [TARGET_MONTH], f"Stage 06: Structured Monthly JSON Report Compilation ({TARGET_MONTH})"),
    ("07_blog_generator.py", [TARGET_MONTH], f"Stage 07: Research Blog Markdown Publishing ({TARGET_MONTH})"),
]

def run_stage(script_name: str, args: list, description: str) -> bool:
    script_path = PYTHON_DIR / script_name
    if not script_path.exists():
        print(f"\n[ERROR] Script not found: {script_path}")
        return False

    cmd = [sys.executable, str(script_path)] + args

    print("\n" + "=" * 70)
    print(f"RUNNING: {description}")
    print(f"Command: python {script_path.name} {' '.join(args)}".strip())
    print("=" * 70 + "\n")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    start_time = time.time()
    process = subprocess.Popen(
        cmd,
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    for line in iter(process.stdout.readline, ""):
        print(line, end="")

    process.stdout.close()
    return_code = process.wait()
    duration = time.time() - start_time

    if return_code != 0:
        print(f"\n[FAILURE] {script_name} exited with error code {return_code} (took {duration:.1f}s)")
        return False

    print(f"\n[SUCCESS] {script_name} completed in {duration:.1f}s")
    return True

def main():
    print("#" * 70)
    print(" INDIAN EQUITY SECTOR ROTATION PIPELINE - MASTER RUNNER")
    print(f" Target Month: {TARGET_MONTH} | Python: {sys.executable}")
    print("#" * 70)

    total_start = time.time()

    for script, args, desc in PIPELINE_STAGES:
        success = run_stage(script, args, desc)
        if not success:
            print("\n" + "!" * 70)
            print(f"PIPELINE HALTED due to failure in: {script}")
            print("Fix the error above before continuing.")
            print("!" * 70 + "\n")
            sys.exit(1)

    total_elapsed = time.time() - total_start
    print("\n" + "#" * 70)
    print(" ALL PIPELINE STAGES COMPLETED SUCCESSFULLY!")
    print(f" Total Execution Time: {total_elapsed:.1f} seconds")
    print(f" Target Report: Data/Reports/{TARGET_MONTH}_2026.json")
    print(f" Target Blog  : Blogs/2026/{TARGET_MONTH}.md")
    print("#" * 70 + "\n")

if __name__ == "__main__":
    main()
