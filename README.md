
# NicheLab site integration

This package connects the site UI to the auto-generated report files.

## Files
- `index.html`
- `dashboard.html`

## What they do
- `index.html` reads:
  - `generated-reports/homepage-feed.json`
  - `generated-reports/reports-manifest.json`
- `dashboard.html` reads:
  - `generated-reports/homepage-feed.json`
  - `generated-reports/reports-manifest.json`

## Result
When GitHub Actions creates new reports, the homepage featured report and dashboard report list update automatically.

## Replace in repo
- replace current `index.html`
- replace current `dashboard.html`

