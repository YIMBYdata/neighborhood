#!/bin/bash
# Runs all the tests in the project.
set -e

source .venv/bin/activate
pytest
pytype src
