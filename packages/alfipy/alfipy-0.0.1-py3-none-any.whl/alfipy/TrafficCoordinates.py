# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .alfi_messages_pb2 import (
    TrafficCoordinates as ALFIMessages_TrafficCoordinates,
)

from .AlfiConstants import logger_name
from .Coordinates import Coordinates
from .TrafficType import TrafficType
from dataclasses import dataclass

logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class TrafficCoordinates(Coordinates):
    """
    A set of attributes describing a specific request to Gremlin.
    All attributes you include in this object are available to match on when creating an attack.

    An example TrafficCoordinates in English is: an HTTP POST to Slack for teamId=123

    Gremlin offers some integrations that will build these for you around I/O operations.  You may also build your own.

    To build your own, use the :ref:`TrafficCoordinates.Builder` and pass in a type and as many fields as you'd like.
    """

    def to_message(self) -> ALFIMessages_TrafficCoordinates:
        tc = ALFIMessages_TrafficCoordinates()
        return tc

    @dataclass
    class Builder(Coordinates.Builder):
        def build(self) -> TrafficCoordinates:
            return TrafficCoordinates(self.type, self.fields)

        def with_type(self, type: str) -> TrafficCoordinates.Builder:
            self.type = TrafficType(name=type, keys=None)
            return self
