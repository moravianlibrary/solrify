from enum import Enum
from typing import Tuple, TypeVar

from pydantic import BaseModel


class MappingEnum(Enum):
    def __init__(self, value, map_to: str | None = None):
        self._map_to = map_to
        super().__init__(value)

    @property
    def map_to(self):
        return self._map_to

    @classmethod
    def map_from(cls, map_from: str):
        for member in cls:
            if member.map_to == map_from:
                return member
        raise ValueError(f"'{map_from}' not found in {cls.__name__}")


FieldType = TypeVar("F", bound=MappingEnum)

ValueType = (
    str,
    int,
    float,
    MappingEnum,
    Enum,
    Tuple[int, int],
    Tuple[str, str],
)


class Conjuction(Enum):
    AND = " AND "
    OR = " OR "


SolrEntity = TypeVar("SolrEntity", bound=BaseModel)
