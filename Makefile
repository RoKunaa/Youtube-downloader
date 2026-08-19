PYTHON ?= python3
VENV_DIR := .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip

.PHONY: venv install run clean check-ffmpeg

venv:
	$(PYTHON) -m venv $(VENV_DIR)

check-ffmpeg:
	@command -v ffmpeg >/dev/null 2>&1 || { echo "ERROR: ffmpeg no está instalado. En macOS puedes instalarlo con: brew install ffmpeg"; exit 1; }

install: venv
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt

run: check-ffmpeg
	@. $(VENV_DIR)/bin/activate && python Import-YT.py

clean:
	rm -rf $(VENV_DIR)
