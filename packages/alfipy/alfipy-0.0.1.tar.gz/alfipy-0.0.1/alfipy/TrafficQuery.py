# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging
import secrets

from abc import ABCMeta, abstractmethod

from .alfi_messages_pb2 import TrafficQuery as ALFIMessages_TrafficQuery

from .AlfiConstants import logger_name
from .QueryField import QueryField
from .QueryModel import QueryModel
from .TrafficCoordinates import TrafficCoordinates
from .TrafficType import TrafficType

from dataclasses import dataclass, InitVar


logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class TrafficQuery(QueryModel):
    """
    Part of an ApplicationExperiment - the customer defines which traffic to affect.
    An ApplicationExperiment may compose multiple :ref:`TrafficQuery`s.  If traffic
    matches, then a :ref:`Impact` is applied.
    """

    type: TrafficType = None
    fields: dict[str, QueryField] = None

    def should_apply_impact(self, coordinates: TrafficCoordinates) -> bool:
        if self.matches(coordinates):
            return self.percentage_to_impact > secrets.SystemRandom().random()
        return False

    def to_message(self) -> ALFIMessages_TrafficQuery:
        tq = ALFIMessages_TrafficQuery()
        return tq

    def __hash__(self):
        return super().__hash__()

    @dataclass
    class Builder(QueryModel.Builder):
        provider: InitVar = None

        def __post_init__(self, provider) -> None:
            self._provider = provider

        def build(self) -> TrafficQuery:
            return self._provider.create_model(
                self._provider.get_type(self.type),
                self.fields,
                self.percentage_to_impact,
            )
