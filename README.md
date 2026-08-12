# India Consumption Pulse

A polished Streamlit dashboard for exploring India's inflation, urban consumer confidence, GST revenue, and passenger-vehicle sales.

## What is included

- A source and availability audit before analysis
- Clean, bundled CSV snapshots with consistent monthly dates
- Interactive KPI cards, indexed trend comparison, correlations, and downloadable filtered data
- Explicit coverage and methodology notes (including the 2026 CPI base change and SIAM coverage caveats)

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Python 3.11–3.14 is supported. The Altair 6 requirement is intentional: older
Altair 5 builds can fail during import on Python 3.14 because of the newer
`TypedDict` implementation.

The application does not require network access at runtime. Data are frozen official-source snapshots; see `data/source_catalog.csv` and the in-app **Data desk**.

## Data policy

The requested cut-off is July 2026 (the month before the project date). A series is not extended merely to match that cut-off when the official publication was not available. Each chart therefore displays its own `latest_period`, and the overview labels the common comparable window.

## Project structure

```text
app.py                  Streamlit app
data/*.csv              Clean analytical snapshots and source catalog
tests/test_data.py      Data-contract tests
.streamlit/config.toml  Theme
```
