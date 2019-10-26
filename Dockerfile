# Bundles Python 3.7 with Flask and a production web server.
FROM tiangolo/uwsgi-nginx-flask:python3.7

WORKDIR /app
COPY app /app
RUN pip install -r requirements.txt

# Run locally: 
# $ docker run --rm -it -p 8080:80 neighborhood
