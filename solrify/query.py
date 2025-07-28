import re
from enum import Enum

from .definitions import (
    Conjuction,
    FieldType,
    MappingEnum,
    ValueType,
    Wildcard,
)


class SearchQuery:
    """
    Base class for representing a composable search query.

    Supports logical composition of queries using AND, OR, and NOT operators,
    and provides a foundation for concrete search query implementations.

    Attributes
    ----------
    _neg : bool
        Indicates whether the query is negated.
    _conj : Conjuction or None
        Logical operator connecting this query to the previous one.
    _prev : SearchQuery or None
        Previous query in a chain (used for combining queries).

    Methods
    -------
    _transfer_state_from(query)
        Transfers the logical state from another query.
    _copy()
        Returns a copy of the query.
    _combine_with(other, conj)
        Combines this query with another using the specified conjunction.
    __and__(other)
        Overloads '&' to combine queries with AND.
    __or__(other)
        Overloads '|' to combine queries with OR.
    __invert__()
        Overloads '~' to negate the query.
    __str__()
        Returns the string representation of the query.
    _format_query(result)
        Formats the query string based on logical context.
    """

    def __init__(self):
        self._neg: bool = False
        self._conj: Conjuction | None = None
        self._prev: SearchQuery | None = None

    def _transfer_state_from(self, query: "SearchQuery") -> "SearchQuery":
        self._neg = query._neg
        self._conj = query._conj
        self._prev = query._prev
        return self

    def _copy(self) -> "SearchQuery":
        return SearchQuery()._transfer_state_from(self)

    def _combine_with(self, other: "SearchQuery", conj: Conjuction):
        self_copy = self._copy()
        other_copy = other._copy()

        # Link the two queries
        last_node = other_copy
        while last_node._prev:
            last_node = last_node._prev
        last_node._prev = self_copy
        last_node._conj = conj

        return other_copy

    def __and__(self, other: "SearchQuery"):
        return self._combine_with(other, Conjuction.AND)

    def __or__(self, other: "SearchQuery"):
        return self._combine_with(other, Conjuction.OR)

    def __invert__(self):
        neg_query = self._copy()
        neg_query._neg = not self._neg
        return neg_query

    def __str__(self) -> str:
        return ""

    def _format_query(self, result: str) -> str:
        if self._neg:
            result = f"-{result}"
        prev = str(self._prev) if self._prev else ""
        if prev:
            result = f"{prev}{self._conj.value}{result}"
        return result


class SearchQueryField(SearchQuery):
    """
    Represents a single field-based search query.

    Parameters
    ----------
    field : FieldType
        Field to search against.
    value : ValueType
        Value to search for. Can be scalar, range, regex, or list.
    list_conj : Conjuction, default=Conjuction.OR
        Conjunction to use when `value` is a list.

    Methods
    -------
    __str__()
        Converts the query to a Solr-style query string.
    """

    def __init__(
        self,
        field: FieldType,
        value: ValueType,
        list_conj: Conjuction = Conjuction.OR,
    ):
        super().__init__()
        self._field = field
        self._value = value
        self._list_conj = list_conj

    def _copy(self) -> "SearchQueryField":
        return SearchQueryField(
            self._field, self._value, self._list_conj
        )._transfer_state_from(self)

    def __str__(self) -> str:
        if self._value is None:
            return ""

        def _value_to_str(value: ValueType) -> str:
            if isinstance(value, MappingEnum):
                return f'"{value.alias}"'
            if isinstance(value, Enum):
                return f'"{value.value}"'
            if isinstance(value, re.Pattern):
                return f"/{value.pattern}/"
            if isinstance(value, str):
                return f"{Wildcard}" if value == Wildcard else f'"{value}"'
            return str(value)

        if isinstance(self._value, tuple):
            value1 = _value_to_str(self._value[0])
            value2 = _value_to_str(self._value[1])

            return self._format_query(
                f"{self._field.alias}:[{value1} TO {value2}]"
            )

        if isinstance(self._value, list):
            joined_values = self._list_conj.value.join(
                _value_to_str(v) for v in self._value
            )
            return self._format_query(f"{self._field.alias}:({joined_values})")

        return self._format_query(
            f"{self._field.alias}:{_value_to_str(self._value)}"
        )


class SearchQueryGroup(SearchQuery):
    """
    Represents a grouped search query (wrapped in parentheses).

    Useful for explicitly grouping parts of a compound query.

    Parameters
    ----------
    query : SearchQueryField
        The query to wrap in a group.

    Methods
    -------
    __str__()
        Returns the grouped string representation.
    """

    def __init__(self, query: SearchQueryField):
        super().__init__()
        self._query = query

    def _copy(self) -> "SearchQueryGroup":
        return SearchQueryGroup(self._query._copy())._transfer_state_from(self)

    def __str__(self) -> str:
        return self._format_query(f"({str(self._query)})")
