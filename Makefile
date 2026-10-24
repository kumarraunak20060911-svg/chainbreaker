PYTHON ?= python
export PYTHONPATH := src

install:
	$(PYTHON) -m pip install -e ".[dev]"

db-upgrade:
	$(PYTHON) -m alembic upgrade head

run:
	$(PYTHON) -m uvicorn chainbreaker.api.app:app --reload --host 127.0.0.1 --port 8000

demo:
	$(PYTHON) scripts/seed_demo.py

test:
	pytest -q

compile:
	$(PYTHON) -m compileall -q src tests evaluation scripts
