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
import scourgify
import string
import sys
import usaddress


def parse_street_address(street_address):
  """Parses a raw street address to (number, name, type)."""
  if not street_address:
    raise ValueError("Empty address")
  try:
    normalized = scourgify.normalize_address_record(street_address)
  except scourgify.exceptions.UnParseableAddressError as e:
    raise ValueError(e)
  parsed, _ = usaddress.tag(normalized["address_line_1"])
  street_number = parsed.get("AddressNumber")
  if not street_number:
    raise ValueError(str(parsed))
  street_number = street_number.rstrip(string.ascii_letters)
  return (int(street_number),
          parsed.get("StreetName", "").lower(),
          parsed.get("StreetNamePostType", "").lower())


class HouseNumRange(object):
  """
  The data file contains house number ranges defined by a side code, range
  low (inclusive) and range high (inclusive). The side code can be E for even,
  O for odd, A for all (no number range provided), or B for both. If the street
  number is withing [lo, hi] and is on the appropriate side of street, it
  matches.
  """
  def __init__(
      self, side_code, house_num_low, house_num_high, district, neighborhood):
    self._side_code = side_code
    self._house_num_low = house_num_low
    self._house_num_high = house_num_high
    self.district = district
    self.neighborhood = neighborhood

  def Matches(self, number):
    if ((self._side_code == 'E' and number % 2 == 1) or
        (self._side_code == 'O' and number % 2 == 0)):
      return False
    if self._side_code == 'A':
      return True
    return self._house_num_low <= number and number <= self._house_num_high


class StreetDatabase(object):

  def __init__(self, data_filename):
    self._parsed_data = self._parse(self._read(data_filename))

  def find_district(self, street_address):
    matches = self._find_matches(street_address)
    return ",".join(sorted(set([m.district for m in matches])))

  def find_neighborhood(self, street_address):
    matches = self._find_matches(street_address)
    return ",".join(sorted(set([m.neighborhood for m in matches])))
    
  def _read(self, data_filename):
    open_file = gzip.open if data_filename.endswith(".gz") else open
    with open_file(data_filename, mode="rt") as f:
      return f.readlines()

  def _parse(self, data):
    parsed_data = {}
    reader = csv.DictReader(data, delimiter='\t')
    for row in reader:
      ranges = parsed_data.setdefault(row["StreetName"], {}).setdefault(row["StreetType"], [])
      ranges.append(HouseNumRange(
          row["SideCode"], int(row["HouseNumLo"]), int(row["HouseNumHi"]),
          row["District"], row["Neighborhood"]))
    return parsed_data

  def _find_matches(self, street_address):
    """
    Given the loaded data and the input address, finds HouseNumRanges
    that match. If the street_type doesn't match for a given street, we'll fall
    back to all street types for that street.
    """
    try:
      street_number, street_name, street_type = parse_street_address(
          street_address)
    except ValueError:
      return ()
    street_data = self._parsed_data.get(street_name, {})
    ranges = street_data.get(street_type)
    if not ranges:
      ranges = itertools.chain(*street_data.values())
    return [r for r in ranges if r.Matches(street_number)]


def find_neighborhood(data_filename, street_address):
  """Testable method."""
  db = StreetDatabase(data_filename)
  return db.find_neighborhood(street_address)


# Run on the command line.
# ./app/find_neighborhood.py data/neighborhood_data.tsv "123 Main St" 
if __name__ == '__main__':
  assert len(sys.argv) == 3
  print(find_neighborhood(sys.argv[1], sys.argv[2]))