# Fat Belly Hobo - External Test Suite

Deterministic automated tests. No game code is modified for testing.

## Run locally

```bash
# Serve the game first:
python3 -m http.server 8901   # from repo root

# Then run:
cd tests && pip install -r requirements.txt
playwright install chromium
python3 run_suite.py
```

## Tests

- T01: game starts, canvas renders
- T02: QA cheat button exists and opens input
- T03: test API v2 available with scenarios
- T04: skill interaction via `trick('fart')` (deterministic)
- T05: echo scenario spawns MINI + GIANT BELLY
- T06: travel scenario for bus visual regression

Results go to `tests/results/` (report.json + screenshots).
