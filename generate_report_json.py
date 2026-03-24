#!/usr/bin/env python3
import json, argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent

def make_visual_series(base_score: int):
    start = max(12, base_score - 45)
    return [start, start + 6, start + 11, start + 17, start + 24, start + 31, start + 39, base_score]

def build_report(candidate):
    overall = int(candidate["scores"]["overall"])
    market = min(92, overall + 4)
    revenue = min(89, overall + 1)
    competition = max(28, 100 - overall + 36)
    difficulty = max(34, 92 - overall)

    title = candidate["title"]
    subtitle = candidate["subtitle"]
    buyer = candidate["buyer"]["primary"]
    workflow = candidate["workflow"]
    pain = candidate["pain"]
    trigger = candidate["trigger"]

    slug = title.lower().replace("&", "and").replace("/", "-").replace("  ", " ").replace(" ", "-")
    return {
        "report_id": candidate["candidate_id"].replace("cand_", "rep_"),
        "slug": slug,
        "status": "published",
        "tier_visibility": {
            "starter_available": True,
            "pro_available": True,
            "pdf_export_pro_only": True
        },
        "meta": {
            "title": title,
            "subtitle": subtitle,
            "category_primary": candidate["visible_category"],
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
            "scoring_notes": [
                f"Clear buyer: {buyer}",
                f"Sharp workflow: {workflow}",
                f"Commercial pain: {pain}"
            ]
        },
        "market_research": {
            "market_overview": {
                "summary": f"This opportunity sits inside {candidate['visible_category']} and targets {buyer} through a narrow {workflow} use case.",
                "market_definition": f"A workflow layer built to reduce {pain} for {buyer}.",
                "demand_drivers": [
                    f"Growing need for {workflow}",
                    f"Rising cost of {pain}",
                    f"More teams operating under {trigger}"
                ],
                "timing_catalysts": [
                    trigger.title(),
                    "Higher workflow complexity",
                    "Need for faster execution with lean teams"
                ]
            },
            "market_size": {
                "tam": {"value": market * 100000000, "display": f"${market/10:.1f}B", "method": "heuristic_estimate"},
                "sam": {"value": revenue * 10000000, "display": f"${revenue*10}M", "method": "segment_estimate"},
                "som": {"value": max(7, overall//6) * 1000000, "display": f"${max(7, overall//6)}M", "method": "obtainable_share_estimate"},
                "assumptions": ["Focused buyer segment", "Single workflow wedge", "SMB-friendly initial GTM"]
            },
            "buyer_urgency": {
                "level": "high" if overall >= 80 else "medium",
                "summary": f"{pain.capitalize()} creates tangible operational cost for {buyer}."
            }
        },
        "community_signals": {
            "summary": f"Community pain clusters around {pain} and the lack of streamlined {workflow}.",
            "signal_sources": ["Reddit", "Operator forums", "Review sites", "Product discussions"],
            "pain_points": [
                {"theme": pain.title(), "frequency": "high", "detail": f"Users repeatedly describe {pain} as a blocker."},
                {"theme": workflow.title(), "frequency": "medium", "detail": f"Teams want cleaner workflows around {workflow}."}
            ],
            "sentiment": {"positive": 22, "neutral": 31, "negative": 47}
        },
        "competitor_insights": {
            "summary": "The category is active, but positioning remains fragmented.",
            "competitor_table": [
                {"name": "Generic incumbent", "type": "incumbent", "positioning": "Broad platform", "pricing": "$99+/mo", "strength": "Breadth", "weakness": "Too broad", "gap_relevance": "Leaves focused wedge open"},
                {"name": "Internal workaround", "type": "substitute", "positioning": "DIY process", "pricing": "Hidden cost", "strength": "Flexible", "weakness": "Manual and brittle", "gap_relevance": "Signals product demand"}
            ],
            "positioning_gap": {
                "headline": f"Focused {workflow} for {buyer}",
                "summary": f"A focused product can win by directly reducing {pain} instead of trying to be a broad platform."
            },
            "pricing_landscape": {
                "low_end": "$0-$19/mo",
                "mid_market": "$29-$99/mo",
                "enterprise": "$299+/mo"
            }
        },
        "strategy_frameworks": {
            "entry_wedge": {
                "headline": workflow.title(),
                "summary": f"Lead with the highest-friction part of {workflow} for {buyer}."
            },
            "acquisition_path": {
                "primary_channels": ["Operator content", "Communities", "Search-driven content", "Direct outreach"],
                "motion": "Bottom-up workflow adoption"
            },
            "defensibility": {
                "level": "moderate",
                "summary": "Defensibility comes from workflow embedding, team usage, and retained operational history."
            },
            "expansion_map": ["Core workflow", "Alerts and approvals", "Reporting and retention", "Adjacent automation"]
        },
        "business_model": {
            "pricing_model": candidate["business_model"],
            "starter_price_hint": "$29/mo",
            "team_price_hint": "$79/mo",
            "enterprise_price_hint": "custom",
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
            "trend_chart": {
                "type": "line",
                "series": make_visual_series(overall),
                "x_labels": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"],
                "label": "Signal trajectory"
            },
            "score_bars": [
                {"label": "Market", "value": market},
                {"label": "Revenue", "value": revenue},
                {"label": "Competition", "value": competition},
                {"label": "Difficulty", "value": difficulty}
            ]
        },
        "starter_view": {
            "visible_sections": [
                "meta", "dashboard", "scoring", "market_research.market_overview",
                "community_signals.summary", "community_signals.pain_points",
                "competitor_insights.summary", "verdict"
            ],
            "locked_sections": [
                "market_research.market_size", "competitor_insights.competitor_table",
                "strategy_frameworks", "business_model", "case_examples",
                "roadmap_30d", "visuals.trend_chart"
            ],
            "pdf_export": False
        },
        "pro_view": {
            "visible_sections": [
                "meta","dashboard","scoring","market_research","community_signals",
                "competitor_insights","strategy_frameworks","business_model",
                "founder_fit","risk_matrix","case_examples","roadmap_30d","verdict","visuals"
            ],
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
