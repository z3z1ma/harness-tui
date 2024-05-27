.PHONY: install-dev run

.venv:
	python3 -m venv .venv

install-dev: .venv
	.venv/bin/pip install -r requirements.txt

run: .venv
	.venv/bin/python src/harness_tui/app.py
