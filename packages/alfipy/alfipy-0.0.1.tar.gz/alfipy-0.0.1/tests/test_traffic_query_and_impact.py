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
from alfipy.alfipy.TrafficQueryAndImpact import TrafficQueryAndImpact
from alfipy.alfipy.Impact import Impact
from alfipy.alfipy.ImpactType import ImpactType
from alfipy.alfipy.TrafficQuery import TrafficQuery
from alfipy.alfipy.alfi_messages_pb2 import (
    TrafficQueryAndImpact as ALFIMessages_TrafficQueryAndImpact,
)
from alfipy.alfipy.alfi_messages_pb2 import (
    Impact as ALFI_Impact,
)
from alfipy.alfipy.alfi_messages_pb2 import (
    TrafficQuery as ALFI_TrafficQuery,
)

from .util import test_key, test_val

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestTrafficQueryAndImpact(unittest.TestCase):
    def test_to_message(self) -> None:
        traffic_query = ALFI_TrafficQuery()
        impact = ALFI_Impact()
        helper = TrafficQueryAndImpact(traffic_query, impact)
        expected_output = ALFIMessages_TrafficQueryAndImpact()
        expected_output.impact.CopyFrom(impact)
        expected_output.traffic_query.CopyFrom(traffic_query)
        self.assertEqual(helper.to_message(), expected_output)

    def test___eq__(self) -> None:
        traffic_query = TrafficQuery()
        impact = Impact(
            type=ImpactType(name="", keys=None),
            fields={
                "exception_should_be_thrown": True,
                "latency_to_add_in_ms": 300.0,
            },
        )
        helper = TrafficQueryAndImpact(traffic_query, impact)
        helper_2 = TrafficQueryAndImpact(traffic_query, impact)
        self.assertTrue(helper.__eq__(helper))
        self.assertFalse(helper.__eq__(None))
        self.assertTrue(helper.__eq__(helper_2))
