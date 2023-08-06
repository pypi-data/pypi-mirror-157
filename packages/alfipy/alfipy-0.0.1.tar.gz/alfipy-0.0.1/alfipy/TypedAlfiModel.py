# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations


from .alfi_messages_pb2 import TypedAlfiModel as ALFIMessages_TypedAlfiModel

from .Exceptions import ALFIIllegalStateException

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar

F = TypeVar("F", bound="object")
K = TypeVar("K", bound="TypedAlfiModel.Keys")
T = TypeVar("T", bound="TypedAlfiModel.Type")


@dataclass(frozen=True)
class TypedAlfiModel(Generic[F, T], metaclass=ABCMeta):
    """
    The heart of the protocol buffer to python object serialization/deserialization workflow
    """

    type: T = field(default_factory=str)
    fields: dict[str, F] = field(default_factory=dict)

    def get_or_default(self, key: str, fallback: Any) -> Any:
        return self.fields.get(key, fallback)

    def get_field(self, key: str) -> Any:
        return self.fields.get(key)

    def get_fields(self) -> dict:
        return self.fields

    def to_message(self) -> ALFIMessages_TypedAlfiModel:
        t = ALFIMessages_TypedAlfiModel()
        t.type = self.type
        for _field in self.get_fields().keys():
            t.fields.get_or_create(_field)
            t.fields[_field].CopyFrom(self.field_to_message(_field))
        return t

    @staticmethod
    @abstractmethod
    def field_to_message(field: str):
        raise NotImplementedError("Method needs to implemented in subclass")

    def populate_proto_builder(
        self, message: ALFIMessages_TypedAlfiModel
    ) -> ALFIMessages_TypedAlfiModel:
        message.type = self.type

    def __eq__(self, other: Optional[Any] = None) -> bool:
        if self is other:
            return True
        if other is None or self.__class__ != other.__class__:
            return False
        return self.type == other.type and self.fields == other.fields

    def __hash__(self) -> int:
        return hash((str(self.type.keys), str(self.fields.keys())))

    @dataclass
    class Builder:
        type: T = field(default_factory=str)
        fields: dict[str, F] = field(default_factory={})

        def with_type(self, type: str) -> TypedAlfiModel.Builder:
            # self.type = TypedAlfiModel.Type(name=type, keys=None)
            self.type = type
            return self

        def with_field(self, key: str, value: F) -> TypedAlfiModel.Builder:
            self.fields[key] = value
            return self

        def build(self) -> TypedAlfiModel:
            return TypedAlfiModel(type=self.type, fields=self.fields)

    @dataclass(frozen=True)
    class Type(Generic[K]):
        name: str
        keys: K

        def __eq__(self, other: Optional[object] = None) -> bool:
            if self == other:
                return True
            if other is None or self.__class__ != other.__class__:
                return False
            return self.name == other.name

        def __hash__(self) -> int:
            return hash((str(self.name), str(self.keys)))

    @dataclass(frozen=True)
    class Keys:
        all_keys: list[str] = field(default_factory=list)
        required_keys: list[str] = field(default_factory=list)

        def get_optional_keys(self) -> list[str]:
            return list(set(self.all_keys) - set(self.required_keys))

        @classmethod
        def empty_keys(cls) -> K:
            return cls()

        def optional(self, name: str) -> K:
            self.all_keys.append(name)
            return self

        def required(self, name: str) -> K:
            self.optional(name)
            self.required_keys.append(name)
            return self

        def validate(self, map: dict[str, Any]) -> None:
            for key in self.required_keys:
                if not map.get(key, None):
                    raise ALFIIllegalStateException(f"{key} is required")

        def __eq__(self, other: Optional[object] = None) -> bool:
            if self == other:
                return True
            if other is None or self.__class__ != other.__class__:
                return False
            return (
                self.all_keys == other.all_keys
                and self.required_keys == other.required_keys
            )

        def __hash__(self) -> int:
            return hash((str(self.all_keys), str(self.required_keys)))
