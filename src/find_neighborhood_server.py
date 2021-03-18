#! /usr/bin/env python

import flask
import os

import find_neighborhood

app = flask.Flask(__name__)


@app.route("/sf")
def find():
    return find_neighborhood.db.find(flask.request.args.get("address", ""))


if __name__ == "__main__":
    app.run(debug=True, port=os.environ.get("PORT", 8080))
