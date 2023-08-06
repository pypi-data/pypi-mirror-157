# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging
import json
import os

from .AlfiConstants import logger_name
from .ApplicationCoordinates import ApplicationCoordinates
from .EnvironmentVariableNameKeys import EnvironmentVariableNameKeys as ENVARS
from .Exceptions import ALFIIllegalArgumentException
from .GremlinCoordinatesProvider import GremlinCoordinatesProvider
from .TrafficCoordinates import TrafficCoordinates

logger = logging.getLogger(f"{logger_name}.{__name__}")


class EnvironmentVariableCoordinatesProvider(GremlinCoordinatesProvider):
    """
    This is the default :class:`GremlinCoordinatesProvider` used if the the user does not
    override or supply a different one in their application
    """

    def initialize_coordinates(self):
        ab = ApplicationCoordinates.Builder().with_type(
            os.getenv(ENVARS.gremlin_application_type, "NO_TYPE_PROVIDED")
        )
        labels = json.loads(
            os.getenv(
                ENVARS.gremlin_application_labels,
                '{"application_label": "NOT_PROVIDED"}',
            )
        )
        if not isinstance(labels, dict):
            error_msg = "Application Labels should be a json set of key/value pairs when provided by ENVARS"
            logger.critical(error_msg)
            raise ALFIIllegalArgumentException(error_msg)
        for field in labels.keys():
            ab.with_field(field, labels.get(field))
        return ab.build()

    def extend_each_traffic_coordinates(
        self, incoming_coordinates: TrafficCoordinates
    ) -> TrafficCoordinates:
        if logger.getEffectiveLevel() is logging.DEBUG:
            logger.debug(
                f"Adding context to TrafficCoordinates {incoming_coordinates}"
            )
        return incoming_coordinates
