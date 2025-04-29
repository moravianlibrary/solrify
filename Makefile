PYTHON_BASE := python3.12

PYTHON_VENV := .venv
PYTHON := $(PYTHON_VENV)/bin/python
PYTHON_PIP := $(PYTHON_VENV)/bin/pip

PYTHON_DEPS := requirements.txt

PYTHON_TESTS_LIB := coverage
TESTS_DIR := tests

.PHONY: generate-venv remove-venv regenerate-env

generate-venv:
	$(PYTHON_BASE) -m venv $(PYTHON_VENV)
	$(PYTHON) -m ensurepip
	$(PYTHON_PIP) install --upgrade pip
	$(PYTHON_PIP) install -r $(PYTHON_DEPS)
	$(PYTHON_PIP) install $(PYTHON_TESTS_LIB)

remove-venv:
	rm -rf $(PYTHON_VENV)

regenerate-env: remove-venv generate-venv

test:
	$(PYTHON) -m coverage run -m unittest discover -s $(TESTS_DIR) \
	&& $(PYTHON) -m coverage html \
	&& $(PYTHON) -m coverage report

open-report:
	xdg-open htmlcov/index.html &
