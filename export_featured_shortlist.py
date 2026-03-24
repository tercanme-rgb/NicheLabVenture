#!/usr/bin/env python3
import json, argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="output/scored-candidates.json")
    ap.add_argument("--count", type=int, default=3)
    args = ap.parse_args()

    data = json.loads((BASE / args.input).read_text(encoding="utf-8"))
    top = data[:args.count]
    featured = []
    for i, c in enumerate(top, start=1):
        featured.append({
            "rank": i,
            "title": c["title"],
            "category": c["visible_category"],
            "buyer": c["buyer"]["primary"],
            "workflow": c["workflow"],
            "thesis": c["thesis"],
            "overall_score": c["scores"]["overall"],
            "publishability": c["scores"]["publishability"]
        })

    out_dir = BASE / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "featured-shortlist.json"
    out_path.write_text(json.dumps(featured, indent=2), encoding="utf-8")
    print(f"Wrote featured shortlist to {out_path}")
    for item in featured:
        print(f"- #{item['rank']} {item['title']}")

if __name__ == "__main__":
    main()
