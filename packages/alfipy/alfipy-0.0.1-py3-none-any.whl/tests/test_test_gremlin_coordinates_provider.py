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
from alfipy.alfipy.TestGremlinCoordinatesProvider import (
    TestGremlinCoordinatesProvider,
)

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestTestGremlinCoordinatesProvider(unittest.TestCase):
    def test_initialize_coordinates(self) -> None:
        self.assertEqual(True, False)

    def test_extend_each_traffic_coordinates(self) -> None:
        self.assertEqual(True, False)
