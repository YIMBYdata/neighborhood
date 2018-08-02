# Bundles Python 3.6 with Flask and a production web server.
FROM tiangolo/uwsgi-nginx-flask:python3.6

# Set the working directory to /app
WORKDIR /app

# Copy in project files.
COPY ./app /app
COPY ./data/neighborhood_data.tsv.gz /app
COPY requirements.txt /app

# Install dependencies.
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Set environment variables.
ENV NEIGHBORHOOD_DATA_FILE "neighborhood_data.tsv.gz"

# Notes:
# To run the simple Flask server in a Docker contains, do the following:
# Replace the FROM above with: FROM python:3.6.6-slim
# Add: CMD ["python", "find_neighborhood_server.py", "neighborhood_data.tsv.gz"]
# Change add host="0.0.0.0" to app.run in find_neighborhood_server.py