# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .alfi_messages_pb2 import TrafficQuery as ALFIMessages_TrafficQuery

from .AlfiConstants import logger_name
from .QueryField import QueryField
from .QueryTypeProvider import QueryTypeProvider
from .TrafficCoordinates import TrafficCoordinates
from .TrafficType import TrafficType
from .TrafficQuery import TrafficQuery

from dataclasses import dataclass


logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class TrafficQueryProvider(QueryTypeProvider):
    """
    Implementation of :ref:`QueryTypeProvider`
    Provides a deserialization interface for protocol buffer messages
    """

    def get_type(self, name: str) -> TrafficType:
        return TrafficType(name, self.keys_for_type(name))

    def create_model(
        self,
        type: TrafficType,
        fields: dict[str, QueryField],
        percentage_to_impact: int,
    ) -> TrafficQuery:
        return TrafficQuery(
            type=type, fields=fields, percentage_to_impact=percentage_to_impact
        )

    def deserialize_model(
        self, message: ALFIMessages_TrafficQuery
    ) -> TrafficQuery:
        query_message = message.query_model
        typed_message = query_message.typed_alfi_model
        return self.create_model(
            self.get_type(typed_message.type),
            self.get_fields(typed_message),
            self.get_percentage_to_impact(query_message),
        )

    def new_query_from_coordinates(
        self, coordinates: TrafficCoordinates
    ) -> TrafficQuery:
        builder = TrafficQuery.Builder().with_type(coordinates.type.name)
        for key in coordinates.type.required_keys:
            builder.with_exact_field(key, coordinates.fields.get(key))
        return builder.build()
