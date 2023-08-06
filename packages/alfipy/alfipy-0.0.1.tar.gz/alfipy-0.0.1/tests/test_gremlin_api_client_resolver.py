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
from alfipy.alfipy.GremlinApiClientResolver import GremlinApiClientResolver
from alfipy.alfipy.AlfiConfig import AlfiConfig
from alfipy.alfipy.GremlinApiClient import GremlinApiClient
from alfipy.alfipy.Exceptions import ALFIApiClientException

from .util import test_retries, test_len, test_endpoint, test_version

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestGremlinApiClientResolver(unittest.TestCase):
    def test_get_client(self) -> None:
        helper_client: GremlinApiClient = GremlinApiClientResolver.get_client(
            AlfiConfig, test_endpoint, test_version, test_retries
        )
        helper_head = helper_client._build_headers(test_len)
        helper_head.pop("Authorization")
        expected_output = (
            "{'X-Gremlin-Agent': 'alfi-python/0.0.1', 'Connection': 'keep-alive', 'Content-Length': %d, 'Content-Type': 'application/protobuf'}"
            % test_len
        )
        self.assertEqual(str(helper_head), expected_output)

    def test_get_specific_client(self) -> None:
        def tryme():
            return GremlinApiClientResolver.get_specific_client(
                "badclienttype",
                AlfiConfig,
                test_endpoint,
                test_version,
                test_retries,
            )

        self.assertRaises(ALFIApiClientException, tryme)
        helper_client: GremlinApiClient = (
            GremlinApiClientResolver.get_specific_client(
                "GremlinApiHttpClient",
                AlfiConfig,
                test_endpoint,
                test_version,
                test_retries,
            )
        )
        helper_head = helper_client._build_headers(test_len)
        helper_head.pop("Authorization")
        expected_output = (
            "{'X-Gremlin-Agent': 'alfi-python/0.0.1', 'Connection': 'keep-alive', 'Content-Length': %d, 'Content-Type': 'application/protobuf'}"
            % test_len
        )
        self.assertEqual(str(helper_head), expected_output)
