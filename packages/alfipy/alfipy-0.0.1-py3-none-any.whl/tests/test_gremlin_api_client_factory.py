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
from alfipy.alfipy.GremlinApiClientFactory import GremlinApiClientFactory
from alfipy.alfipy.AlfiConfig import AlfiConfig
from alfipy.alfipy.GremlinApiClient import GremlinApiClient

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestGremlinApiClientFactory(unittest.TestCase):
    def test_get_api_client(self) -> None:
        test_len = 42
        helper = GremlinApiClientFactory.get_api_client(AlfiConfig)
        helper_head = helper._build_headers(test_len)
        helper_head.pop("Authorization")
        expected_output = (
            "{'X-Gremlin-Agent': 'alfi-python/0.0.1', 'Connection': 'keep-alive', 'Content-Length': %d, 'Content-Type': 'application/protobuf'}"
            % test_len
        )
        self.assertEqual(str(helper_head), expected_output)
