# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .alfi_messages_pb2 import (
    ExperimentResponse as ALFIMessages_ExperimentResponse,
)
from .alfi_messages_pb2 import (
    ExperimentResponseList as ALFIMessages_ExperimentResponseList,
)

from .AlfiConstants import logger_name
from .TrafficQueryAndImpact import TrafficQueryAndImpact
from .TrafficAndImpactProvider import TrafficAndImpactProvider

from dataclasses import dataclass, field
from typing import Iterator

logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class ExperimentResponse:
    """
    High level encapsulation of experiment responses from :ref:`GremlinService` into deserialized objects
    """

    guid: str = field(default="")
    teamId: str = field(default="")
    traffic: list[TrafficQueryAndImpact] = field(default_factory=[])

    @classmethod
    def parse_from(
        cls, response: ALFIMessages_ExperimentResponse
    ) -> ExperimentResponse:
        return cls(
            response.guid,
            response.team_id,
            [
                TrafficAndImpactProvider().deserialize_model(message)
                for message in response.traffic
            ],
        )

    @classmethod
    def list_from_message(
        cls, response_message: ALFIMessages_ExperimentResponseList
    ) -> Iterator[ExperimentResponse]:
        if logger.getEffectiveLevel() is logging.DEBUG:
            logger.debug(f"l4m {response_message}")
        for response in response_message.responses:
            yield cls.parse_from(response)
