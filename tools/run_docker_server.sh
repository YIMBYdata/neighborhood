#!/bin/bash
# Runs a local server using Docker, which is the way it's deployed.
set -ae

APP_NAME="neighborhood"

docker build -t $APP_NAME .
docker run --rm -it -p 8080:8080 -e PORT=8080 $APP_NAME
