from enum import Enum

from .custom_types import Conjuction, FieldType, MappingEnum, ValueType


class SearchQuery:
    def __init__(self):
        self._neg: bool = False
        self._conj: Conjuction | None = None
        self._prev: SearchQuery | None = None

    def __and__(self, other: "SearchQuery"):
        return self._combine(other, Conjuction.AND)

    def __or__(self, other: "SearchQuery"):
        return self._combine(other, Conjuction.OR)

    def __invert__(self):
        self._neg = not self._neg
        return self

    def _combine(self, other: "SearchQuery", conj: Conjuction):
        last_node = other
        while last_node._prev:
            last_node = last_node._prev
        last_node._prev = self
        last_node._conj = conj
        return other

    def _build(self, result: str) -> str:
        if self._neg:
            result = f"-{result}"
        if self._prev:
            result = f"{self._prev}{self._conj.value}{result}"
        return result


class SearchQueryField(SearchQuery):
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

    def __str__(self) -> str:
        if self._value is None:
            return ""

        def _value_to_str(value: ValueType) -> str:
            if isinstance(value, MappingEnum):
                value = f'"{value.map_to}"'
            elif isinstance(value, Enum):
                value = f'"{value.value}"'
            elif isinstance(value, str):
                return f'"{value}"'
            return str(value)

        if isinstance(self._value, tuple):
            value1 = _value_to_str(self._value[0])
            value2 = _value_to_str(self._value[1])

            return self._build(f"{self._field.map_to}:[{value1} TO {value2}]")

        if isinstance(self._value, list):
            joined_values = self._list_conj.value.join(
                _value_to_str(v) for v in self._value
            )
            return self._build(f"{self._field.map_to}:({joined_values})")

        return self._build(
            f"{self._field.map_to}:{_value_to_str(self._value)}"
        )


class SearchQueryGroup(SearchQuery):
    def __init__(self, query: SearchQueryField):
        super().__init__()
        self._query = query

    def __str__(self) -> str:
        return self._build(f"({str(self._query)})")
