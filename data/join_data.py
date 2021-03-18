#! /usr/bin/env python

"""
Utility for taking SF's public "Street Data Extract" data set
(https://sfelections.org/tools/election_data/dataset.php?ATAB=d1970-01-01)
and the proprietary precincts.tsv file which maps precinct number to district
and neighborhood, producing a data set that can be used by find_neighborhood.py
to determine neighborhood given a street address.

Sample usage:
  ./join_data.py elections-data.txt precincts.tsv | gzip \
  > neighborhood_data.tsv.gz
"""

import csv
import sys


def join_election_data(election_filename, precinct_filename):
    """Joins the two datasets and outputs to stdout."""
    # Read in the precinct data.
    precinct_data = {}
    with open(precinct_filename) as precinct_fd:
        reader = csv.reader(precinct_fd, delimiter="\t")
        for precinct, district, neighborhood in reader:
            assert precinct not in precinct_data
            precinct_data[precinct] = district, neighborhood

    # Read in the elections data and perform a join, filtering to only keep
    # the fields that find_neighborhood.py needs and normalizing the data to
    # lowercase.
    output = []
    with open(election_filename) as election_fd:
        reader = csv.DictReader(election_fd, delimiter="\t")
        for row in reader:
            street_name = row["StreetName"].lower()
            if street_name.startswith("@"):
                continue  # Filter out some weird records.
            district, neighborhood = precinct_data[row["PrecinctID"]]
            output.append(
                [
                    street_name,
                    row["StreetType"].lower(),
                    row["SideCode"].upper(),
                    row["HouseNumLo"],
                    row["HouseNumHi"],
                    district,
                    neighborhood,
                ]
            )

    # Sort the output so it's easier for a human to parse.
    writer = csv.writer(sys.stdout, delimiter="\t")
    writer.writerow(
        [
            "StreetName",
            "StreetType",
            "SideCode",
            "HouseNumLo",
            "HouseNumHi",
            "District",
            "Neighborhood",
        ]
    )
    for row in sorted(output):
        writer.writerow(row)


if __name__ == "__main__":
    assert len(sys.argv) == 3
    join_election_data(sys.argv[1], sys.argv[2])
