"""
Library that takes a data file produced by join_data.py and an address
(street number, name, and type) and produces the SF neighborhood that
address is in.

The joined data file is tab-separated with the following fields:
StreetName	StreetType	SideCode	HouseNumLo	HouseNumHi	Neighborhood

A given address is matches a row if the StreetName and StreetType match,
and the street number is in the range defined by SideCode, HouseNumLo, and
HouseNumHi (see the HouseNumRange class).
"""

from collections import namedtuple
import csv
import itertools
import os
import string
from typing import Dict, Final, Iterable, List, Optional, Tuple

import scourgify
import usaddress

# CSV row tuple
Row = namedtuple(
    "Row",
    "street_name, street_type, side_code, house_num_lo, house_num_hi, district, neighborhood",
)


def parse_street_address(street_address: str) -> Tuple[int, str, str]:
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
    return (
        int(street_number),
        parsed.get("StreetName", "").lower(),
        parsed.get("StreetNamePostType", "").lower(),
    )


class HouseNumRange:
    """
    The data file contains house number ranges defined by a side code, range
    low (inclusive) and range high (inclusive). The side code can be E for even,
    O for odd, A for all (no number range provided), or B for both. If the street
    number is withing [lo, hi] and is on the appropriate side of street, it
    matches.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        side_code: str,
        house_num_low: int,
        house_num_high: int,
        district: str,
        neighborhood: str,
    ) -> None:
        self._side_code: Final = side_code
        self._house_num_low: Final = house_num_low
        self._house_num_high: Final = house_num_high
        self.district: Final = district
        self.neighborhood: Final = neighborhood

    def matches(self, number: int) -> bool:
        if (self._side_code == "E" and number % 2 == 1) or (
            self._side_code == "O" and number % 2 == 0
        ):
            return False
        if self._side_code == "A":
            return True
        return self._house_num_low <= number <= self._house_num_high


class StreetDatabase:
    def __init__(self, data_filename: str) -> None:
        self._parsed_data: Final = self._parse(self._read(data_filename))

    def find(self, street_address: str) -> Dict[str, List[str]]:
        matches = self._find_matches(street_address)
        return {
            "district": sorted({m.district for m in matches}),
            "neighborhood": sorted({m.neighborhood for m in matches}),
        }

    def _read(self, data_filename: str) -> List[str]:
        with open(data_filename, mode="rt") as f:
            return f.readlines()

    def _parse(self, data: List[str]) -> Dict[str, Dict[str, List[HouseNumRange]]]:
        parsed_data: Dict[str, Dict[str, List[HouseNumRange]]] = {}
        reader = csv.reader(data, delimiter="\t")
        next(reader)
        for row in map(Row._make, reader):
            ranges = parsed_data.setdefault(row.street_name, {}).setdefault(
                row.street_type, []
            )
            ranges.append(
                HouseNumRange(
                    row.side_code,
                    int(row.house_num_lo),
                    int(row.house_num_hi),
                    row.district,
                    row.neighborhood,
                )
            )
        return parsed_data

    def _find_matches(self, street_address: str) -> List[HouseNumRange]:
        """
        Given the loaded data and the input address, finds HouseNumRanges
        that match. If the street_type doesn't match for a given street, we'll fall
        back to all street types for that street.
        """
        try:
            street_number, street_name, street_type = parse_street_address(
                street_address
            )
        except ValueError:
            return []
        street_data = self._parsed_data.get(street_name, {})
        ranges: Optional[Iterable[HouseNumRange]] = street_data.get(street_type)
        if not ranges:
            ranges = itertools.chain(*street_data.values())
        return [r for r in ranges if r.matches(street_number)]


_db: Final = StreetDatabase(
    os.path.join(os.path.dirname(__file__), "data/neighborhood_data.tsv")
)

find = _db.find
