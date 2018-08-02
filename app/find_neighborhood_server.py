#! /usr/bin/env python

import flask
import find_neighborhood
import os
import sys

app = flask.Flask(__name__)

db = None
def get_db():  
  global db
  if not db:
    print(os.getcwd())
    data_filename = os.environ['NEIGHBORHOOD_DATA_FILE']
    print("Loading initial database: " + data_filename)
    db = find_neighborhood.StreetDatabase(data_filename)
  return db


@app.route("/sf/district")
def district():
  return get_db().find_district(flask.request.args.get("address", ""))


@app.route("/sf/neighborhood")
def neighborhood():
  return get_db().find_neighborhood(flask.request.args.get("address", ""))


if __name__ == "__main__":
  assert len(sys.argv) == 2
  os.environ['NEIGHBORHOOD_DATA_FILE'] = sys.argv[1]
  app.run(debug=True)