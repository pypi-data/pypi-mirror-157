# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .alfi_messages_pb2 import Coordinates as ALFIMessages_Coordinates
from .alfi_messages_pb2 import Field as ALFIMessages_Field

from .AlfiConstants import logger_name
from .TypedAlfiModel import TypedAlfiModel

from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class Coordinates(TypedAlfiModel):
    """
    Serialization/Deserialization of protobuff coordinates messages
    """

    def put_field(self, key: str, value: str) -> None:
        self.fields[key] = value

    def put_field_if_absent(self, key: str, value: str) -> None:
        if not self.get_field(key):
            self.put_field(key, value)

    def to_message(self) -> ALFIMessages_Coordinates:
        c = ALFIMessages_Coordinates()
        c.typed_alfi_model.CopyFrom(super().to_message())
        return c

    def field_to_message(self, field: str) -> ALFIMessages_Field:
        message = ALFIMessages_Field()
        message.element = self.get_or_default(field, "")
        return message

    @dataclass
    class Builder(TypedAlfiModel.Builder):
        fields: dict[str, str] = field(default_factory=dict)

        def get_field(self, key: str) -> Any:
            return self.fields.get(key)

        def put_field(self, key: str, value: str) -> None:
            self.fields[key] = value

        def put_field_if_absent(self, key: str, value: str) -> None:
            if not self.get_field(key):
                self.put_field(key, value)

        def with_field(self, key: str, value: str) -> Coordinates:
            self.put_field_if_absent(key, value)
            return self

        def build(self) -> Coordinates:
            return Coordinates(type=self.type, fields=self.fields)
