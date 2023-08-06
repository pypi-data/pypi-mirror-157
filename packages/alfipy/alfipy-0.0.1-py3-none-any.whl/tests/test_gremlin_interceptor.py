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
from alfipy.alfipy.GremlinInterceptor import GremlinInterceptor
from alfipy.alfipy.EnvironmentVariableConfigurationResolver import (
    EnvironmentVariableConfigurationResolver,
)
from alfipy.alfipy.TestGremlinCoordinatesProvider import (
    TestGremlinCoordinatesProvider,
)

from typing import Callable

from .util import mock_json

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestGremlinInterceptor(unittest.TestCase):
    def test_build_coordinates(self) -> None:
        helper = GremlinInterceptor(
            configuration_resolver=EnvironmentVariableConfigurationResolver,
            coordinates_provider=TestGremlinCoordinatesProvider,
        )
        expected_output = "TrafficCoordinates(type=TrafficType(name='', keys=None), fields={})"
        self.assertEqual(
            expected_output,
            str(helper.build_coordinates(mock_json, [], {}, "", {})),
        )

    def test_coordinates(self) -> None:
        helper = GremlinInterceptor(
            configuration_resolver=EnvironmentVariableConfigurationResolver,
            coordinates_provider=TestGremlinCoordinatesProvider,
        )
        self.assertTrue(isinstance(helper.coordinates(type="str"), Callable))
