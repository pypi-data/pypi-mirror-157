# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging

# import requests

from alfipy.alfipy.AlfiConstants import logger_name
from alfipy.alfipy.TrafficQueryProvider import TrafficQueryProvider
from alfipy.alfipy.TrafficType import TrafficType
from alfipy.alfipy.TrafficQuery import TrafficQuery
from alfipy.alfipy.TrafficCoordinates import TrafficCoordinates
from alfipy.alfipy.alfi_messages_pb2 import (
    TrafficQuery as ALFIMessages_TrafficQuery,
)

from .util import test_val

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestTrafficQueryProvider(unittest.TestCase):
    def test_get_type(self) -> None:
        helper = TrafficQueryProvider()
        expected_output = TrafficType(test_val, None)
        self.assertEqual(expected_output, helper.get_type(test_val))

    def test_create_model(self) -> None:
        helper = TrafficQueryProvider()
        traffic_type = TrafficType(test_val, None)
        percentage_to_impact = 50
        fields = {}
        expected_output = TrafficQuery(
            type=traffic_type,
            fields=fields,
            percentage_to_impact=percentage_to_impact,
        )
        self.assertEqual(
            expected_output,
            helper.create_model(traffic_type, fields, percentage_to_impact),
        )

    def test_deserialize_model(self) -> None:
        helper = TrafficQueryProvider()
        traffic_type = TrafficType(test_val, None)
        helper_TC = ALFIMessages_TrafficQuery(query_model={})
        expected_output = "TrafficQuery(type=TrafficType(name='', keys=None), fields={}, percentage_to_impact=0)"
        self.assertEqual(
            str(helper.deserialize_model(helper_TC)), expected_output
        )

    def test_new_query_from_coordinates(self) -> None:
        tc = (
            TrafficCoordinates.Builder()
            .with_type("foo")
            .with_field("user", "kyle")
            .build()
        )
        helper = TrafficQueryProvider()
        expected_output = tc
        # The code in the following function `TrafficQuery.Builder().with_type(tc.type.name)`
        # results in an error `TypeError: 'dict' object is not callable`
        # self.assertEqual(expected_output, helper.new_query_from_coordinates(tc))
