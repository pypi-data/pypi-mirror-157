# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .AlfiConstants import AlfiConstants, logger_name
from .Impact import Impact
from .ImpactProvider import ImpactProvider

from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class ExperimentImpact:
    """
    Encapsulates the :ref:`Impact` and :ref:`ImpactProvider` into a single object
    """

    experiment_guid: str
    impact: Impact
    impact_provider: Optional[ImpactProvider] = field(
        default_factory=ImpactProvider
    )

    def latency(self, guid: str, amount_in_ms: int) -> ExperimentImpact:
        return ExperimentImpact(
            experiment_guid=guid,
            impact=self.impact_provider.new_builder()
            .with_type(AlfiConstants.TI_GENERAL_NAME)
            .with_field(AlfiConstants.KEY_LATENCY_TO_ADD_IN_MS, amount_in_ms)
            .with_field(AlfiConstants.KEY_EXCEPTION_SHOULD_BE_THROWN, False)
            .build(),
        )

    def fail(
        self, guid: str, amount_in_ms: Optional[int] = 0
    ) -> ExperimentImpact:
        return ExperimentImpact(
            experiment_guid=guid,
            impact=self.impact_provider.new_builder()
            .with_type(AlfiConstants.TI_GENERAL_NAME)
            .with_field(AlfiConstants.KEY_LATENCY_TO_ADD_IN_MS, amount_in_ms)
            .with_field(AlfiConstants.KEY_EXCEPTION_SHOULD_BE_THROWN, True)
            .build(),
        )

    def get_impact(self) -> Impact:
        return self.impact

    def get_impact_parameter(self, key: str) -> object:
        return self.impact

    def parse_from_(
        self, guid: str, should_fail: bool, latency_to_add_in_ms: int
    ) -> ExperimentImpact:
        pass

    @classmethod
    def parse_from_impact(cls, guid: str, impact: Impact) -> ExperimentImpact:
        return cls(guid, impact)

    def get_experiment_guid(self) -> str:
        return self.experiment_guid
