# Credit Score Simulator (Static + Pyodide)

This static tool estimates how common credit profile factors may influence a credit score range.

## Features
- Runs entirely in-browser with Pyodide (no backend)
- Transparent factor-by-factor score impact
- Top 3 improvement tips
- Copy Results button and mobile-friendly layout

## Run locally
```bash
cd credit-score-sim
python3 -m http.server 8000
```
Then open `http://localhost:8000`.

## Deploy on Render Static Site
- Service type: Static Site
- Build command: *(leave empty)*
- Publish directory: `.`

## Disclaimer
Estimates only. Not financial advice.
