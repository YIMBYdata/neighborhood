#! /usr/bin/env python

from dataclasses import asdict
import json

import click
import flask

import neighborhood


def find(address: str) -> str:
    results = neighborhood.find(address)
    return json.dumps([asdict(r) for r in results])


def handle_request(request: flask.Request) -> str:
    return find(request.args.get("address", ""))


# pylint: disable=no-value-for-parameter
# ./src/main.py "123 Main St"
@click.command()
@click.argument("address")
def run_cli(address: str) -> None:
    print(find(address))


if __name__ == "__main__":
    run_cli()