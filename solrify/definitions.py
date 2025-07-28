import re
from enum import Enum
from typing import List, Tuple, TypeVar, Union

from pydantic import BaseModel


class MappingEnum(Enum):
    """
    An extended Enum class that adds aliasing
    and snake_case attribute name support.

    Each enum member automatically gains:
    - `attr_name`: a snake_case version of the name
      (e.g., 'SomeValue' → 'some_value')
    - `alias`: a custom alias if provided, or `attr_name` by default.

    Examples
    --------
    >>> class Field(MappingEnum):
    ...     Title = "title"
    ...     Author = "author"

    >>> Field.Title.attr_name
    'title'
    >>> Field.Title.alias
    'title'
    >>> Field.from_alias("author")
    <Field.Author: 'author'>

    Methods
    -------
    from_alias(alias: str) -> MappingEnum
        Retrieves enum member by its alias.

    Attributes
    ----------
    attr_name : str
        Snake_case version of the enum member name.

    alias : str
        Optional custom alias or derived attr_name.
    """

    def __init__(self, alias: str | None = None):
        self.attr_name = re.sub(r"(?<!^)(?=[A-Z])", "_", self.name).lower()
        self.alias = alias or self.attr_name

    def __str__(self) -> str:
        """Return the enum name as a string."""
        return self.name

    def __repr__(self) -> str:
        """Return a string representation of the enum with class context."""
        return f"{self.__class__.__name__}.{self.name}"

    @classmethod
    def from_alias(cls, alias: str) -> "MappingEnum":
        """
        Return the enum member corresponding to a given alias.

        Parameters
        ----------
        alias : str
            The alias to look up.

        Returns
        -------
        MappingEnum
            The enum member corresponding to the alias.

        Raises
        ------
        ValueError
            If no member matches the alias.
        """
        for member in cls:
            if member.alias == alias:
                return member
        raise ValueError(
            f"No enum member in {cls.__name__} matches alias '{alias}'"
        )


FieldType = TypeVar("F", bound=MappingEnum)
"""Type variable representing any subtype of MappingEnum."""


Wildcard = "*"
"""Constant representing a wildcard character used in queries."""


type ValueType = Union[
    str,
    int,
    float,
    MappingEnum,
    Enum,
    re.Pattern,
    Tuple[int, int],
    Tuple[str, str],
]
"""
A union type representing allowed search values.

Includes:
- Scalar types: `str`, `int`, `float`
- Enums: `MappingEnum`, `Enum`
- Patterns: `re.Pattern`
- Ranges: `(int, int)`, `(str, str)`
"""


class Conjuction(Enum):
    """
    Logical conjunction operators for combining query clauses.

    Members
    -------
    AND : str
        Logical AND represented as " AND ".
    OR : str
        Logical OR represented as " OR ".
    """

    AND = " AND "
    OR = " OR "


SolrEntity = TypeVar("SolrEntity", bound=BaseModel)
"""Type variable representing a Solr-bound Pydantic model."""

FacetResult = List[Tuple[str, int]]
"""Type alias representing a list of (facet_value, count) pairs."""
