#!/bin/bash
# Runs a local server using Docker, which is the way it's deployed.
set -ae

APP_NAME="neighborhood"

cd src
pack build $APP_NAME \
    --env GOOGLE_FUNCTION_TARGET="handle_request" \
    --builder gcr.io/buildpacks/builder:v1
docker run --rm -it -p 8080:8080 -e PORT=8080 $APP_NAME
