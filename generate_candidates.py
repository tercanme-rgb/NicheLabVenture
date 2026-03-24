#!/usr/bin/env python3
import json, random, argparse, re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ARCH = json.loads((BASE / "category-architecture.json").read_text(encoding="utf-8"))

FORBIDDEN_TITLE_CHUNKS = {"tool", "platform", "solution", "software", "dashboard"}

def normalize_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title.strip())
    words = []
    for i, word in enumerate(title.split()):
        lw = word.lower()
        if i and lw in {"for", "and", "of", "with"}:
            words.append(lw)
        else:
            words.append(word.capitalize())
    out = " ".join(words)
    for src, dst in ARCH.get("publish_rules", {}).get("title_normalization", {}).items():
        out = out.replace(src, dst)
    return out

def workflow_focus_from(workflow: str, category: str) -> str:
    custom = {
        "support inbox triage": "Support Triage Workflow",
        "internal alert escalation": "Internal Alert Escalation Workflow",
        "invoice exception review": "Invoice Exception Review",
        "client onboarding QA": "Client Onboarding QA",
        "patient intake follow-up": "Patient Intake Follow-Up",
        "contract request triage": "Contract Request Triage",
        "AI output validation": "AI Output Validation",
        "human approval routing": "Human Approval Routing",
        "prompt review workflow": "Prompt Review Workflow",
        "approval routing": "Approval Routing Workflow",
        "handoff tracking": "Handoff Tracking Workflow",
        "exception handling": "Exception Handling Workflow",
        "review workflows": "Review Workflow",
        "appointment reminders": "Appointment Reminder System",
        "lead qualification": "Lead Qualification Workflow",
        "invoice review": "Invoice Review Workflow",
        "expense approvals": "Expense Approval Workflow",
        "reconciliation": "Reconciliation Workflow",
        "audit logging": "Audit Logging",
        "client onboarding": "Client Onboarding Workflow",
        "proposal-to-kickoff flow": "Proposal-to-Kickoff Workflow",
        "delivery reporting": "Delivery Reporting Workflow",
    }
    return custom.get(workflow, workflow.title())

def pain_focus_from(pain: str, workflow: str) -> str:
    mapping = {
        "manual coordination": workflow_focus_from(workflow, ""),
        "poor visibility": workflow_focus_from(workflow, ""),
        "slow handoffs": "Handoff Workflow",
        "spreadsheet dependency": workflow_focus_from(workflow, ""),
        "inconsistent outputs": "AI Output Review",
        "manual QA": "AI QA Workflow",
        "refund leakage": "Refund Exception Review",
        "admin overload": workflow_focus_from(workflow, ""),
        "messy onboarding": "Client Onboarding QA",
        "manual review": "Exception Review Workflow",
        "support overload": "Support Triage Workflow",
        "low visibility": workflow_focus_from(workflow, ""),
        "invoice errors": "Invoice Exception Review",
        "approval delays": "Approval Workflow",
        "missed follow-ups": "Follow-Up Workflow",
    }
    return mapping.get(pain, workflow_focus_from(workflow, ""))

def apply_editorial_rewrite(title: str, category: str) -> str:
    rules = ARCH.get("editorial_rules", {}).get(category, {})
    for src, dst in rules.get("preferred_rewrites", {}).items():
        title = title.replace(src, dst)

    cleanup_pairs = {
        " for B2B AI Product Teams Shipping AI Features": " for B2B AI Product Teams",
        " for B2B SaaS Teams Shipping AI Features": " for B2B AI Product Teams",
        " for Smb Admin Teams": " for SMB Admin Teams",
        "AI AI QA Workflow": "AI QA Workflow",
        "QA Workflow for B2B AI Product Teams": "AI QA Workflow for B2B AI Product Teams",
        "Expense Approval Controls Workflow": "Expense Approval Workflow",
        "Approval Controls Workflow": "Approval Workflow",
    }
    for src, dst in cleanup_pairs.items():
        title = title.replace(src, dst)

    title = re.sub(r"\bAI AI\b", "AI", title)
    title = re.sub(r"\bWorkflow Workflow\b", "Workflow", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title

def build_candidate(visible_category: str, theme_name: str, seed_i: int):
    theme = ARCH["engine_theme_dictionary"][theme_name]
    random.seed(f"{visible_category}:{theme_name}:{seed_i}")
    buyer = random.choice(theme["buyers"])
    workflow = random.choice(theme["workflows"])
    pain = random.choice(theme["pains"])
    trigger = random.choice(theme["triggers"])
    model = random.choice(theme["models"])

    title_options = [
        f"{workflow} for {buyer}",
        f"{workflow_focus_from(workflow, visible_category)} for {buyer}",
        f"{pain_focus_from(pain, workflow)} for {buyer}",
    ]
    title = normalize_title(random.choice(title_options))

    if any(chunk in title.lower() for chunk in FORBIDDEN_TITLE_CHUNKS):
        title = normalize_title(f"{workflow_focus_from(workflow, visible_category)} for {buyer}")

    title = apply_editorial_rewrite(title, visible_category)
    title = normalize_title(title)

    subtitle = f"A focused {workflow} wedge for {buyer} facing {pain}."
    thesis = f"A {model.replace('_', ' ')} product focused on {workflow} could win with {buyer} by reducing {pain} under conditions shaped by {trigger}."
    return {
        "candidate_id": f"cand_{visible_category.lower().replace(' ','_')}_{theme_name}_{seed_i}",
        "visible_category": visible_category,
        "engine_theme": theme_name,
        "title": title,
        "subtitle": subtitle,
        "buyer": {"primary": buyer, "secondary": []},
        "workflow": workflow,
        "pain": pain,
        "trigger": trigger,
        "business_model": model,
        "geo": "Global",
        "thesis": thesis
    }

def dedupe_key(c):
    return "|".join([c["visible_category"].lower(), c["title"].lower()])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", required=True, help="Visible category")
    ap.add_argument("--count", type=int, default=30)
    args = ap.parse_args()

    if args.category not in ARCH["categories"]:
        raise SystemExit(f"Unknown category: {args.category}")

    themes = ARCH["categories"][args.category]["engine_themes"]
    raw = [build_candidate(args.category, themes[i % len(themes)], i) for i in range(args.count)]

    deduped = []
    seen = set()
    for c in raw:
        k = dedupe_key(c)
        if k not in seen:
            seen.add(k)
            deduped.append(c)

    out_dir = BASE / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "candidates.json"
    out_path.write_text(json.dumps(deduped, indent=2), encoding="utf-8")
    print(f"Wrote {len(deduped)} candidates to {out_path}")

if __name__ == "__main__":
    main()
