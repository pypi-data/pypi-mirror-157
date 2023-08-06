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
from .ImpactProvider import ImpactProvider
from .TrafficQueryAndImpact import TrafficQueryAndImpact
from .TrafficQueryProvider import TrafficQueryProvider

from dataclasses import dataclass, field


logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass
class TrafficAndImpactProvider:
    """
    Provides mapping between :ref:`TrafficCoordinates` and :ref:`ImpactProvider`
    """

    traffic_query_provider: TrafficQueryProvider = field(
        default_factory=TrafficQueryProvider
    )
    impact_provider: ImpactProvider = field(default_factory=ImpactProvider)

    def __post_init__(self):
        self.traffic_query_provider = TrafficQueryProvider()
        self.impact_provider = ImpactProvider()

    def deserialize_model(
        self, traffic_message: ALFIMessages_TrafficQueryAndImpact
    ) -> TrafficQueryAndImpact:
        return TrafficQueryAndImpact(
            self.traffic_query_provider.deserialize_model(
                traffic_message.traffic_query
            ),
            self.impact_provider.deserialize_model(traffic_message.impact),
        )
