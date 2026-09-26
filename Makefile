.PHONY: install demo api ui test corpus metrics fixtures

VENV ?= .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

install:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	cd aegis && PYTHONPATH=. ../$(PY) demos/generate_fixtures.py

api:
	cd aegis && PYTHONPATH=. ../$(VENV)/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

ui:
	cd aegis && PYTHONPATH=. ../$(VENV)/bin/streamlit run ui/console.py --server.port 8501

demo:
	@echo "Terminal 1: make api"
	@echo "Terminal 2: make ui"
	@echo "Open http://localhost:8501 → Demo Scenarios"

fixtures:
	cd aegis && PYTHONPATH=. ../$(PY) demos/generate_fixtures.py

test:
	cd aegis && PYTHONPATH=. ../$(PYTEST) -q tests/

corpus:
	cd aegis && PYTHONPATH=. ../$(PY) -m corpus.evaluate

metrics:
	cd aegis && PYTHONPATH=. ../$(PY) -m corpus.evaluate --json
