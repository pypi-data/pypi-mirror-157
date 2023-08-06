# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .alfi_messages_pb2 import (
    TrafficQueryAndImpact as ALFIMessages_TrafficQueryAndImpact,
)

from .AlfiConstants import logger_name
from .Impact import Impact
from .TrafficQuery import TrafficQuery

from dataclasses import dataclass


logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass
class TrafficQueryAndImpact:
    """
    Serialization/Deserialization interface for protocol buffer messages
    """

    query: TrafficQuery
    impact: Impact

    def to_message(self) -> ALFIMessages_TrafficQueryAndImpact:
        tcai = ALFIMessages_TrafficQueryAndImpact()
        tcai.impact.CopyFrom(self.impact)
        tcai.traffic_query.CopyFrom(self.query)
        return tcai

    def __eq__(self, other):
        if self is other:
            return True
        if other is None or self.__class__ != other.__class__:
            return False
        return self.query == other.query and self.impact == other.impact

    def __hash__(self):
        return hash((str(self.query), str(self.impact)))
