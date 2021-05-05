"""
Library that takes a data file produced by join_data.py and an address
(street number, name, and type) and produces the SF neighborhood that
address is in.

The joined data file is tab-separated with the following fields:
StreetName	StreetType	SideCode	HouseNumLo	HouseNumHi	Neighborhood

A given address is matches a row if the StreetName and StreetType match,
and the street number is in the range defined by SideCode, HouseNumLo, and
HouseNumHi.
"""

from dataclasses import dataclass
import os
import string
from typing import Any, Dict, Final, List

import pandas as pd
import scourgify
import usaddress


@dataclass(frozen=True)
class StreetAddress:
    number: int
    name: str
    type: str

    @property
    def side_code(self) -> str:
        return "O" if self.number % 2 else "E"


def parse_street_address(street_address: str) -> StreetAddress:
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
    return StreetAddress(
        int(street_number.rstrip(string.ascii_letters)),
        parsed.get("StreetName", "").lower(),
        parsed.get("StreetNamePostType", "").lower(),
    )


class StreetDatabase:
    def __init__(self, data_filename: str) -> None:
        self._data: Final = pd.read_csv(data_filename, "\t")

    def find(self, street_address: str) -> Dict[str, List[Any]]:
        matches = self._find_matches(street_address)
        return {
            "district": sorted(set(matches["District"])),
            "neighborhood": sorted(set(matches["Neighborhood"])),
        }

    def _find_matches(self, raw_street_address: str) -> pd.DataFrame:
        """
        Given the loaded data and the input address, finds rows that match.
        If the street_type doesn't exist for a given street, we'll fall back
        to all street types for that street.
        """
        data = self._data
        try:
            street_address = parse_street_address(raw_street_address)
        except ValueError:
            return pd.DataFrame(columns=data.columns)
        street_data = data[
            (data["StreetName"] == street_address.name)
            & (data["StreetType"] == street_address.type)
        ]
        if street_data.empty:
            street_data = data[data["StreetName"] == street_address.name]
        return street_data[
            (street_data["SideCode"].isin([street_address.side_code, "A"]))
            & (street_data["HouseNumLo"] <= street_address.number)
            & (street_data["HouseNumHi"] >= street_address.number)
        ]


_db: Final = StreetDatabase(
    os.path.join(os.path.dirname(__file__), "data/neighborhood_data.tsv")
)

find = _db.find
