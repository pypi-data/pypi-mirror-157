# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .alfi_messages_pb2 import Field as ALFIMessages_Field
from .alfi_messages_pb2 import Impact as ALFIMessages_Impact

from .AlfiConstants import logger_name
from .Exceptions import ALFIRuntimeException
from .TypedAlfiModel import TypedAlfiModel

from dataclasses import dataclass


logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class Impact(TypedAlfiModel):
    """
    Serialization/Deserialization of protocol buffer messages for `impact` types
    """

    def get_or_default(
        self, key: str, fallback: TypedAlfiModel.Type
    ) -> TypedAlfiModel.Type:
        found = super().get_or_default(key, fallback)
        try:
            return found
        except Exception as e:
            error_msg = (
                f"Field with key {key} is not an instance of {type(fallback)}"
            )
            logger.critical(error_msg)
            raise ALFIRuntimeException(error_msg) from e

    def get_impact_parameter(self, key: str):
        return self.fields.get(key)

    def to_message(self) -> ALFIMessages_Impact:
        impact = ALFIMessages_Impact()
        # populate impact....
        return impact

    def field_to_message(self, field: object) -> ALFIMessages_Field:
        pass

    @dataclass
    class Builder(TypedAlfiModel.Builder):
        def build(self) -> Impact:
            return Impact(self.type, self.fields)
