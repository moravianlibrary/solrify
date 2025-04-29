import re
from enum import Enum
from typing import List, Tuple, TypeVar, Union

from pydantic import BaseModel


class MappingEnum(Enum):
    def __init__(self, alias: str | None = None):
        self.attr_name = re.sub(r"(?<!^)(?=[A-Z])", "_", self.name).lower()
        self.alias = alias or self.attr_name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"

    @classmethod
    def from_alias(cls, alias: str) -> "MappingEnum":
        for member in cls:
            if member.alias == alias:
                return member
        raise ValueError(
            f"No enum member in {cls.__name__} matches alias '{alias}'"
        )


FieldType = TypeVar("F", bound=MappingEnum)

type ValueType = Union[
    str,
    int,
    float,
    MappingEnum,
    Enum,
    Tuple[int, int],
    Tuple[str, str],
]


class Conjuction(Enum):
    AND = " AND "
    OR = " OR "


SolrEntity = TypeVar("SolrEntity", bound=BaseModel)
FacetResult = List[Tuple[str, int]]
