#! /usr/bin/env python

import flask
import find_neighborhood
import sys

app = flask.Flask(__name__)

db = None
def _load_static_data(data_filename):
  global db
  db = find_neighborhood.StreetDatabase(data_filename)


@app.route("/sf/district")
def district():
  return db.find_district(flask.request.args.get("address"))


@app.route("/sf/neighborhood")
def neighborhood():
  return db.find_neighborhood(flask.request.args.get("address"))
  

# TODO: Add support for district.


if __name__ == "__main__":
  assert len(sys.argv) == 2
  _load_static_data(sys.argv[1])
  app.run()
