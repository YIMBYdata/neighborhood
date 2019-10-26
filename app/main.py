#! /usr/bin/env python

import flask
import os

from find_neighborhood import db

app = flask.Flask(__name__)


@app.route("/sf/district")
def district():
    return db.find_district(flask.request.args.get("address", ""))


@app.route("/sf/neighborhood")
def neighborhood():
    return db.find_neighborhood(flask.request.args.get("address", ""))


if __name__ == '__main__':
    app.run(debug=True, port=os.environ.get('PORT', 8080))
