#! /usr/bin/env python

"""
Utility for taking SF's public "Street Data Extract" data set
(https://sfelections.org/tools/election_data/dataset.php?ATAB=d1970-01-01)
and the proprietary precincts.tsv file which maps precinct number to district
and neighborhood, producing a data set that can be used by find_neighborhood.py
to determine neighborhood given a street address.

Sample usage:
  ./join_data.py elections-data.txt precincts.tsv > ../src/data/neighborhood_data.tsv
"""

import sys

import pandas as pd

OUTPUT_COLUMNS = [
    "StreetName",
    "StreetType",
    "SideCode",
    "HouseNumLo",
    "HouseNumHi",
    "District",
    "Neighborhood",
]


def join_election_data(election_filename: str, precinct_filename: str) -> None:
    """Joins the two datasets and outputs to stdout."""
    election_data = pd.read_csv(election_filename, "\t", low_memory=False)
    precinct_data = pd.read_csv(precinct_filename, "\t")
    assert precinct_data["PrecinctID"].is_unique
    data = pd.merge(election_data, precinct_data, on="PrecinctID", how="inner")
    # Filter out weird records
    data = data[~data["StreetName"].str.startswith("@")]
    data["StreetName"] = data["StreetName"].str.lower()
    data["StreetType"] = data["StreetType"].str.lower()
    data["SideCode"] = data["SideCode"].str.upper()
    data.sort_values(by=OUTPUT_COLUMNS, inplace=True)
    data.to_csv(sys.stdout, sep="\t", index=False, columns=OUTPUT_COLUMNS)


if __name__ == "__main__":
    assert len(sys.argv) == 3
    join_election_data(sys.argv[1], sys.argv[2])
