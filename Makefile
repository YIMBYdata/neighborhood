.PHONY: build run run_docker run_docker_image test venv

.DEFAULT_GOAL = run
.SHELLFLAGS = -ec

# Constants
APP_NAME = neighborhood
FUNCTION_TARGET = handle_request

# Builds a local Docker image with pack.
build:
	pack build $(APP_NAME) \
		--path src \
		--env GOOGLE_FUNCTION_TARGET=$(FUNCTION_TARGET) \
		--builder gcr.io/buildpacks/builder:v1

# Runs a local debug server.
run:
	. .venv/bin/activate; \
	cd src; \
	functions-framework --target $(FUNCTION_TARGET) --debug

# Builds and runs a local Docker image.
run_docker: build run_docker_image

# Runs a local Docker image.
run_docker_image:
	docker run --rm -it -p 8080:8080 $(APP_NAME)

test:
	. ./.venv/bin/activate; \
	pytest; \
	pytype src

# Sets up the virtual environment.
venv:
	python -m venv .venv; \
	source .venv/bin/activate; \
	python -m pip install --upgrade pip wheel; \
	python -m pip install -r src/requirements.txt; \
	python -m pip install -r src/requirements-test.txt
