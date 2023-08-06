# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging

from alfipy.alfipy.AlfiConstants import logger_name
from alfipy.alfipy.TrafficAndImpactProvider import TrafficAndImpactProvider
from alfipy.alfipy.alfi_messages_pb2 import (
    TrafficQueryAndImpact as ALFIMessages_TrafficQueryAndImpact,
)
from alfipy.alfipy.alfi_messages_pb2 import (
    TrafficQuery as ALFIMessages_TrafficQuery,
)
from alfipy.alfipy.Impact import Impact
from alfipy.alfipy.ImpactProvider import ImpactProvider
from alfipy.alfipy.TrafficQueryAndImpact import TrafficQueryAndImpact
from alfipy.alfipy.TrafficQueryProvider import TrafficQueryProvider
from alfipy.alfipy.TrafficQuery import TrafficQuery

from .util import mock_data, test_val, test_key

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestTrafficAndImpactProvider(unittest.TestCase):
    def test_deserialize_model(self) -> None:
        helper_tqp = TrafficQueryProvider()
        helper_ip = ImpactProvider(query_keys={})
        helper = TrafficAndImpactProvider(helper_tqp, helper_ip)
        traffic_query = ALFIMessages_TrafficQuery()
        test_input = ALFIMessages_TrafficQueryAndImpact(
            traffic_query=traffic_query
        )
        expected_output = "TrafficQueryAndImpact(query=TrafficQuery(type=TrafficType(name='', keys=None), fields={}, percentage_to_impact=0), impact=Impact(type=ImpactType(name='', keys=None), fields={}))"
        self.assertEqual(
            str(helper.deserialize_model(test_input)), expected_output
        )
