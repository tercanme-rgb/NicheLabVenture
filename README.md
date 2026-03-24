# NicheLab First Working Generation Engine

This is the first working report generation engine.

## What it does
1. Takes a visible category such as `Micro-SaaS`
2. Generates candidate opportunities
3. Scores and ranks those candidates
4. Converts the top candidate into a report JSON
5. Renders Starter and PRO HTML report pages

## Files
- `category-architecture.json`
- `generate_candidates.py`
- `score_candidates.py`
- `generate_report_json.py`
- `render_report.py`
- `run_pipeline.py`

## Quick start

```bash
python run_pipeline.py --category "Micro-SaaS"
```

Then open:

```text
output/report-starter.html
output/report-pro.html
output/report.json
```

## Example categories
- Micro-SaaS
- AI Automation
- E-Commerce
- Creator Economy
- Local Business
- B2B Services
- Finance & Admin

## Notes
- This engine is heuristic and template-based
- It does not require OpenAI or any external API
- It is designed as a first working production engine, not the final quality layer
- You can later replace any stage with stronger data or LLM generation
