#!/usr/bin/env python3
import json, argparse
from pathlib import Path
from importlib.machinery import SourceFileLoader

BASE = Path(__file__).resolve().parent

# reuse v6 logic by loading previous script dynamically is overkill; copy the generated structure from v6 file if needed
# here we build on top of v6-style logic but with editorial subtitle refinement
import random

ARCH = json.loads((BASE / "category-architecture.json").read_text(encoding="utf-8"))

CATEGORY_TONE = {
    "AI Automation": {
        "market": "This market is being shaped less by generic AI enthusiasm and more by the operational burden of shipping AI features reliably. Teams are moving beyond experimentation and into repeatable delivery, which means internal review, validation, and audit workflows are becoming real product categories rather than temporary patches.",
        "community": "Operator conversations in this category usually sound practical rather than visionary. Teams talk about failed edge cases, unclear ownership, weak review discipline, and the difficulty of trusting outputs in live workflows.",
        "positioning": "The strongest positioning is rarely 'AI platform.' It is usually a narrower promise around control, validation, or reliability.",
        "wedge": "The right wedge is the point where AI workflow risk becomes visible to an operator.",
        "business": "Pricing works best when the product is easy to trial but clearly tied to a repeated operational action.",
        "verdict": "This is strongest when framed as workflow infrastructure for trust, validation, and operator control."
    },
    "Finance & Admin": {
        "market": "Finance and admin categories are often stronger than they look because the pain is recurring, unglamorous, and expensive in aggregate. Products that reduce review time, exception handling, or administrative drift can create clear ROI even without dramatic top-line storytelling.",
        "community": "The most useful signals are usually complaints about manual review, approval lag, reconciliation friction, and spreadsheet dependency.",
        "positioning": "The strongest positioning is around operational clarity and reduced error, not flashy transformation language.",
        "wedge": "The entry wedge should start at the exception path, where manual work is slowest and most expensive.",
        "business": "Recurring pricing is credible when the product clearly reduces finance-team drag or removes repetitive review burden.",
        "verdict": "This is strongest when framed as error reduction and workflow discipline."
    },
    "Local Business": {
        "market": "Local business software works when it reduces real administrative drag for operators who are already overloaded. Buying decisions are often driven by time pressure, staff constraints, and the need to make front-desk or service workflows less fragile.",
        "community": "Signals here tend to appear through complaints about missed follow-up, no-shows, inconsistent intake, slow admin work, or poor visibility across repeated workflows.",
        "positioning": "The best positioning is concrete and operational.",
        "wedge": "The best wedge is usually the first workflow that staff repeatedly fail to execute cleanly under time pressure.",
        "business": "Pricing needs to feel easy to justify against wasted admin time, missed revenue, or poor customer follow-through.",
        "verdict": "This is strongest when packaged as a practical workflow improvement rather than a software overhaul."
    }
}
BASELINE_TONE = {
    "market": "This opportunity becomes more interesting when the workflow is narrow, repeated, and tied to a buyer who already feels the cost of solving it badly.",
    "community": "Community evidence in categories like this tends to show up through repeated complaints, workaround behavior, and operator frustration rather than direct feature requests.",
    "positioning": "The best positioning is about solving one repeated workflow with more clarity and less friction than existing tools or manual workarounds.",
    "wedge": "A strong wedge begins where workflow pain is already visible and where the buyer can quickly see what gets easier after adoption.",
    "business": "Recurring pricing is most credible when the workflow is repeated often enough and the value can be understood in saved time, reduced error, or improved consistency.",
    "verdict": "This is strongest when kept narrow, measurable, and operationally useful."
}

def tone_for(category):
    return CATEGORY_TONE.get(category, BASELINE_TONE)

def make_visual_series(base_score: int):
    start = max(12, base_score - 45)
    return [start, start + 6, start + 11, start + 17, start + 24, start + 31, start + 39, base_score]

def section_block(title, paragraphs, bullets):
    return {"title": title, "paragraphs": paragraphs, "bullets": bullets}

def estimate_prices(category, business_model):
    if category == "AI Automation":
        return "$49/mo", "$149/mo", "Custom"
    if category == "Finance & Admin":
        return "$39/mo", "$99/mo", "Custom"
    if category == "Local Business":
        return "$29/mo", "$79/mo", "Custom"
    if category == "B2B Services":
        return "$39/mo", "$119/mo", "Custom"
    if category == "E-Commerce":
        return "$39/mo", "$99/mo", "Custom"
    return "$29/mo", "$79/mo", "Custom"

def estimate_market(category, overall):
    if category == "AI Automation":
        return (f"${max(4.8, round((overall+10)/12,1))}B", f"${max(180, (overall+15)*3)}M", f"${max(12, overall//5)}M")
    if category == "Finance & Admin":
        return (f"${max(3.6, round((overall+6)/14,1))}B", f"${max(140, (overall+8)*2)}M", f"${max(10, overall//6)}M")
    if category == "Local Business":
        return (f"${max(2.8, round((overall+4)/15,1))}B", f"${max(120, (overall+5)*2)}M", f"${max(8, overall//7)}M")
    return (f"${max(3.2, round((overall+5)/14,1))}B", f"${max(130, (overall+5)*2)}M", f"${max(9, overall//6)}M")

def subtitle_for(category, workflow, buyer, pain):
    if category == "AI Automation":
        return f"A focused control layer for {buyer} that reduces the operational risk of {workflow.lower()}."
    if category == "Finance & Admin":
        return f"A workflow product for {buyer} built to reduce {pain} and improve review discipline."
    if category == "Local Business":
        return f"A practical operations layer for {buyer} built to reduce admin drag around {workflow.lower()}."
    return f"A focused workflow product for {buyer} built to reduce {pain}."

def build_report(candidate):
    overall = int(candidate["scores"]["overall"])
    market = min(92, overall + 4)
    revenue = min(89, overall + 1)
    competition = max(28, 100 - overall + 36)
    difficulty = max(34, 92 - overall)

    title = candidate["title"]
    buyer = candidate["buyer"]["primary"]
    workflow = candidate["workflow"]
    pain = candidate["pain"]
    trigger = candidate["trigger"]
    category = candidate["visible_category"]
    tone = tone_for(category)
    subtitle = subtitle_for(category, workflow, buyer, pain)

    random.seed(candidate["candidate_id"])
    competitors = ARCH.get("category_competitors", {}).get(category, [])[:4]
    starter_price, team_price, ent_price = estimate_prices(category, candidate["business_model"])
    tam, sam, som = estimate_market(category, overall)
    slug = title.lower().replace("&", "and").replace("/", "-").replace("  ", " ").replace(" ", "-")

    expanded_sections = {
        "market_overview_section": section_block(
            "Market overview",
            [
                f"This opportunity sits inside {category} and targets {buyer} through a narrow {workflow} use case. {tone['market']}",
                f"For this specific angle, the commercial logic comes from reducing {pain} without forcing the buyer to adopt a broad new system. Smaller teams usually prefer products that fit into existing workflows and remove one sharp point of friction quickly."
            ],
            [f"Target buyer is explicit: {buyer}", f"Core workflow is focused: {workflow}", f"Commercial pain is tangible: {pain}"]
        ),
        "community_signals_section": section_block(
            "Community signals",
            [
                f"Community discussion around this type of workflow usually clusters around {pain} and the lack of a cleaner process around {workflow}. {tone['community']}",
                f"When operators repeatedly describe a problem in terms of hidden cost, inconsistency, or repeated manual effort, that is usually more actionable than surface-level trend interest."
            ],
            ["Recurring complaints usually indicate stable underlying demand", "Manual workarounds are often a sign of product whitespace", "Operator language is more valuable than generic trend language"]
        ),
        "positioning_gap_section": section_block(
            "Positioning gap",
            [
                f"The strongest opportunity is not to become a broad platform but to solve {workflow} more cleanly for {buyer}. {tone['positioning']}",
                f"The positioning gap usually appears when existing options are either too generic, too enterprise-shaped, or still dependent on manual work."
            ],
            ["Whitespace often sits between broad platforms and internal workarounds", "Clear positioning makes distribution easier", "A narrow claim is usually stronger than a vague category story"]
        ),
        "entry_wedge_section": section_block(
            "Entry wedge",
            [
                f"The best entry wedge is the highest-friction slice of {workflow} for {buyer}. {tone['wedge']}",
                f"The first version of the product should create an obvious before-and-after improvement in one repeated use case."
            ],
            [f"Start where {pain} is most expensive", "Keep the first version narrow and legible", "Expand only after one repeated workflow clearly works"]
        ),
        "business_model_section": section_block(
            "Business model",
            [
                f"A {candidate['business_model'].replace('_', ' ')} model is plausible because the buyer and workflow are both well-defined. {tone['business']}",
                f"The strongest pricing path is usually a low-friction entry point with expansion into team use, retained workflow history, reporting, or higher-frequency usage."
            ],
            ["Recurring workflow pain supports recurring revenue", "Entry pricing should feel easy to justify against wasted time or errors", "Expansion should come from deeper workflow embedding, not feature sprawl"]
        ),
        "verdict_section": section_block(
            "Verdict",
            [
                f"A credible wedge exists if the product remains tightly focused on {workflow} for {buyer}. {tone['verdict']}",
                f"The next step is validation, not platform building. The key question is whether buyers feel {pain} strongly enough to change behavior and pay for a cleaner process."
            ],
            ["This opportunity improves when scope gets narrower, not broader", "Validation should focus on urgency and current workaround behavior", "The product wins through clarity, repetition, and operational usefulness"]
        )
    }

    comp_table = []
    for c in competitors:
        comp_table.append({
            "name": c["name"],
            "type": "incumbent" if "internal" not in c["name"].lower() and "spreadsheet" not in c["name"].lower() else "substitute",
            "positioning": c["positioning"],
            "pricing": c["pricing"],
            "strength": c["strength"],
            "weakness": c["weakness"],
            "gap_relevance": f"Leaves room for a narrower {workflow.lower()} wedge for {buyer}."
        })

    return {
        "report_id": candidate["candidate_id"].replace("cand_", "rep_"),
        "slug": slug,
        "status": "published",
        "tier_visibility": {"starter_available": True, "pro_available": True, "pdf_export_pro_only": True},
        "meta": {
            "title": title,
            "subtitle": subtitle,
            "category_primary": category,
            "category_secondary": [candidate["engine_theme"]],
            "geo": [candidate["geo"]],
            "language": "en",
            "published_at": "2026-03-24",
            "updated_at": "2026-03-24",
            "report_number": 184,
            "author_mode": "system-generated",
            "version": "1.0"
        },
        "dashboard": {
            "hero_label": "Featured report",
            "hero_summary": candidate["thesis"],
            "thumbnail_theme": "dark-premium",
            "badges": ["High signal", "Focused wedge", "Actionable"]
        },
        "scoring": {
            "overall_confidence": overall,
            "recommendation": "build" if overall >= 80 else "validate_first",
            "market_score": market,
            "revenue_score": revenue,
            "competition_score": competition,
            "difficulty_score": difficulty,
            "speed_to_mvp_score": max(55, 100 - difficulty),
            "founder_fit_score": min(88, overall + 3),
            "signal_strength_score": min(90, overall + 5),
            "scoring_notes": [f"Clear buyer: {buyer}", f"Sharp workflow: {workflow}", f"Commercial pain: {pain}"]
        },
        "market_research": {
            "market_overview": {
                "summary": f"This opportunity sits inside {category} and targets {buyer} through a narrow {workflow} use case.",
                "market_definition": f"A workflow layer built to reduce {pain} for {buyer}.",
                "demand_drivers": [f"Growing need for {workflow}", f"Rising cost of {pain}", f"More teams operating under {trigger}"],
                "timing_catalysts": [trigger.title(), "Higher workflow complexity", "Need for faster execution with lean teams"]
            },
            "market_size": {
                "tam": {"value": 0, "display": tam, "method": "category-adjusted heuristic estimate"},
                "sam": {"value": 0, "display": sam, "method": "segment estimate"},
                "som": {"value": 0, "display": som, "method": "obtainable share estimate"},
                "assumptions": ["Focused buyer segment", "Single workflow wedge", "SMB-friendly initial GTM"]
            },
            "buyer_urgency": {
                "level": "high" if overall >= 80 else "medium",
                "summary": f"{pain.capitalize()} creates tangible operational cost for {buyer}."
            }
        },
        "community_signals": {
            "summary": f"Community pain clusters around {pain} and the lack of streamlined {workflow}.",
            "signal_sources": ["Operator communities", "Review sites", "Product discussions", "Workflow complaints"],
            "pain_points": [
                {"theme": pain.title(), "frequency": "high", "detail": f"Users repeatedly describe {pain} as a blocker."},
                {"theme": workflow.title(), "frequency": "medium", "detail": f"Teams want cleaner workflows around {workflow}."}
            ],
            "sentiment": {"positive": 22, "neutral": 31, "negative": 47}
        },
        "competitor_insights": {
            "summary": "The category is validated, but the strongest gap is usually in packaging, workflow focus, and pricing clarity for a narrower buyer.",
            "competitor_table": comp_table,
            "positioning_gap": {
                "headline": f"Focused {workflow} for {buyer}",
                "summary": f"A focused product can win by directly reducing {pain} instead of trying to be a broad platform."
            },
            "pricing_landscape": {"low_end": starter_price, "mid_market": team_price, "enterprise": ent_price}
        },
        "strategy_frameworks": {
            "entry_wedge": {"headline": workflow.title(), "summary": f"Lead with the highest-friction part of {workflow} for {buyer}."},
            "acquisition_path": {"primary_channels": ["Operator content", "Communities", "Search-driven content", "Direct outreach"], "motion": "Bottom-up workflow adoption"},
            "defensibility": {"level": "moderate", "summary": "Defensibility comes from workflow embedding, team usage, and retained operational history."},
            "expansion_map": ["Core workflow", "Alerts and approvals", "Reporting and retention", "Adjacent automation"]
        },
        "business_model": {
            "pricing_model": candidate["business_model"],
            "starter_price_hint": starter_price,
            "team_price_hint": team_price,
            "enterprise_price_hint": ent_price,
            "upsells": ["Team seats", "Retention", "Reporting", "Integrations"],
            "monetization_summary": f"A {candidate['business_model'].replace('_',' ')} model is plausible because the buyer and workflow are both well-defined."
        },
        "founder_fit": {
            "best_for": ["Technical founders", "Workflow-focused builders", "Operators who know the pain firsthand"],
            "less_ideal_for": ["Broad consumer app builders", "Founders without access to buyer conversations"],
            "sales_complexity": "medium",
            "technical_load": "medium",
            "support_burden": "medium"
        },
        "risk_matrix": {
            "overall_risk": "moderate",
            "risks": [
                {"type": "commoditization", "severity": "medium", "summary": "The wedge can be copied if positioning is weak."},
                {"type": "overbreadth", "severity": "high", "summary": "Trying to solve adjacent workflows too early reduces clarity."}
            ]
        },
        "case_examples": {
            "success_patterns": [{"title": "Focused workflow success", "summary": "Narrow workflow products often win by solving one operational pain deeply before expanding."}],
            "failure_patterns": [{"title": "Too broad too early", "summary": "Products that expand before owning one painful workflow often lose positioning."}],
            "strategic_lessons": ["Own one workflow first", "Turn operational pain into measurable ROI"]
        },
        "roadmap_30d": {
            "week_1": [f"Interview 10-15 {buyer}", f"Validate {pain} urgency"],
            "week_2": [f"Draft landing page for {workflow}", "Test positioning and willingness to pay"],
            "week_3": ["Run outreach in niche communities", "Collect objections and workflow details"],
            "week_4": ["Ship narrow MVP", "Test paid conversion"]
        },
        "verdict": {
            "final_call": "build" if overall >= 80 else "validate_first",
            "summary": f"A credible wedge exists if the product remains focused on {workflow} for {buyer}.",
            "next_best_action": f"Validate how urgently {buyer} want help with {pain} before expanding scope."
        },
        "visuals": {
            "trend_chart": {"type": "line", "series": make_visual_series(overall), "x_labels": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"], "label": "Signal trajectory"},
            "score_bars": [{"label": "Market", "value": market}, {"label": "Revenue", "value": revenue}, {"label": "Competition", "value": competition}, {"label": "Difficulty", "value": difficulty}]
        },
        "expanded_sections": expanded_sections,
        "starter_view": {
            "visible_sections": ["meta", "dashboard", "scoring", "market_research.market_overview", "community_signals.summary", "community_signals.pain_points", "competitor_insights.summary", "verdict", "expanded_sections"],
            "locked_sections": ["market_research.market_size", "competitor_insights.competitor_table", "strategy_frameworks", "business_model", "case_examples", "roadmap_30d", "visuals.trend_chart"],
            "pdf_export": False
        },
        "pro_view": {
            "visible_sections": ["meta","dashboard","scoring","market_research","community_signals","competitor_insights","strategy_frameworks","business_model","founder_fit","risk_matrix","case_examples","roadmap_30d","verdict","visuals","expanded_sections"],
            "pdf_export": True
        },
        "rendering": {
            "theme": "dark-premium",
            "layout_variant": "institutional-terminal",
            "pdf_template": "report_v2",
            "starter_template": "report_starter_v1",
            "pro_template": "report_pro_v1"
        }
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="output/scored-candidates.json")
    ap.add_argument("--index", type=int, default=0)
    args = ap.parse_args()
    data = json.loads((BASE / args.input).read_text(encoding="utf-8"))
    report = build_report(data[args.index])
    out_dir = BASE / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote report JSON to {out_path}")
    print(f"Selected candidate: {data[args.index]['title']}")

if __name__ == "__main__":
    main()
