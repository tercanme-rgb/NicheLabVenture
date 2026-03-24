#!/usr/bin/env python3
import json, argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent
ARCH = json.loads((BASE / "category-architecture.json").read_text(encoding="utf-8"))

GENERIC_PATTERNS = {
    "internal alerts", "visibility layer", "lightweight workflow tool",
    "review workflow", "tool for", "platform for", "dashboard for", "software for"
}

def title_penalty(title: str):
    t = title.lower()
    penalty = 0
    if any(g in t for g in GENERIC_PATTERNS):
        penalty += 16
    if len(t.split()) < 4:
        penalty += 10
    if "tool" in t and "for" not in t:
        penalty += 10
    return penalty

def editorial_bonus(c):
    rules = ARCH.get("editorial_rules", {}).get(c["visible_category"], {})
    bonus = 0
    if c["buyer"]["primary"] in rules.get("preferred_buyers", []):
        bonus += 10
    if c["workflow"] in rules.get("preferred_workflows", []):
        bonus += 10
    t = c["title"].lower()
    for frag in rules.get("avoid_title_fragments", []):
        if frag in t:
            bonus -= 8
    return bonus

def publishability_score(c):
    score = 58
    title = c["title"]
    if 4 <= len(title.split()) <= 10:
        score += 12
    if " for " in title.lower():
        score += 8
    if "workflow" in title.lower() or "review" in title.lower() or "logging" in title.lower() or "validation" in title.lower():
        score += 7
    score += editorial_bonus(c)
    return max(0, min(score, 98))

def score_candidate(c):
    title_words = len(c["title"].split())
    specificity = 60
    if 4 <= title_words <= 10:
        specificity += 14
    if " for " in c["title"].lower():
        specificity += 10
    if len(c["buyer"]["primary"].split()) >= 2:
        specificity += 7

    buyer_clarity = 75 + (8 if c["buyer"]["primary"] else 0) + editorial_bonus(c) // 2
    monetization_clarity = 86 if c["business_model"] in {
        "subscription", "tiered_saas", "workflow_saas", "usage_based",
        "finance_workflow", "ops_tooling", "local_business_saas",
        "seat_based", "practice_ops", "finance_ops_tool", "white_label_workflow"
    } else 72
    founder_viability = 82 if c["business_model"] != "enterprise_only" else 45
    wedge_clarity = 68 + editorial_bonus(c) // 2

    penalty = title_penalty(c["title"])
    publish = publishability_score(c)
    overall = round((specificity + buyer_clarity + monetization_clarity + founder_viability + wedge_clarity + publish) / 6 - penalty, 1)

    c["scores"] = {
        "specificity": max(0, specificity - penalty),
        "buyer_clarity": max(0, buyer_clarity),
        "monetization_clarity": monetization_clarity,
        "founder_viability": founder_viability,
        "wedge_clarity": max(0, wedge_clarity - penalty // 2),
        "publishability": publish,
        "editorial_bonus": editorial_bonus(c),
        "generic_penalty": penalty,
        "overall": max(0, min(overall, 100))
    }
    c["report_candidate"] = c["scores"]["overall"] >= 78 and penalty < 16
    return c

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="output/candidates.json")
    args = ap.parse_args()

    data = json.loads((BASE / args.input).read_text(encoding="utf-8"))
    scored = [score_candidate(c) for c in data]
    scored.sort(key=lambda x: (x["scores"]["overall"], x["scores"]["publishability"], x["scores"]["editorial_bonus"]), reverse=True)

    out_dir = BASE / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "scored-candidates.json"
    out_path.write_text(json.dumps(scored, indent=2), encoding="utf-8")
    print(f"Wrote scored candidates to {out_path}")
    print("Top 5:")
    for c in scored[:5]:
        print(f"- {c['title']} :: {c['scores']['overall']} (publish {c['scores']['publishability']}, editorial {c['scores']['editorial_bonus']}, penalty {c['scores']['generic_penalty']})")

if __name__ == "__main__":
    main()
