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
import sys
import zlib


# Normalize the street type.
_STREET_TYPES = {
  'st': 'st',
  'street': 'st',
  'dr': 'dr',
  'drive': 'dr',
  'blvd': 'blvd',
  'ave': 'ave',
  'avenue': 'ave',
  'way': 'way',
  'terrace': 'ter',
  'ter': 'ter',
  'park': 'park'
}


def parse_street_address(street_address):
  """Parses a raw street address to (number, name, type)."""
  tokens = street_address.split(" ")
  # Consume and parse the street number.
  street_number = tokens.pop(0).lower()
  if any(street_number.endswith(x) for x in "abc"):
    street_number = street_number[:-1]
  # Strip extra junk off the end.
  if len(tokens) > 1 and len(tokens[-1]) == 1:
    tokens.pop()
  if len(tokens) > 1 and any(c in '0123456789' for c in tokens[-1]):
    tokens.pop()
  # Parse the street type
  street_type = _STREET_TYPES.get(tokens[-1].lower(), '')
  if street_type:
    tokens.pop()
  # Street is what's left.
  street_name = " ".join(tokens).lower()
  return (int(street_number), street_name, street_type)


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


class StreetRecord(object):

  def __init__(self, street_name, street_type):
    self.street_name = street_name
    self.street_type = street_type
    self.house_num_ranges = []


class StreetDatabase(object):

  def __init__(self, data_filename):
    self._records = self._parse(self._read(data_filename))

  def find_neighborhood(self, street_address):
    street_address = street_address.strip()
    if not street_address:
      return None
    street_number, street_name, street_type = parse_street_address(street_address)
    candidates = self._find_candidates(street_name, street_type)
    matches = set()
    for house_num_range in candidates:
      if house_num_range.Matches(street_number):
        matches.add(house_num_range.neighborhood)
    if not matches:
      return None
    if len(matches) == 1:
      return matches.pop()
    return "Multiple matches: " + ", ".join(matches)
    
  def _read(self, data_filename):
    if data_filename.endswith(".gz"):
      return gzip.open(data_filename).readlines()
    else:
      return file(data_filename).readlines()

  def _parse(self, data):
    parsed_data = {}
    reader = csv.DictReader(data, delimiter='\t')
    for row in reader:
      key = (row["StreetName"], row["StreetType"])
      record = parsed_data.get(key)
      if not record:
        record = parsed_data[key] = StreetRecord(*key)
      record.house_num_ranges.append(HouseNumRange(
          row["SideCode"], int(row["HouseNumLo"]), int(row["HouseNumHi"]),
          row["District"], row["Neighborhood"]))
    return parsed_data.values()

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
    has_space = street_name.find(" ")
    tier2, tier3 = [], []
    for record in self._records:
      if street_name == record.street_name:
        if street_type == record.street_type:
          return record.house_num_ranges  # Exact match
        else:
          tier2.extend(record.house_num_ranges)
      elif has_space and street_name.startswith(record.street_name):
        tier3.extend(record.house_num_ranges)
    return tier2 if tier2 else tier3


def find_neighborhood(data_filename, street_address):
  """Testable method."""
  db = StreetDatabase(data_filename)
  return db.find_neighborhood(street_address)


# Run on the command line.
# ./find_neighborhood.py neighborhood_data.tsv "123 Main St" 
if __name__ == '__main__':
  assert len(sys.argv) == 3
  print find_neighborhood(sys.argv[1], sys.argv[2])