#! /usr/bin/env python
"""
Script that takes a data file produced by join_data.py and an address
(street number, name, and type) and produces the SF neighborhood that
address is in.

The joined data file is tab-separated with the following fields:
StreetName	StreetType	SideCode	HouseNumLo	HouseNumHi	Neighborhood

A given address is matches a row if the StreetName and StreetType match,
and the street number is in the range defined by SideCode, HouseNumLo, and
HouseNumHi (see the HouseNumRange class).
"""

import csv
import gzip
import itertools
import os
import scourgify
import string
import sys
import usaddress

# CSV index constants
_STREET_NAME = 0
_STREET_TYPE = 1
_SIDE_CODE = 2
_HOUSE_NUM_LO = 3
_HOUSE_NUM_HI = 4
_DISTRICT = 5
_NEIGHBORHOOD = 6


def parse_street_address(street_address: str) -> tuple[int, str, str]:
    """Parses a raw street address to (number, name, type)."""
    if not street_address:
        raise ValueError("Empty address")
    try:
        normalized = scourgify.normalize_address_record(street_address)
    except scourgify.exceptions.UnParseableAddressError as e:
        raise ValueError(e)
    parsed, _ = usaddress.tag(normalized["address_line_1"])
    street_number: str = parsed.get("AddressNumber")
    if not street_number:
        raise ValueError(str(parsed))
    street_number = street_number.rstrip(string.ascii_letters)
    return (int(street_number), parsed.get("StreetName", "").lower(),
            parsed.get("StreetNamePostType", "").lower())


class HouseNumRange:
    """
    The data file contains house number ranges defined by a side code, range
    low (inclusive) and range high (inclusive). The side code can be E for even,
    O for odd, A for all (no number range provided), or B for both. If the street
    number is withing [lo, hi] and is on the appropriate side of street, it
    matches.
    """
    def __init__(self, side_code: str, house_num_low: int, house_num_high: int,
                 district: str, neighborhood: str):
        self._side_code = side_code
        self._house_num_low = house_num_low
        self._house_num_high = house_num_high
        self.district = district
        self.neighborhood = neighborhood

    def Matches(self, number):
        if ((self._side_code == 'E' and number % 2 == 1)
                or (self._side_code == 'O' and number % 2 == 0)):
            return False
        if self._side_code == 'A':
            return True
        return self._house_num_low <= number and number <= self._house_num_high


class StreetDatabase:
    def __init__(self, data_filename: str):
        self._parsed_data = self._parse(self._read(data_filename))

    def find(self, street_address: str) -> dict[str, list[str]]:
        matches = self._find_matches(street_address)
        return {
            "district": sorted(set([m.district for m in matches])),
            "neighborhood": sorted(set([m.neighborhood for m in matches]))
        }

    def _read(self, data_filename: str) -> list[str]:
        open_file = gzip.open if data_filename.endswith(".gz") else open
        with open_file(data_filename, mode="rt") as f:
            return f.readlines()

    def _parse(self, data: list[str]) -> dict[str, dict[str, list[HouseNumRange]]]:
        parsed_data = {}
        reader = csv.reader(data, delimiter='\t')
        next(reader)
        for row in reader:
            ranges = parsed_data.setdefault(row[_STREET_NAME], {}).setdefault(
                row[_STREET_TYPE], [])
            ranges.append(
                HouseNumRange(row[_SIDE_CODE], int(row[_HOUSE_NUM_LO]),
                              int(row[_HOUSE_NUM_HI]), row[_DISTRICT],
                              row[_NEIGHBORHOOD]))
        return parsed_data

    def _find_matches(self, street_address: str) -> list[HouseNumRange]:
        """
        Given the loaded data and the input address, finds HouseNumRanges
        that match. If the street_type doesn't match for a given street, we'll fall
        back to all street types for that street.
        """
        try:
            street_number, street_name, street_type = parse_street_address(
                street_address)
        except ValueError:
            return []
        street_data = self._parsed_data.get(street_name, {})
        ranges = street_data.get(street_type)
        if not ranges:
            ranges = itertools.chain(*street_data.values())
        return [r for r in ranges if r.Matches(street_number)]


db = StreetDatabase(
    os.path.join(os.path.dirname(__file__), 'data/neighborhood_data.tsv'))

# ./app/find_neighborhood.py "123 Main St"
if __name__ == '__main__':
    assert len(sys.argv) == 2
    print(db.find(sys.argv[1]))
