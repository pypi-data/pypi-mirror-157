# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .alfi_messages_pb2 import Field as ALFIMessages_Field

from .AlfiConstants import logger_name
from .QueryField import QueryField

from dataclasses import dataclass
from typing import Any, Optional


logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class WildcardField(QueryField):
    """
    Protocol buffer serializer/deserialzer for the `WildcardField` message, a sub-type of :ref:`QueryField`
    """

    def to_json_string(self):
        return self.WILDCARD_STRING

    def matches(self, coordinates_filed: str) -> bool:
        return True

    def is_wildcard(self) -> bool:
        return True

    def to_message(self) -> ALFIMessages_Field:
        wcf = ALFIMessages_Field()
        wcf.query.wildcard_field.SetInParent()
        return wcf

    def __eq__(self, other: Optional[Any] = None) -> bool:
        if self is other:
            return True
        if other is None or self.__class__ != other.__class__:
            return False
        return True

    def __str__(self):
        return "WildcardField()"
