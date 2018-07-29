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


class HouseNumRange:
  """
  The data file contains house number ranges defined by a side code, range
  low (inclusive) and range high (inclusive). The side code can be E for even,
  O for odd, A for all (no number range provided), or B for both. If the street
  number is withing [lo, hi] and is on the appropriate side of street, it
  matches.
  """
  def __init__(self, row):
    self._side_code = row["SideCode"]
    self._house_num_low = int(row["HouseNumLo"])
    self._house_num_hi = int(row["HouseNumHi"])

  def Matches(self, number):
    if ((self._side_code == 'E' and number % 2 == 1) or
        (self._side_code == 'O' and number % 2 == 0)):
      return False
    if self._side_code == 'A':
      return True
    return self._house_num_low <= number and number <= self._house_num_hi


def load_neighborhood_data(data_url):
  """
  Loads the data file into a list of lines. data_url can be local or on the web.
  If it's on the web, we use the Zapier-provided requests library to fetch it.
  Supports gzipped files.
  """
  if data_url.startswith("http"):
    response = requests.get(data_url)
    response.raise_for_status()
    if data_url.endswith(".gz"):
      text = zlib.decompress(response.text)
    else:
      text = response.text
    return text.splitlines()
  else:
    if data_url.endswith(".gz"):
      return gzip.open(data_url).readlines()
    else:
      return file(data_url).readlines()


def find_candidates(neighborhood_data, street_name, street_type):
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
  tier1, tier2, tier3 = [], [], []
  reader = csv.DictReader(neighborhood_data, delimiter='\t')
  for row in reader:
    row_street_name = row["StreetName"]
    if street_name == row_street_name:
      if street_type == row["StreetType"]:
        tier1.append((HouseNumRange(row), row["Neighborhood"]))
      else:
        tier2.append((HouseNumRange(row), row["Neighborhood"]))
    elif has_space and street_name.startswith(row_street_name):
      tier3.append((HouseNumRange(row), row["Neighborhood"]))
  return tier1 if tier1 else tier2 if tier2 else tier3


# Normalize the street type.
STREET_TYPES = {
  'st': 'st',
  'street': 'street',
  'dr': 'dr',
  'drive': 'drive',
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
  street_type = STREET_TYPES.get(tokens[-1].lower(), '')
  if street_type:
    tokens.pop()
  # Street is what's left.
  street_name = " ".join(tokens).lower()
  return (int(street_number), street_name, street_type)


def find_neighborhood(data_url, street_address):
  """
  Parses the address, loads the data, and finds the neighborhood(s) that match.
  """
  street_number, street_name, street_type = parse_street_address(street_address)
  neighborhood_data = load_neighborhood_data(data_url)
  candidates = find_candidates(neighborhood_data, street_name, street_type)
  matches = set()
  for house_num_range, neighborhood in candidates:
    if house_num_range.Matches(street_number):
      matches.add(neighborhood)
  if not matches:
    return None
  if len(matches) == 1:
    return matches.pop()
  return "Multiple matches: " + ", ".join(matches)


# Test on the command line.
# ./find_neighborhood.py neighborhood_data.tsv "123 Main St" 
if __name__ == '__main__':
  assert len(sys.argv) == 3
  print find_neighborhood(sys.argv[1], sys.argv[2])
else:
  # Execute in Zapier. Fix the variable and uncomment the return value.
  DATA_URL = "http://path/to/neighborhood_data.tsv.gz"
  INPUT_FIELD = "address"
  OUTPUT_FIELD = "neighborhood"
  # return {OUTPUT_FIELD: find_neighborhood(DATA_URL, input_data[INPUT_FIELD])}