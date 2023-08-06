# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .AlfiConstants import logger_name
from .ExperimentImpact import ExperimentImpact
from .Impact import Impact
from .GremlinService import GremlinService
from .TrafficCoordinates import TrafficCoordinates


logger = logging.getLogger(f"{logger_name}.{__name__}")


class PassthroughGremlinService(GremlinService):
    """
    A *NO-OP* implementation of :ref:`GremlinService` that is used when:
      - No other implementation :ref:`GremlinService` is available
      - ALFI is disabled by configuration
      - ALFI encounters a configuration error that would prevent communication to the API
    """

    def __init__(self) -> None:
        super().__init__()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GremlinService, cls).__new__(cls)
        return cls._instance

    def has_experiments(self) -> bool:
        return False

    def get_experiment(
        self, traffic_coordinates: TrafficCoordinates
    ) -> ExperimentImpact:
        return ExperimentImpact(experiment_guid="", impact=Impact())

    def shutdown(self) -> None:
        pass
