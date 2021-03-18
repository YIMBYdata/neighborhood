FROM python:3.8-slim

ENV PYTHONUNBUFFERED TRUE

WORKDIR /app
COPY src /app
RUN pip install -r requirements.txt

CMD exec functions-framework --target=handle_request --port $PORT