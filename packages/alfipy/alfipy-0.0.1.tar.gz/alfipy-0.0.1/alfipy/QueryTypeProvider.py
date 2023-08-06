# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from abc import ABCMeta, abstractmethod

from .alfi_messages_pb2 import Field as ALFIMessages_Field
from .alfi_messages_pb2 import QueryModel as ALFIMessages_QueryModel

from .AlfiConstants import logger_name
from .Exceptions import ALFIIllegalArgumentException
from .QueryField import QueryField
from .TypeProvider import TypeProvider

from dataclasses import dataclass

logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class QueryTypeProvider(TypeProvider, metaclass=ABCMeta):
    """
    Abstract implementation of :ref:`TypeProvider` to map `QueryType`
    """

    def get_field_from_proto_entry(
        self, entry: dict[str, ALFIMessages_Field]
    ) -> object:
        if not entry or not entry.HasField("query"):
            raise ALFIIllegalArgumentException(
                "Invalid Query protobuf message. Fields of wrong type."
            )
        return QueryField.from_message(entry)
        # query = entry.query
        # if query.HasField("exact_field"):
        #     return query.exact_field.value
        # else:
        #     return "*"

    def get_percentage_to_impact(
        self, model_message: ALFIMessages_QueryModel
    ) -> float:
        if model_message.HasField("percentage_to_impact"):
            return model_message.percentage_to_impact.value
        else:
            return 0
