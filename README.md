# MES Trading AI — Python + Quantower Read-Only Bridge

A portfolio-ready, **runnable research software demo** built around MES futures minute bars. Includes a local dashboard, defensive CSV ingestion, a Quantower-compatible file bridge, example synthetic candles, and unit tests.

> **Status: research demonstration, not live-trading certified.** The educational EMA-cross detector is **not** one of the original 41 frozen MES specialists. The 41-detector source and historical-to-live parity are not verified in this repository. No broker orders are placed, and no profitability is claimed.

## Quick start (Python 3.10+, no pip install required)

```powershell
python -m unittest discover -s tests -v
python -m mes_ai.dashboard
```

Open http://127.0.0.1:8765. The default dashboard uses synthetic sample data (NOT real MES history).

## Quantower bridge (Windows)

1. In Quantower, use an available historical-data export or a separately configured data exporter to write **completed** MES 1-minute candles to `C:\\MES\\completed_1m.csv`. This repository **does not install or implement a Quantower API plugin/exporter**. Exporter availability and configuration depend on your Quantower installation.
2. Required CSV header: `timestamp,open,high,low,close,volume,complete`. Timestamp is ISO-8601 with UTC offset and identifies the **start** of the minute. Each row must have `complete=true` only after the candle closes. Use chronological, deduplicated rows. Include contract symbol/roll selection in your external data provenance documentation.
3. Run the fail-closed read-only bridge:

```powershell
python -m mes_ai.bridge --csv "C:\\MES\\completed_1m.csv" --output "C:\\MES\\bridge_status.json" --watch
```

4. To view the exported CSV in the dashboard:

```powershell
python -m mes_ai.dashboard --csv "C:\\MES\\completed_1m.csv"
```

The bridge checks timestamp freshness, chronology, OHLCV validity, and last-bar continuity. It does **not** establish authenticated Quantower connectivity, enforce exchange calendars, guarantee exporter atomicity, verify historical contract selection, or reconcile manual positions. If the export is stale, invalid, missing, or has a recent gap, the bridge blocks research signals. Use atomic file replacement when exporting to avoid partial reads.

## Project architecture

- `mes_ai/core.py`: strict completed-bar parser and transparent research-only EMA-cross example
- `mes_ai/bridge.py`: read-only CSV polling and atomic JSON status output
- `mes_ai/dashboard.py`: localhost dashboard and JSON endpoint
- `tests/`: defensive data and smoke tests
- `sample_data/`: explicitly synthetic fixture
- `RESEARCH_STATUS.md`: frozen 41-specialist background and verification limitations

## Roadmap

- [ ] Recover all 41 original parent event generators and exact frozen definitions
- [ ] Independently verify detector parity against reference events
- [ ] Complete causal contract-selection and historical replay validation
- [ ] Build-only 1R/2R/3R comparisons with fixed execution assumptions
- [ ] Freeze candidates before truly prospective paper-forward observations
- [ ] Test actual Quantower export, restarts, rollover and gaps on Windows

## Resume-friendly description

**MES Market Data Research Platform (Python):** Developed a read-only futures market-data pipeline with completed-candle validation, fail-closed freshness checks, a local research dashboard, JSON status reporting, and automated tests. Designed a reproducible framework for historical detector validation and risk/reward experimentation.

MIT licensed. No financial advice or performance guarantees.
