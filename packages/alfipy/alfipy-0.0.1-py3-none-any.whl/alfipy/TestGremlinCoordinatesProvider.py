# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .AlfiConstants import logger_name
from .ApplicationCoordinates import ApplicationCoordinates
from .GremlinCoordinatesProvider import GremlinCoordinatesProvider
from .TrafficCoordinates import TrafficCoordinates

logger = logging.getLogger(f"{logger_name}.{__name__}")


class TestGremlinCoordinatesProvider(GremlinCoordinatesProvider):
    """
    Implementation of :ref:`GremlinCoordinatesProvider` used for testing purposes only
    """

    def initialize_coordinates(self):
        return (
            ApplicationCoordinates.Builder()
            .with_type("test")
            .with_field("type", "foo")
            .build()
        )

    def extend_each_traffic_coordinates(
        self, incoming_coordinates: TrafficCoordinates
    ) -> TrafficCoordinates:
        if logger.getEffectiveLevel() is logging.DEBUG:
            logger.debug(
                f"Adding context to TrafficCoordinates {incoming_coordinates}"
            )
        return incoming_coordinates
