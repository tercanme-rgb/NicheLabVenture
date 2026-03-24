# NicheLab Generation Engine V7.1

This version adds an editorial cleanup pass.

## Improvements over v7
- fixes title rewrite edge-cases
- removes awkward duplicates like `AI AI QA`
- improves shortlist ordering
- exports a publish-ready featured shortlist

## Quick start

```bash
python .\run_pipeline.py --category "AI Automation"
```

Open:
- `output\report-starter.html`
- `output\report-pro.html`
- `output\featured-shortlist.json`
