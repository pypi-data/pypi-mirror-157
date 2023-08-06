# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

from .alfi_messages_pb2 import Field as ALFIMessages_Field

from .QueryField import QueryField

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExactField(QueryField):
    """
    Protocol buffer serializer/deserialzer for the `ExactField` message, a sub-type of :ref:`QueryField`
    """

    data: str = field(default="")

    def to_json_string(self):
        return self.data

    def matches(self, coordinates_filed: str) -> bool:
        return self.data == coordinates_filed

    def is_wildcard(self) -> bool:
        return False

    def to_string(self) -> str:
        return f"ExactField{{data={self.data}}}"

    def to_message(self) -> ALFIMessages_Field:
        efm = ALFIMessages_Field()
        efm.query.exact_field.value = self.data
        return efm

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if other is None or self.__class__ != other.__class__:
            return False
        if self.data == other.data:
            return True

    def __str__(self) -> str:
        return f"ExactField(data={self.data})"
