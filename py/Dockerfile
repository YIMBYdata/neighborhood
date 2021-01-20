# Bundles Python 3.8 with a production web server.
FROM tiangolo/uvicorn-gunicorn:python3.8

WORKDIR /app
COPY app /app
RUN pip install -r requirements.txt

# Run locally: 
# $ docker run --rm -it -p 8080:80 neighborhood

# Alternative:
# Add gunicorn==19.9.0 to requirements.txt
# FROM python:3.7-slim
# WORKDIR /app
# COPY app /app
# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
