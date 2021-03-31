#! /usr/bin/env python

import json

import click
import flask

import neighborhood


def handle_request(request: flask.Request) -> str:
    address = request.args.get("address", "")
    data = neighborhood.find(address)
    return json.dumps(data)


# pylint: disable=no-value-for-parameter
# ./src/main.py "123 Main St"
@click.command()
@click.argument("address")
def run_cli(address: str) -> None:
    print(neighborhood.find(address))


if __name__ == "__main__":
    run_cli()