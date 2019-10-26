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
    dirname = os.path.dirname(__file__)
    print(dirname)
    data_filename = os.path.join(dirname, 'data/neighborhood_data.tsv.gz')
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
  app.run(debug=True, port=os.environ.get('PORT', 8080))