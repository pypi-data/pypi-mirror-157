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
from alfipy.alfipy.TrafficQuery import TrafficQuery
from alfipy.alfipy.TrafficCoordinates import TrafficCoordinates
from alfipy.alfipy.alfi_messages_pb2 import (
    TrafficQuery as ALFIMessages_TrafficQuery,
)

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestTrafficQuery(unittest.TestCase):
    def test_should_apply_impact(self) -> None:
        helper = TrafficQuery()
        helper_tc = (
            TrafficCoordinates.Builder()
            .with_type("foo")
            .with_field("user", "kyle")
            .build()
        )
        self.assertFalse(helper.should_apply_impact(helper_tc))

    def test_to_message(self) -> None:
        helper = TrafficQuery()
        expected_output = ALFIMessages_TrafficQuery()
        # TODO: further populate when to_message returns something non-default
        self.assertEqual(helper.to_message(), expected_output)
