# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from abc import ABCMeta, abstractmethod

from .AlfiConstants import logger_name
from .GremlinCoordinatesProvider import GremlinCoordinatesProvider
from .TrafficCoordinates import TrafficCoordinates

logger = logging.getLogger(f"{logger_name}.{__name__}")


class ContextAwareGremlinCoordinatesProvider(
    GremlinCoordinatesProvider, metaclass=ABCMeta
):
    """
    This class provides an implementation to extend :ref:`TrafficCoordinates` with per-request
    attributes.

    This class is designed to be used as a singleton
    """

    def per_thread_context(self):
        pass

    def extend_each_traffic_coordinates(
        self, incoming_coordinates: TrafficCoordinates
    ) -> TrafficCoordinates:
        if logger.getEffectiveLevel() is logging.DEBUG:
            logger.debug("Adding context to TrafficCoordinates")
        return incoming_coordinates

    def set_context(self, per_thread_context: dict[str, str]) -> None:
        pass

    def clear_context(self) -> None:
        pass
