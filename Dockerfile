FROM python:3.8-slim

WORKDIR /app
COPY app /app
RUN pip install -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 find_neighborhood_server:app
