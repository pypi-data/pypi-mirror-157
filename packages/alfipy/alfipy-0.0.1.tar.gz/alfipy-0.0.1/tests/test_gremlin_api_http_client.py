# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging
import http.client
import requests

from alfipy.alfipy.AlfiConstants import logger_name
from alfipy.alfipy.GremlinApiHttpClient import GremlinApiHttpClient
from alfipy.alfipy.AlfiConfig import AlfiConfig


from .util import (
    test_endpoint,
    test_version,
    mock_json,
    mock_data,
    mock_headers,
)

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestGremlinApiHttpClient(unittest.TestCase):
    def test__initialize_build_conn(self) -> None:
        helper = GremlinApiHttpClient(AlfiConfig, test_endpoint, test_version)
        expected_output = http.client.HTTPSConnection(
            test_endpoint,
            timeout=500 / 1000,  # default
        )
        self.assertNotEqual(helper._http_conn, None)
        self.assertEqual(type(expected_output), type(helper._build_conn()))

    @patch("http.client.HTTPSConnection.getresponse")
    def test__request(self, mock_post) -> None:
        helper = GremlinApiHttpClient(AlfiConfig, test_endpoint, test_version)
        mock_status_code = 200

        # 200 status code
        mock_post.return_value = http.client.HTTPSConnection(
            test_endpoint
        ).getresponse()
        mock_post.return_value.read = mock_json
        mock_post.return_value.getheaders = mock_headers
        mock_post.return_value.status = mock_status_code

        helper_req = helper._request(
            "POST", test_endpoint, "body", {"headers": "headers"}, 0
        )
        helper_req.pop("raw")
        expected_output = (
            "{'data': {'testkey': 'testval'}, 'status': %d, 'headers': {'auth': '123yg34256iuh'}}"
            % mock_status_code
        )
        self.assertEqual(expected_output, str(helper_req))
        helper.shutdown()

    @patch("http.client.HTTPSConnection.getresponse")
    def test__request_400status(self, mock_post) -> None:
        helper = GremlinApiHttpClient(AlfiConfig, test_endpoint, test_version)
        mock_status_code = 400

        # 400 status code
        mock_post.return_value = http.client.HTTPSConnection(
            test_endpoint
        ).getresponse()
        mock_post.return_value.read = mock_json
        mock_post.return_value.getheaders = mock_headers
        mock_post.return_value.status = mock_status_code

        # retry of 11 causes the request to not be retried (11 > max_retries)
        helper_req = helper._request(
            "POST", test_endpoint, "body", {"headers": "headers"}, 11
        )
        expected_output = "{'status': -1}"
        self.assertEqual(expected_output, str(helper_req))
        helper.shutdown()

    @patch("http.client.HTTPSConnection.getresponse")
    def test__request_badstatus(self, mock_post) -> None:
        helper = GremlinApiHttpClient(AlfiConfig, test_endpoint, test_version)
        mock_status_code = 500

        # 500 status code
        mock_post.return_value = http.client.HTTPSConnection(
            test_endpoint
        ).getresponse()
        mock_post.return_value.read = mock_json
        mock_post.return_value.getheaders = mock_headers
        mock_post.return_value.status = mock_status_code

        helper_req = helper._request(
            "POST", test_endpoint, "body", {"headers": "headers"}, 0
        )
        expected_output = "{'status': %d}" % mock_status_code
        self.assertEqual(expected_output, str(helper_req))
        helper.shutdown()
