# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from abc import ABCMeta, abstractmethod

from .alfi_messages_pb2 import Field as ALFIMessages_Field

from .AlfiConstants import logger_name
from .Coordinates import Coordinates
from .TypedAlfiModel import TypedAlfiModel
from .QueryField import QueryField

from dataclasses import dataclass, InitVar
from typing import Any, ClassVar, Optional


logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class QueryModel(TypedAlfiModel, metaclass=ABCMeta):
    """
    Abstract implementation of TypedAlfiModel for deserialized QueryModel messages
    """

    KEY_PERCENTAGE_TO_IMPACT: ClassVar[str] = "percentage_to_impact"

    percentage_to_impact: float = 0.0

    def matches(self, coordinates: Coordinates) -> bool:
        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.debug(
                f"coordinates.type == {coordinates.type} ;; query.type == {self.type}"
            )
        if coordinates.type == self.type:
            all_match = True
            for field in self.fields.keys():
                if not coordinates.fields.get(field) or (
                    not self.fields.get(field).is_wildcard()
                    and coordinates.fields.get(field)
                    != self.fields.get(field).data
                ):
                    all_match = False
            return all_match
        else:
            return False

    def to_string(self) -> str:
        pass

    def field_to_message(self, field: QueryField) -> ALFIMessages_Field:
        return field.to_message()

    def __eq__(self, other: Optional[Any] = None):
        if self is other:
            return True
        if other is None or self.__class__ != other.__class__:
            return False
        if not super().__eq__(other):
            return False
        return self.percentage_to_impact == other.percentage_to_impact

    def __hash__(self):
        return hash((super().__hash__(), str(self.percentage_to_impact)))

    @dataclass
    class Builder(TypedAlfiModel.Builder):
        percentage_to_impact: float = 0.0
        provider: InitVar = None

        def __post_init__(self, provider) -> None:
            self._provider = provider

        def with_percent_to_impact(
            self, percent_to_impact: int
        ) -> QueryModel.Builder:
            self.percentage_to_impact = percent_to_impact
            return self

        def with_exact_field(self, key: str, value: str) -> QueryModel.Builder:
            self.fields[key] = QueryField.specific(value)
            return self

        def with_any_field(self, key: str) -> QueryModel.Builder:
            self.fields[key] = QueryField.any()
            return self

        def build(self) -> QueryModel:
            return QueryModel(
                type=self.type,
                fields=self.fields,
                percentage_to_impact=self.percentage_to_impact,
            )
