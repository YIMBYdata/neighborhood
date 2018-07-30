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

This script can be run in Zapier by fixing the code at the very bottom.
"""

import csv
import gzip
import scourgify
import string
import sys
import usaddress


def parse_street_address(street_address):
  """Parses a raw street address to (number, name, type)."""
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
          parsed["StreetName"].lower(),
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

  def find_neighborhood(self, street_address):
    street_address = street_address.strip()
    try:
      street_number, street_name, street_type = parse_street_address(street_address)
    except ValueError:
      return ""
    candidates = self._find_candidates(street_name, street_type)
    matches = set()
    for house_num_range in candidates:
      if house_num_range.Matches(street_number):
        matches.add(house_num_range.neighborhood)
    return ",".join(sorted(matches))
    
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

  def _find_candidates(self, street_name, street_type):
    """
    Given the loaded data and the input street name/type, finds HouseNumRanges
    that are relevant. We use some heuristics in the face of imperfect data.
    If the street name and type match the record, that's the best match. If only
    the street name matches, that second. If the input street name has a space in
    it and the record's street name is a prefix, that's third. The last of these
    corrects for something like "123 Main Suite 100" which will be parsed to
    123, Main Suite, ''.
    """
    street_type_map = self._parsed_data.get(street_name)
    if not street_type_map:
      return ()
    street_ranges = street_type_map.get(street_type)
    if not street_ranges:
      street_ranges = []
      for x in street_type_map.values():
        street_ranges.extend(x)
    return street_ranges


def find_neighborhood(data_filename, street_address):
  """Testable method."""
  db = StreetDatabase(data_filename)
  return db.find_neighborhood(street_address)


# Run on the command line.
# ./find_neighborhood.py neighborhood_data.tsv "123 Main St" 
if __name__ == '__main__':
  assert len(sys.argv) == 3
  print(find_neighborhood(sys.argv[1], sys.argv[2]))