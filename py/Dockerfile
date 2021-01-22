# Run locally: 
# $ docker run --rm -it -p 8080:80 neighborhood
# or
# $ cd app
# $ gunicorn -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --workers 1 main:app

FROM python:3.9-slim

WORKDIR /app
COPY app /app
RUN pip install -r requirements.txt

CMD exec gunicorn -k uvicorn.workers.UvicornWorker --bind :$PORT --workers 1  main:app
