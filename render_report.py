#!/usr/bin/env python3
import json, argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#07080C;--s1:#0B0D15;--s2:#10131E;--b1:#1D2136;--b2:#252B44;
  --t1:#ECF0F8;--t2:#8892B0;--t3:#505878;--gold:#C8861A;--gold-l:#E8A832;
  --gold-bg:rgba(200,134,26,.07);--gold-br:rgba(200,134,26,.22);
  --green:#22C55E;--green-bg:rgba(34,197,94,.07);--green-br:rgba(34,197,94,.20);
  --amber:#F59E0B;--amber-bg:rgba(245,158,11,.07);--amber-br:rgba(245,158,11,.20);
  --display:Georgia,serif;--body:Arial,sans-serif;--mono:monospace;
}
body{font-family:var(--body);background:var(--bg);color:var(--t1);line-height:1.6;font-size:15px}
.wrap{max-width:1100px;margin:0 auto;padding:32px 24px 48px}
.hero{background:linear-gradient(160deg,#120F05,var(--s1));border:1px solid var(--gold-br);border-radius:20px;padding:28px;margin-bottom:18px}
.kicker{font-family:var(--mono);font-size:10px;color:var(--t3);letter-spacing:1px;text-transform:uppercase;margin-bottom:10px}
.hero h1{font-family:var(--display);font-size:44px;line-height:1.02;margin-bottom:14px}
.hero p,.note{color:var(--t2)}
.score-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.score{font-family:var(--mono);font-size:12px;padding:6px 9px;border-radius:8px;border:1px solid var(--b2)}
.score.good{color:var(--green);background:var(--green-bg);border-color:var(--green-br)}
.score.mid{color:var(--amber);background:var(--amber-bg);border-color:var(--amber-br)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.card{background:var(--s1);border:1px solid var(--b1);border-radius:16px;padding:20px}
.section-title{font-size:16px;margin-bottom:8px}
.tam-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:14px;position:relative}
.tam-value{font-family:var(--mono);font-size:26px;color:var(--gold-l);margin-bottom:6px}
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
@media(max-width:900px){.grid,.tam-grid{grid-template-columns:1fr}.hero h1{font-size:36px}}
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

def render_report(report, plan="pro"):
    s = report["scoring"]
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
    comp_locked = plan == "starter"
    comp_rows = "".join(f"<tr><td>{r['name']}</td><td>{r['positioning']}</td><td>{r['pricing']}</td><td>{r['gap_relevance']}</td></tr>" for r in report["competitor_insights"]["competitor_table"])
    comp_table = f"""
    <div class="table-wrap {'locked' if comp_locked else ''}">
      <table class="table">
        <thead><tr><th>Competitor</th><th>Positioning</th><th>Pricing</th><th>Gap / opening</th></tr></thead>
        <tbody>{comp_rows}</tbody>
      </table>
      {('<div class="lock-overlay"><div class="kicker">PRO only</div><div class="note">Competitor table is available on PRO.</div><a class="btn btn-gold" href="#">Upgrade</a></div>' if comp_locked else '')}
    </div>
    """
    chart_locked = plan == "starter"
    chart = f"""
    <div class="card {'locked' if chart_locked else ''}">
      <div class="kicker">Momentum</div>
      <div class="section-title">{report['visuals']['trend_chart']['label']}</div>
      <div class="note">{report['market_research']['market_overview']['summary']}</div>
      {chart_svg(report['visuals']['trend_chart']['series'], report['visuals']['trend_chart']['x_labels'])}
      {('<div class="lock-overlay"><div class="kicker">PRO only</div><div class="note">Trend chart is available on PRO.</div><a class="btn btn-gold" href="#">Upgrade</a></div>' if chart_locked else '')}
    </div>
    """
    sections = [
        ("Market overview", report["market_research"]["market_overview"]["summary"]),
        ("Community signals", report["community_signals"]["summary"]),
        ("Positioning gap", report["competitor_insights"]["positioning_gap"]["summary"]),
        ("Entry wedge", report["strategy_frameworks"]["entry_wedge"]["summary"]),
        ("Business model", report["business_model"]["monetization_summary"]),
        ("Verdict", report["verdict"]["summary"]),
    ]
    cards = []
    for idx, (title, body) in enumerate(sections):
        locked = (plan == "starter" and idx in [3, 4])
        cards.append(f"""
        <div class="card {'locked' if locked else ''}">
          <div class="kicker">Section</div>
          <div class="section-title">{title}</div>
          <div class="note">{body}</div>
          {('<div class="lock-overlay"><div class="kicker">PRO only</div><div class="note">This section is available on PRO only.</div><a class="btn btn-gold" href="#">Upgrade</a></div>' if locked else '')}
        </div>
        """)
    pdf_btn = '<a class="btn btn-gold" href="#">Download PDF export</a>' if plan == "pro" else '<a class="btn btn-gold" href="#">Upgrade for PDF export</a>'
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{report['meta']['title']}</title><style>{CSS}</style></head><body>
    <div class="wrap">
      <div class="hero">
        <div class="kicker">{report['meta']['category_primary']} - {'PRO' if plan == 'pro' else 'STARTER'}</div>
        <h1>{report['meta']['title']}</h1>
        <p>{report['meta']['subtitle']}</p>
        <div class="score-row">{scores}</div>
      </div>
      {tam_block}
      {chart}
      {comp_table}
      <div class="grid">{''.join(cards)}</div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:18px">{pdf_btn}<a class="btn" href="#">Back to dashboard</a></div>
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
