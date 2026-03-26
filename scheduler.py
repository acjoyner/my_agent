"""
Scheduler
=========
Runs automatic daily/weekly scans without you having to ask.

Usage:
  python scheduler.py            # Run once right now
  python scheduler.py --loop     # Keep running on a schedule (leave terminal open)

To run in the background on a schedule, add to cron (Mac/Linux):
  crontab -e
  0 8 * * * cd /path/to/my_agent && python scheduler.py >> output/scheduler.log 2>&1

Or on Windows Task Scheduler, run:
  python C:\path\to\my_agent\scheduler.py
"""

import sys
import time
import argparse
from datetime import datetime
from agent import run_agent
from memory.memory import Memory
from config.settings import (
    JOB_TITLE_INTERESTS,
    MIN_SALARY,
    PREFER_REMOTE,
    BUSINESS_INTEREST_AREAS,
    JOB_SCAN_INTERVAL_HOURS,
    TREND_SCAN_INTERVAL_HOURS,
)


def run_daily_job_scan(memory: Memory):
    """Automatically search for jobs matching your interests."""
    print(f"\n📋 [{datetime.now():%H:%M}] Running daily job scan...")
    for title in JOB_TITLE_INTERESTS[:2]:   # Limit to 2 titles per run to save API calls
        prompt = (
            f"Search for {title} jobs"
            + (" that are remote" if PREFER_REMOTE else "")
            + (f" with a salary of at least ${MIN_SALARY:,}" if MIN_SALARY else "")
            + ". Save the results to a file named 'daily_jobs'."
        )
        result = run_agent(prompt, memory)
        print(f"  ✅ {title}: Done")


def run_trend_scan(memory: Memory):
    """Automatically scan for trends in your interest areas."""
    print(f"\n📈 [{datetime.now():%H:%M}] Running trend scan...")
    for area in BUSINESS_INTEREST_AREAS[:2]:
        prompt = (
            f"Search for the latest trends and business opportunities in {area}. "
            "Summarize the top 3 signals and save them to a file named 'weekly_trends'."
        )
        result = run_agent(prompt, memory)
        print(f"  ✅ {area}: Done")


def run_once():
    """Run all scans once and exit."""
    memory = Memory()
    print("=" * 50)
    print("  Automated Agent Scan")
    print(f"  {datetime.now():%Y-%m-%d %H:%M}")
    print("=" * 50)
    run_daily_job_scan(memory)
    run_trend_scan(memory)
    print(f"\n✅ All scans complete. Results saved to output/")


def run_loop():
    """Keep running scans on an interval."""
    memory = Memory()
    job_interval    = JOB_SCAN_INTERVAL_HOURS * 3600
    trend_interval  = TREND_SCAN_INTERVAL_HOURS * 3600
    last_job_scan   = 0
    last_trend_scan = 0

    print("🔄 Scheduler running. Press Ctrl+C to stop.")
    while True:
        now = time.time()
        if now - last_job_scan >= job_interval:
            run_daily_job_scan(memory)
            last_job_scan = now
        if now - last_trend_scan >= trend_interval:
            run_trend_scan(memory)
            last_trend_scan = now
        time.sleep(60)   # Check every minute


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="Run continuously on a schedule")
    args = parser.parse_args()

    if args.loop:
        run_loop()
    else:
        run_once()
