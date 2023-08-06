# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

from .alfi_messages_pb2 import Field as ALFIMessages_Field

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Field(metaclass=ABCMeta):
    """
    Serialization/Deserialization of protocol buffer messages for the `Field` attribute
    """

    @abstractmethod
    def to_json_string(self) -> str:
        raise NotImplementedError("Method needs to be implemented in subclass")

    @abstractmethod
    def to_message(self) -> ALFIMessages_Field:
        raise NotImplementedError("Method needs to be implemented in subclass")
