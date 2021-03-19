#!/bin/bash
# Initialize the virtual environment for running a local server, tests, and tools.
set -e

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install -r src/requirements.txt
python -m pip install -r src/requirements-test.txt
