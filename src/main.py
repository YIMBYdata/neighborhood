#! /usr/bin/env python

import json

import click

import neighborhood


def handle_request(request):
    address = request.args.get("address", "")
    data = neighborhood.db.find(address)
    return json.dumps(data)


# ./src/main.py "123 Main St"
@click.command()
@click.argument("address")
def run_cli(address):
    print(neighborhood.find(address))


if __name__ == "__main__":
    run_cli()