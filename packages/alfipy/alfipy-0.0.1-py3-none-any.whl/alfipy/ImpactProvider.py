# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging
import secrets

from abc import ABCMeta, abstractmethod

from .alfi_messages_pb2 import Field as ALFIMessages_Field
from .alfi_messages_pb2 import Impact as ALFIMessages_Impact

from .AlfiConstants import AlfiConstants, logger_name
from .Exceptions import ALFIIllegalArgumentException
from .Impact import Impact
from .ImpactType import ImpactType
from .TypeProvider import TypeProvider

from dataclasses import dataclass


logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class ImpactProvider(TypeProvider):
    """
    Encapsulation of :ref:`Impact` and :ref:`ImpactType`
    """

    def __post_init__(self):
        self.register_type(
            AlfiConstants.TI_GENERAL_NAME, AlfiConstants.TI_KEYS_GENERAL
        )

    def get_type(self, name: str) -> ImpactType:
        return ImpactType(name, self.keys_for_type(name))

    def create_model(
        self, type: ImpactType, fields: dict[str, object]
    ) -> Impact:
        return Impact(type, fields)

    def deserialize_model(self, message: ALFIMessages_Impact) -> Impact:
        typed_message = message.typed_alfi_model
        return self.create_model(
            self.get_type(typed_message.type), self.get_fields(typed_message)
        )

    def get_field_from_proto_entry(
        self, entry: dict[str, ALFIMessages_Field]
    ) -> object:
        if not entry or not entry.HasField("impact"):
            raise ALFIIllegalArgumentException(
                "Invalid Impact protobuf message. Fields of wrong type."
            )
        impact = entry.impact
        if impact.HasField("null_value"):
            return None
        elif impact.HasField("bool_value"):
            return impact.bool_value
        elif impact.HasField("list_value"):
            return impact.list_value
        elif impact.HasField("number_value"):
            return impact.number_value
        elif impact.HasField("string_value"):
            return impact.string_value
        elif impact.HasField("struct_value"):
            return impact.struct_value
        else:
            raise ALFIIllegalArgumentException(
                "Impact field not a valid type."
            )

    def new_builder(self) -> Impact.Builder:
        return Impact.Builder()
