# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging
import requests

from alfipy.alfipy.AlfiConstants import logger_name
from .util import mock_json

from alfipy.alfipy.AlfiConfig import AlfiConfig

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.INFO)


class TestConfig(unittest.TestCase):
    def test_constrain_cache_refresh_interval(self) -> None:
        # None
        self.assertEqual(
            AlfiConfig.constrain_cache_refresh_interval(None), 10_000
        )
        # Default
        self.assertEqual(
            AlfiConfig.constrain_cache_refresh_interval(-1), 10_000
        )
        # Minimum
        self.assertEqual(
            AlfiConfig.constrain_cache_refresh_interval(800), 1000
        )
        # Maximum
        self.assertEqual(
            AlfiConfig.constrain_cache_refresh_interval(900000), 5 * 60 * 1000
        )
        # Acceptable Value
        self.assertEqual(
            AlfiConfig.constrain_cache_refresh_interval(128000), 128000
        )
