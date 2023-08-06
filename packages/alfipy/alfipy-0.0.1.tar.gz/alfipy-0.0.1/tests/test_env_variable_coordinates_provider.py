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
from alfipy.alfipy.EnvironmentVariableCoordinatesProvider import (
    EnvironmentVariableCoordinatesProvider,
)

from alfipy.alfipy.TrafficCoordinates import TrafficCoordinates

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestEnvironmentVariableCoordinatesProvider(unittest.TestCase):
    def test_initialize_coordinates(self) -> None:
        # defaults
        helper = EnvironmentVariableCoordinatesProvider()
        expected_output = "ApplicationCoordinates(type='NO_TYPE_PROVIDED', fields={'application_label': 'NOT_PROVIDED'})"
        self.assertEqual(str(helper.initialize_coordinates()), expected_output)

    def test_extend_each_traffic_coordinates(self) -> None:
        helper = EnvironmentVariableCoordinatesProvider()
        helper_tc = (
            TrafficCoordinates.Builder()
            .with_type("foo")
            .with_field("user", "kyle")
            .build()
        )
        self.assertEqual(
            helper.extend_each_traffic_coordinates(helper_tc), helper_tc
        )
