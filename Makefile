PYTHON ?= python
export PYTHONPATH := src

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	uvicorn chainbreaker.api.app:app --reload --host 127.0.0.1 --port 8000

demo:
	$(PYTHON) scripts/seed_demo.py

test:
	pytest -q

compile:
	$(PYTHON) -m compileall -q src tests evaluation scripts
