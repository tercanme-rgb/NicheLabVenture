#!/usr/bin/env python3
import json, argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#07080C;--s1:#0B0D15;--s2:#10131E;--s3:#151A27;
  --b1:#1D2136;--b2:#252B44;--b3:#31395A;
  --t1:#ECF0F8;--t2:#8892B0;--t3:#505878;
  --gold:#C8861A;--gold-l:#E8A832;--gold-bg:rgba(200,134,26,.07);--gold-br:rgba(200,134,26,.22);
  --green:#22C55E;--green-bg:rgba(34,197,94,.07);--green-br:rgba(34,197,94,.20);
  --amber:#F59E0B;--amber-bg:rgba(245,158,11,.07);--amber-br:rgba(245,158,11,.20);
  --cyan:#0BB8D4;--cyan-bg:rgba(11,184,212,.07);--cyan-br:rgba(11,184,212,.20);
  --red:#EF4444;--red-bg:rgba(239,68,68,.07);--red-br:rgba(239,68,68,.20);
  --display:Georgia,serif;--body:Arial,sans-serif;--mono:monospace;
}
body{font-family:var(--body);background:var(--bg);color:var(--t1);line-height:1.65;font-size:15px}
.wrap{max-width:1180px;margin:0 auto;padding:32px 24px 60px}
.hero{background:linear-gradient(160deg,#120F05,var(--s1));border:1px solid var(--gold-br);border-radius:20px;padding:28px;margin-bottom:18px;position:relative;overflow:hidden}
.hero:before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--gold),var(--cyan))}
.kicker{font-family:var(--mono);font-size:10px;color:var(--t3);letter-spacing:1px;text-transform:uppercase;margin-bottom:10px}
.hero h1{font-family:var(--display);font-size:46px;line-height:1.02;margin-bottom:14px}
.hero p,.note{color:var(--t2)}
.score-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.score{font-family:var(--mono);font-size:12px;padding:6px 9px;border-radius:8px;border:1px solid var(--b2)}
.score.good{color:var(--green);background:var(--green-bg);border-color:var(--green-br)}
.score.mid{color:var(--amber);background:var(--amber-bg);border-color:var(--amber-br)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.card{background:var(--s1);border:1px solid var(--b1);border-radius:16px;padding:22px}
.section-title{font-size:16px;margin-bottom:12px}
.tam-grid,.signal-grid,.callout-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:14px;position:relative}
.tam-value,.signal-value{font-family:var(--mono);font-size:26px;color:var(--gold-l);margin-bottom:6px}
.signal-value{color:var(--cyan)}
.table{width:100%;border-collapse:collapse}
.table-wrap{background:var(--s1);border:1px solid var(--b1);border-radius:16px;overflow:hidden;margin:14px 0;position:relative}
.table th,.table td{padding:12px 14px;border-bottom:1px solid var(--b1);text-align:left;vertical-align:top}
.table th{font-family:var(--mono);font-size:11px;color:var(--t3);text-transform:uppercase}
.table tr:last-child td{border-bottom:none}
.locked{position:relative;overflow:hidden;min-height:220px}
.locked::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(7,8,12,.10),rgba(7,8,12,.78));pointer-events:none}
.lock-overlay{position:absolute;left:16px;right:16px;bottom:16px;z-index:2;background:rgba(11,13,21,.96);border:1px solid var(--gold-br);border-radius:14px;padding:14px}
.btn{display:inline-flex;padding:10px 14px;border-radius:10px;border:1px solid var(--b2);text-decoration:none;color:var(--t1)}
.btn-gold{background:linear-gradient(180deg,var(--gold-l),var(--gold));color:#fff;border:none}
svg{width:100%;height:auto;margin-top:10px}
.card p{margin-bottom:12px}
.takeaways{margin-top:10px;padding-left:18px}
.takeaways li{color:var(--t2);margin-bottom:8px}
.mini-badges{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 4px}
.mini-badge{font-family:var(--mono);font-size:10px;padding:5px 8px;border-radius:999px;border:1px solid var(--b2);background:var(--s2);color:var(--t2)}
.mini-badge.good{color:var(--green);background:var(--green-bg);border-color:var(--green-br)}
.mini-badge.amber{color:var(--amber);background:var(--amber-bg);border-color:var(--amber-br)}
.mini-badge.cyan{color:var(--cyan);background:var(--cyan-bg);border-color:var(--cyan-br)}
.callout{background:linear-gradient(180deg,var(--s3),var(--s1));border:1px solid var(--b2);border-radius:16px;padding:18px}
.callout .label{font-family:var(--mono);font-size:10px;color:var(--t3);letter-spacing:1px;text-transform:uppercase;margin-bottom:8px}
.callout strong{display:block;font-size:15px;margin-bottom:6px}
.section-split{display:grid;grid-template-columns:1fr;gap:10px}
.competitor-chip{display:inline-flex;padding:4px 8px;border-radius:999px;font-family:var(--mono);font-size:10px;border:1px solid var(--b2);background:var(--s2);color:var(--t2)}
.competitor-wrap{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.competitor-card{background:var(--s1);border:1px solid var(--b1);border-radius:16px;padding:18px}
.footer-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}
@media(max-width:980px){.grid,.tam-grid,.signal-grid,.callout-grid,.competitor-wrap{grid-template-columns:1fr}.hero h1{font-size:38px}}
"""

def score_class(v):
    if v >= 75: return "good"
    if v >= 50: return "mid"
    return "bad"

def chart_svg(series, labels):
    width, height = 720, 220
    left, bottom = 48, 180
    maxv = max(series) or 1
    step = (width - 90) / (len(series)-1)
    coords = []
    for i, p in enumerate(series):
        x = left + i*step
        y = bottom - (p/maxv)*130
        coords.append((x,y,p))
    poly = " ".join(f"{x},{y}" for x,y,_ in coords)
    labels_svg = "".join(f'<text x="{x}" y="{bottom+24}" fill="#505878" font-size="11" text-anchor="middle">{labels[i]}</text>' for i,(x,y,_) in enumerate(coords))
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="4.5" fill="#E8A832"/><text x="{x}" y="{y-10}" fill="#ECF0F8" font-size="11" text-anchor="middle">{p}</text>' for x,y,p in coords)
    grid = "".join(f'<line x1="{left}" y1="{yy}" x2="{width-20}" y2="{yy}" stroke="#1D2136" stroke-width="1"/>' for yy in [50,82,114,146,178])
    return f'<svg viewBox="0 0 {width} {height}" aria-label="Trend chart">{grid}<polyline fill="none" stroke="#E8A832" stroke-width="3" points="{poly}" stroke-linecap="round" stroke-linejoin="round"></polyline>{dots}{labels_svg}</svg>'

def metric_badges(report):
    s = report["scoring"]
    rec = report["scoring"]["recommendation"].replace("_"," ").title()
    urgency = report["market_research"]["buyer_urgency"]["level"].title()
    return f"""
    <div class="mini-badges">
      <div class="mini-badge good">Confidence {s['overall_confidence']}</div>
      <div class="mini-badge amber">Recommendation {rec}</div>
      <div class="mini-badge cyan">Urgency {urgency}</div>
    </div>
    """

def render_section(section, locked=False):
    paragraphs = "".join(f"<p class='note'>{p}</p>" for p in section["paragraphs"])
    bullets = "".join(f"<li>{b}</li>" for b in section["bullets"])
    overlay = '<div class="lock-overlay"><div class="kicker">PRO only</div><div class="note">This section is available on PRO only.</div><a class="btn btn-gold" href="#">Upgrade</a></div>' if locked else ""
    return f"""
    <div class="card {'locked' if locked else ''}">
      <div class="kicker">Section</div>
      <div class="section-title">{section['title']}</div>
      {paragraphs}
      <ul class="takeaways">{bullets}</ul>
      {overlay}
    </div>
    """

def render_competitor_cards(report, plan):
    comps = report["competitor_insights"]["competitor_table"]
    cards = []
    for c in comps:
        cards.append(f"""
        <div class="competitor-card">
          <div class="kicker">Competitor</div>
          <div class="section-title">{c['name']}</div>
          <div class="mini-badges">
            <div class="competitor-chip">{c['type'].title()}</div>
            <div class="competitor-chip">{c['pricing']}</div>
          </div>
          <p class="note"><strong style="color:var(--t1)">Positioning:</strong> {c['positioning']}</p>
          <p class="note"><strong style="color:var(--t1)">Strength:</strong> {c['strength']}</p>
          <p class="note"><strong style="color:var(--t1)">Weakness:</strong> {c['weakness']}</p>
          <p class="note"><strong style="color:var(--t1)">Why it matters:</strong> {c['gap_relevance']}</p>
        </div>
        """)
    locked = plan == "starter"
    overlay = '<div class="lock-overlay"><div class="kicker">PRO only</div><div class="note">Full competitor blocks are available on PRO.</div><a class="btn btn-gold" href="#">Upgrade</a></div>' if locked else ""
    return f"""
    <div class="card {'locked' if locked else ''}">
      <div class="kicker">Competitor insights</div>
      <div class="section-title">Landscape snapshot</div>
      <div class="competitor-wrap">{''.join(cards)}</div>
      {overlay}
    </div>
    """

def render_report(report, plan="pro"):
    s = report["scoring"]
    rec = report["scoring"]["recommendation"].replace("_"," ").title()
    scores = "".join(f'<div class="score {score_class(v)}">{label} {v}</div>' for label, v in [
        ("Market", s["market_score"]), ("Revenue", s["revenue_score"]), ("Competition", s["competition_score"]), ("Difficulty", s["difficulty_score"])
    ])
    tam_locked = plan == "starter"
    tam_block = f"""
    <div class="tam-grid {'locked' if tam_locked else ''}">
      <div class="card"><div class="kicker">TAM</div><div class="tam-value">{report['market_research']['market_size']['tam']['display']}</div><div class="note">Total addressable market</div></div>
      <div class="card"><div class="kicker">SAM</div><div class="tam-value">{report['market_research']['market_size']['sam']['display']}</div><div class="note">Serviceable available market</div></div>
      <div class="card"><div class="kicker">SOM</div><div class="tam-value">{report['market_research']['market_size']['som']['display']}</div><div class="note">Serviceable obtainable market</div></div>
      {('<div class="lock-overlay"><div class="kicker">PRO only</div><div class="note">TAM / SAM / SOM blocks are part of PRO report depth.</div><a class="btn btn-gold" href="#">Upgrade</a></div>' if tam_locked else '')}
    </div>
    """
    chart_locked = plan == "starter"
    chart = f"""
    <div class="card {'locked' if chart_locked else ''}">
      <div class="kicker">Momentum</div>
      <div class="section-title">{report['visuals']['trend_chart']['label']}</div>
      <div class="mini-badges">
        <div class="mini-badge cyan">Signal strength {report['scoring']['signal_strength_score']}</div>
        <div class="mini-badge amber">Category {report['meta']['category_primary']}</div>
      </div>
      <div class="note">{report['market_research']['market_overview']['summary']}</div>
      {chart_svg(report['visuals']['trend_chart']['series'], report['visuals']['trend_chart']['x_labels'])}
      {('<div class="lock-overlay"><div class="kicker">PRO only</div><div class="note">Trend chart is available on PRO.</div><a class="btn btn-gold" href="#">Upgrade</a></div>' if chart_locked else '')}
    </div>
    """
    signal_grid = f"""
    <div class="signal-grid">
      <div class="callout">
        <div class="label">Recommendation</div>
        <strong>{rec}</strong>
        <div class="note">{report['verdict']['summary']}</div>
      </div>
      <div class="callout">
        <div class="label">Buyer urgency</div>
        <strong>{report['market_research']['buyer_urgency']['level'].title()}</strong>
        <div class="note">{report['market_research']['buyer_urgency']['summary']}</div>
      </div>
      <div class="callout">
        <div class="label">Positioning gap</div>
        <strong>{report['competitor_insights']['positioning_gap']['headline']}</strong>
        <div class="note">{report['competitor_insights']['positioning_gap']['summary']}</div>
      </div>
    </div>
    """
    callout_grid = f"""
    <div class="callout-grid">
      <div class="callout">
        <div class="label">Best entry wedge</div>
        <strong>{report['strategy_frameworks']['entry_wedge']['headline']}</strong>
        <div class="note">{report['strategy_frameworks']['entry_wedge']['summary']}</div>
      </div>
      <div class="callout">
        <div class="label">Business model</div>
        <strong>{report['business_model']['pricing_model'].replace('_',' ').title()}</strong>
        <div class="note">{report['business_model']['monetization_summary']}</div>
      </div>
      <div class="callout">
        <div class="label">Next best action</div>
        <strong>Validate first</strong>
        <div class="note">{report['verdict']['next_best_action']}</div>
      </div>
    </div>
    """
    keys = [
        "market_overview_section",
        "community_signals_section",
        "positioning_gap_section",
        "entry_wedge_section",
        "business_model_section",
        "verdict_section",
    ]
    cards = []
    for key in keys:
        locked = plan == "starter" and key in {"entry_wedge_section", "business_model_section"}
        cards.append(render_section(report["expanded_sections"][key], locked=locked))
    pdf_btn = '<a class="btn btn-gold" href="#">Download PDF export</a>' if plan == "pro" else '<a class="btn btn-gold" href="#">Upgrade for PDF export</a>'
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{report['meta']['title']}</title><style>{CSS}</style></head><body>
    <div class="wrap">
      <div class="hero">
        <div class="kicker">{report['meta']['category_primary']} - {'PRO' if plan == 'pro' else 'STARTER'}</div>
        <h1>{report['meta']['title']}</h1>
        <p>{report['meta']['subtitle']}</p>
        {metric_badges(report)}
        <div class="score-row">{scores}</div>
      </div>
      {signal_grid}
      {tam_block}
      {chart}
      {callout_grid}
      {render_competitor_cards(report, plan)}
      <div class="grid">{''.join(cards)}</div>
      <div class="footer-actions">{pdf_btn}<a class="btn" href="#">Back to dashboard</a></div>
    </div>
    </body></html>"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="output/report.json")
    ap.add_argument("--plan", choices=["starter", "pro"], default="pro")
    args = ap.parse_args()

    report = json.loads((BASE / args.input).read_text(encoding="utf-8"))
    html = render_report(report, plan=args.plan)

    out_dir = BASE / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"report-{args.plan}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
