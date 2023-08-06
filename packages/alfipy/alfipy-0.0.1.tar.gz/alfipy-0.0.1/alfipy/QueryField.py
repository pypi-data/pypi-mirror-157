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
from .Exceptions import ALFIIllegalArgumentException
from .Field import Field

from dataclasses import dataclass, field
from typing import Any, ClassVar

logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class QueryField(Field, metaclass=ABCMeta):
    """
    Serialization/Deserialization of protocol buffer `QueryField` messages
    Subclass of :ref:`Field`
    """

    WILDCARD_STRING: ClassVar[str] = "*"

    @abstractmethod
    def to_json_string(self) -> str:
        raise NotImplementedError("Method needs to be implemented in subclass")

    @abstractmethod
    def matches(self, coordinates_field: str) -> bool:
        raise NotImplementedError("Method needs to implemented in subclass")

    @abstractmethod
    def is_wildcard(self) -> bool:
        raise NotImplementedError("Method needs to implemented in subclass")

    def from_map_object(self, o: Any):
        if type(o) == type(str):
            s = o
            if s == self.WILDCARD_STRING:
                return self.any()
            else:
                return self.specific(s)
        else:
            error_msg = "Could not parse field"
            logger.critical(error_msg)
            raise ALFIIllegalArgumentException(error_msg)

    @classmethod
    def specific(cls, s: str) -> QueryField:
        from .ExactField import ExactField

        return ExactField(data=s)

    @classmethod
    def any(cls) -> QueryField:
        from .WildcardField import WildcardField

        return WildcardField()

    @classmethod
    def from_message(cls, field_message: ALFIMessages_Field) -> QueryField:
        if not field_message.HasField("query"):
            error_msg = "Could not parse QueryField. Invalid protobuf message. Expected QueryField, received Impact"
            logger.critical(error_msg)
            raise ALFIIllegalArgumentException(error_msg)
        query_field = field_message.query
        if query_field.HasField("exact_field"):
            return cls.specific(query_field.exact_field.value)
        return cls.any()
