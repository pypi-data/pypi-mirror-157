# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging

from alfipy.alfipy.AlfiConstants import logger_name
from alfipy.alfipy.TrafficCoordinates import TrafficCoordinates
from alfipy.alfipy.alfi_messages_pb2 import (
    TrafficCoordinates as ALFIMessages_TrafficCoordinates,
)

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestTrafficCoordinates(unittest.TestCase):
    def test_to_message(self) -> None:
        helper = (
            TrafficCoordinates.Builder()
            .with_type("foo")
            .with_field("user", "kyle")
            .build()
        )
        expected_output = ALFIMessages_TrafficCoordinates()
        # TODO: further populate when to_message returns something non-default
        self.assertEqual(helper.to_message(), expected_output)
