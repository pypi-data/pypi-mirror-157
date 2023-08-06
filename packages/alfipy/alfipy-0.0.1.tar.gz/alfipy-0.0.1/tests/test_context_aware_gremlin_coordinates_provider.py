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
from alfipy.alfipy.ContextAwareGremlinCoordinatesProvider import (
    ContextAwareGremlinCoordinatesProvider,
)
from alfipy.alfipy.TrafficCoordinates import TrafficCoordinates

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestContextAwareGremlinCoordinatesProvider(unittest.TestCase):
    def test_per_thread_context(self) -> None:
        self.assertEqual(True, False)

    def test_extend_each_traffic_coordinates(self) -> None:
        helper = ContextAwareGremlinCoordinatesProvider()
        helper_tc = TrafficCoordinates()
        self.assertEqual(
            helper.extend_each_traffic_coordinates(helper_tc), helper_tc
        )

    def test_set_context(self) -> None:
        self.assertEqual(True, False)

    def test_clear_context(self) -> None:
        self.assertEqual(True, False)
