PYTHON_BASE := python3.12
PYTHON_VENV := .venv
PYTHON := $(PYTHON_VENV)/bin/python
PYTHON_PIP := $(PYTHON_VENV)/bin/pip
PYTHON_DEPS := requirements.txt

.PHONY: generate-venv remove-venv regenerate-env

generate-venv:
	$(PYTHON_BASE) -m venv $(PYTHON_VENV)
	$(PYTHON) -m ensurepip
	$(PYTHON_PIP) install --upgrade pip
	$(PYTHON_PIP) install -r $(PYTHON_DEPS)

remove-venv:
	rm -rf $(PYTHON_VENV)

regenerate-env: remove-venv generate-venv
