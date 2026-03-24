#!/usr/bin/env python3
import subprocess, sys, argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent

def run(cmd):
    print("> " + " ".join(cmd))
    subprocess.run(cmd, cwd=BASE, check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", default="Micro-SaaS")
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--candidate-index", type=int, default=0)
    args = ap.parse_args()

    py = sys.executable
    run([py, "generate_candidates.py", "--category", args.category, "--count", str(args.count)])
    run([py, "score_candidates.py"])
    run([py, "generate_report_json.py", "--index", str(args.candidate_index)])
    run([py, "render_report.py", "--plan", "starter"])
    run([py, "render_report.py", "--plan", "pro"])
    run([py, "export_featured_shortlist.py"])
    print("\nDone. Open:")
    print(" - output/report-starter.html")
    print(" - output/report-pro.html")
    print(" - output/report.json")
    print(" - output/featured-shortlist.json")

if __name__ == "__main__":
    main()
