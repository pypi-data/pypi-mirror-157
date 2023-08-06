# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from abc import ABCMeta, abstractmethod

from .alfi_messages_pb2 import TypedAlfiModel as ALFIMessages_TypedAlfiModel
from .alfi_messages_pb2 import Field as ALFIMessages_Field

from .AlfiConstants import logger_name
from .Exceptions import ALFIIllegalArgumentException
from .TypedAlfiModel import TypedAlfiModel

from dataclasses import dataclass, field
from typing import Generic, TypeVar

logger = logging.getLogger(f"{logger_name}.{__name__}")

F = TypeVar("F", bound="object")


@dataclass(frozen=True)
class TypeProvider(Generic[F], metaclass=ABCMeta):
    """
    Provider mapping for :ref:`TypedAlfiModel.Type` objects
    """

    query_keys: dict[str, TypedAlfiModel.Keys] = field(default_factory=dict)

    def register_type(self, name: str, keys: TypedAlfiModel.Keys) -> None:
        if self.query_keys.get(name, None):
            raise ALFIIllegalArgumentException(
                f"TrafficQuery name already exists: {name}"
            )
        self.query_keys[name] = keys

    def keys_for_type(self, name: str) -> dict:
        return self.query_keys.get(name, None)

    def get_fields(
        self, model_message: ALFIMessages_TypedAlfiModel
    ) -> dict[str, F]:
        if logger.getEffectiveLevel() is logging.DEBUG:
            logger.debug(f"Received model_message: {model_message}")
        # breakpoint()
        fields = {}
        for field_item in model_message.fields.items():
            logger.debug(field)
            fields[field_item[0]] = self.get_field_from_proto_entry(
                field_item[1]
            )
        return fields

    @abstractmethod
    def get_type(self, name: str) -> TypedAlfiModel.Type:
        raise NotImplementedError("Method needs to be defined in subclass")

    @abstractmethod
    def create_model(
        self, type: TypedAlfiModel.Type, fields: dict[str, object]
    ) -> TypedAlfiModel:
        raise NotImplementedError("Method needs to be defined in subclass")

    @abstractmethod
    def deserialize_model(self, message: object) -> TypedAlfiModel:
        raise NotImplementedError("Method needs to be defined in subclass")

    @abstractmethod
    def get_field_from_proto_entry(
        self, entry: dict[str, ALFIMessages_Field]
    ) -> object:
        raise NotImplementedError("Method needs to be defined in subclass")
