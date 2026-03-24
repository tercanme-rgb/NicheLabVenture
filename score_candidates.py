#!/usr/bin/env python3
import json, argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent
HIGH_VALUE_BUYERS = {
    "small SaaS teams", "indie SaaS teams", "startup CTOs", "finance managers",
    "Shopify brands", "agencies", "AI product teams", "clinic owners"
}

def score_candidate(c):
    title_words = len(c["title"].split())
    specificity = min(95, 40 + (10 if 4 <= title_words <= 11 else 0) + (15 if " for " in c["title"].lower() else 0) + 20)
    buyer_clarity = 90 if c["buyer"]["primary"] else 40
    monetization_clarity = 85 if c["business_model"] in {"subscription", "tiered_saas", "workflow_saas", "usage_based", "finance_workflow", "ops_tooling"} else 68
    founder_viability = 78 if c["business_model"] != "enterprise_only" else 45
    wedge_clarity = 80 if c["pain"] and c["workflow"] else 50
    signal_bonus = 6 if c["buyer"]["primary"] in HIGH_VALUE_BUYERS else 0
    overall = round((specificity + buyer_clarity + monetization_clarity + founder_viability + wedge_clarity) / 5 + signal_bonus, 1)
    c["scores"] = {
        "specificity": specificity,
        "buyer_clarity": buyer_clarity,
        "monetization_clarity": monetization_clarity,
        "founder_viability": founder_viability,
        "wedge_clarity": wedge_clarity,
        "overall": min(overall, 100)
    }
    c["report_candidate"] = overall >= 75
    return c

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="output/candidates.json")
    args = ap.parse_args()

    data = json.loads((BASE / args.input).read_text(encoding="utf-8"))
    scored = [score_candidate(c) for c in data]
    scored.sort(key=lambda x: x["scores"]["overall"], reverse=True)

    out_dir = BASE / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "scored-candidates.json"
    out_path.write_text(json.dumps(scored, indent=2), encoding="utf-8")
    print(f"Wrote scored candidates to {out_path}")
    print("Top 5:")
    for c in scored[:5]:
        print(f"- {c['title']} :: {c['scores']['overall']}")

if __name__ == "__main__":
    main()
