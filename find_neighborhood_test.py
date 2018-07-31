#! /usr/bin/env python

import find_neighborhood
import unittest


class StreetParseTest(unittest.TestCase):

  def assertStreetParsesTo(
      self, street_address, street_number, street_name, street_type):
    self.assertEqual(
      find_neighborhood.parse_street_address(street_address),
      (street_number, street_name, street_type))

  def test_basic_parse(self):
    self.assertStreetParsesTo("123 Main St", 123, "main", "st")

  def test_apt_number_parse(self):
    self.assertStreetParsesTo("123 Main St #101", 123, "main", "st")

  def test_street_type_normalization(self):
    self.assertStreetParsesTo("123 Main Street", 123, "main", "st")

  def test_street_type_normalization(self):
    self.assertStreetParsesTo("123 Main Street", 123, "main", "st")

  def test_apt_number_parse_with_suite(self):
    self.assertStreetParsesTo("123 Main St Suite 101", 123, "main", "st")

  def test_street_type_missing(self):
    self.assertStreetParsesTo("123 Main", 123, "main", "")

  def test_number_with_letter_suffix(self):
    self.assertStreetParsesTo("123b Main St", 123, "main", "st")
    self.assertStreetParsesTo("123 Main St b", 123, "main", "st")

  def test_number_value_error(self):
    with self.assertRaises(ValueError):
      find_neighborhood.parse_street_address("b123 Main St")


class FindNeighborhoodTest(unittest.TestCase):

  def setUp(self):
    self._db = find_neighborhood.StreetDatabase("data/neighborhood_data.tsv.gz")

  def assertResults(self, street_address, district, neighborhood):
    self.assertEqual(
      self._db.find_district(street_address),
      district)
    self.assertEqual(
      self._db.find_neighborhood(street_address),
      neighborhood)

  def test_street_match(self):
    self.assertResults("123 Main St", "6", "Financial District/South Beach")  

  def test_full_address(self):
    self.assertResults("123 Main St, San Francisco, CA 94105",
                       "6", "Financial District/South Beach") 

  def test_street_type_missing(self):
    self.assertResults("123 Main", "6", "Financial District/South Beach")

  def test_junk_suffix(self):
    self.assertResults("123 Main Suite 100",
                       "6", "Financial District/South Beach")

  def test_random_suffix(self):
    self.assertResults("123 Main Suite 100",
                       "6", "Financial District/South Beach")

  def test_unparseable_address(self):
    self.assertResults("1 10th", "", "")
    self.assertResults("1 10th Apt 3", "", "")
    self.assertResults("b123 Main St", "", "")

  def test_ambiguous_address(self):
    self.assertResults(
        "10 10th Apt 3", "2,6",
        "Inner Richmond,South of Market")

  def test_no_match(self):
    self.assertResults("1 asdf123 st", "", "")
  
  def test_empty_input(self):
    self.assertResults(" ", "", "")


if __name__ == '__main__':
    unittest.main()
