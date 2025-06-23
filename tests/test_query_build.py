import unittest
from enum import Enum

from solrify import Conjuction, F, G, MappingEnum, SearchQuery


class TestField(MappingEnum):
    Name = "name"
    Year = "publication_year"
    OldYear = "old_publication_year"
    Status = "status"


class TestEnum(Enum):
    Published = "published"
    Draft = "draft"


class TestSearchQuery(unittest.TestCase):

    def test_string_query(self):
        q = F(TestField.Name, "Alice")
        self.assertEqual(str(q), 'name:"Alice"')

    def test_integer_query(self):
        q = F(TestField.Year, 2020)
        self.assertEqual(str(q), "publication_year:2020")

    def test_enum_query(self):
        q = F(TestField.Status, TestEnum.Published)
        self.assertEqual(str(q), 'status:"published"')

    def test_mapping_enum_query(self):
        q = F(TestField.Name, TestField.OldYear)
        self.assertEqual(str(q), 'name:"old_publication_year"')

    def test_regex_query(self):
        import re

        q = F(TestField.Name, re.compile(r"^Alice"))
        self.assertEqual(str(q), "name:/^Alice/")

    def test_wildcard_query(self):
        q = F(TestField.Name, "*")
        self.assertEqual(str(q), "name:*")

    def test_none_value_query(self):
        q = F(TestField.Name, None)
        self.assertEqual(str(q), "")

    def test_range_query(self):
        q = F(TestField.Year, (2000, 2020))
        self.assertEqual(str(q), "publication_year:[2000 TO 2020]")

    def test_list_query(self):
        q = F(TestField.Name, ["Alice", "Bob"])
        self.assertEqual(str(q), 'name:("Alice" OR "Bob")')

    def test_list_query_with_and(self):
        q = F(TestField.Name, ["Alice", "Bob"], list_conj=Conjuction.AND)
        self.assertEqual(str(q), 'name:("Alice" AND "Bob")')

    def test_negation(self):
        q = ~F(TestField.Name, "Alice")
        self.assertEqual(str(q), '-name:"Alice"')

    def test_and_conjunction(self):
        q1 = F(TestField.Name, "Alice")
        q2 = F(TestField.Year, 2020)
        combined = q1 & q2
        self.assertEqual(
            str(combined), 'name:"Alice" AND publication_year:2020'
        )

    def test_or_conjunction(self):
        q1 = F(TestField.Name, "Alice")
        q2 = F(TestField.Year, 2020)
        combined = q1 | q2
        self.assertEqual(
            str(combined), 'name:"Alice" OR publication_year:2020'
        )

    def test_three_way_conjunction(self):
        q1 = F(TestField.Name, "Alice")
        q2 = F(TestField.Year, 2020)
        q3 = F(TestField.Status, TestEnum.Published)
        combined = q1 & (q2 & q3)
        self.assertEqual(
            str(combined),
            'name:"Alice" AND publication_year:2020 AND status:"published"',
        )

    def test_group_query(self):
        q = G(F(TestField.Name, "Alice"))
        self.assertEqual(str(q), '(name:"Alice")')

    def test_combined_group(self):
        q1 = G(F(TestField.Name, "Alice"))
        q2 = G(F(TestField.Year, 2020))
        combined = G(q1 & q2)
        self.assertEqual(
            str(combined), '((name:"Alice") AND (publication_year:2020))'
        )

    def test_combined_with_empty_query(self):
        q1 = SearchQuery()
        q2 = F(TestField.Name, "Alice")
        combined = q1 & q2
        self.assertEqual(str(combined), 'name:"Alice"')
