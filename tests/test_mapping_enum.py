import unittest

from solrify import MappingEnum


class TestField(MappingEnum):
    Name = "name"
    Year = "publication_year"
    OldYear = "old_publication_year"
    Status = "status"


class TestSearchQuery(unittest.TestCase):

    def test_enum_properties(self):
        self.assertEqual(TestField.OldYear.name, "OldYear")
        self.assertEqual(TestField.OldYear.attr_name, "old_year")
        self.assertEqual(TestField.OldYear.alias, "old_publication_year")

    def test_enum_from_alias(self):
        self.assertEqual(
            TestField.from_alias("old_publication_year"), TestField.OldYear
        )
        with self.assertRaises(ValueError):
            TestField.from_alias("non_existent_alias")

    def test_enum_str(self):
        self.assertEqual(str(TestField.OldYear), "OldYear")
        self.assertEqual(repr(TestField.OldYear), "TestField.OldYear")
