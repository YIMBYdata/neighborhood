.PHONY: run run_docker test venv

.DEFAULT_GOAL = run
.SHELLFLAGS = -ec

# Constants
APP_NAME = neighborhood
FUNCTION_TARGET = handle_request
FUNCTION_TARGET_ENV = GOOGLE_FUNCTION_TARGET=$(FUNCTION_TARGET)

run:
	# Runs a local debug server.
	. .venv/bin/activate; \
	cd src; \
	functions-framework --target $(FUNCTION_TARGET) --debug

run_docker:
	# Runs a local Docker server.
	pack build $(APP_NAME) \
		--path src \
		--env $(FUNCTION_TARGET_ENV) \
		--builder gcr.io/buildpacks/builder:v1
	docker run --rm -it -p 8080:8080 $(APP_NAME)

test:
	. ./.venv/bin/activate; \
	pytest; \
	pytype src

venv:
	# Sets up the virtual environment.
	python -m venv .venv; \
	source .venv/bin/activate; \
	python -m pip install --upgrade pip wheel; \
	python -m pip install -r src/requirements.txt; \
	python -m pip install -r src/requirements-test.txt
