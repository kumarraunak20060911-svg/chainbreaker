# Contributing to ChainBreaker

Thank you for your interest in contributing to ChainBreaker!

## Development Guidelines

1. **Python 3.12+ Only:** ChainBreaker is strictly Python 3.12+ with zero Node.js / npm dependencies. Server-rendered Jinja2 templates and dynamic SVG charts provide zero-dependency operational dashboards.
2. **Deterministic & Explainable:** All analytical modules (Fellegi-Sunter correlation, Viterbi DAG inference, Pareto min-cut containment) must remain mathematically explainable and produce deterministic outputs.
3. **Safety First:** Never allow automated containment recommendations to take `LIFE_SAFETY` infrastructure offline. All containment actuation requires human approval receipts.

## Running Tests

Before submitting a pull request, ensure all tests pass:

```bash
# Run full unit and integration test suite
python -m pytest tests/ -v

# Run scientific evaluation benchmarks
PYTHONPATH=src python evaluation/run_benchmark.py
PYTHONPATH=src python evaluation/run_ablation.py
```
