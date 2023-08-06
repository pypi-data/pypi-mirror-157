# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .alfi_messages_pb2 import (
    ApplicationCoordinates as ALFIMessages_ApplicationCoordinates,
)

from .AlfiConstants import logger_name
from .Coordinates import Coordinates

from dataclasses import dataclass

logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class ApplicationCoordinates(Coordinates):
    """
    A set of attributes describing the application to Gremlin. All attributes you include in this
    object are available to match on when creating an experiment.

    An example of :ref:`ApplicationCoordinates` in English is::

        On AWS Lambda running in `US-West-2` named `event-handler`.

    To build your own, use the :ref:`ApplicationCoordinates.Builder` and pass in a type and as many
    fields as you'd like.

    An example of :ref:`ApplicationCoordinates` in Python is::

        application_coordinates = ApplicationCoordinates.Builder().with_type(
            'event-handler').with_field('application_owner', 'kyle').with_field(
            'environment',  'awslambda').with_field('region', 'us-west-2').build()

    """

    def to_message(self) -> ALFIMessages_ApplicationCoordinates:
        ac = ALFIMessages_ApplicationCoordinates()
        ac.coordinates.CopyFrom(super().to_message())
        return ac

    @dataclass
    class Builder(Coordinates.Builder):
        def build(self) -> ApplicationCoordinates:
            return ApplicationCoordinates(self.type, self.fields)
