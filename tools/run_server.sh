#!/bin/bash
# Runs a local server in debug mode, which supports hot reloading.
set -e

source .venv/bin/activate
cd src
functions-framework --target=handle_request --debug
