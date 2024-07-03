.PHONY: install-dev install run format lint

.venv:
	python3 -m venv .venv

install: .venv
	.venv/bin/pip install -e .

install-dev: .venv install
	.venv/bin/pip install -r requirements-dev.txt

run: .venv
	.venv/bin/python src/harness_tui/app.py

format: .venv
	.venv/bin/ruff format src

lint: .venv
	.venv/bin/ruff check src
