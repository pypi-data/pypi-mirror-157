# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging
import http.client

# import requests

from alfipy.alfipy.alfi_messages_pb2 import (
    ExperimentResponseList as ALFIMessages_ExperimentResponseList,
)
from alfipy.alfipy.AlfiConstants import logger_name
from alfipy.alfipy.ApiGremlinService import ApiGremlinService
from alfipy.alfipy.ApplicationCoordinates import ApplicationCoordinates
from alfipy.alfipy.EnvironmentVariableCoordinatesProvider import (
    EnvironmentVariableCoordinatesProvider,
)
from alfipy.alfipy.GremlinApiHttpClient import GremlinApiHttpClient
from alfipy.alfipy.TrafficCoordinates import TrafficCoordinates
from alfipy.alfipy.TrafficType import TrafficType
from alfipy.alfipy.Atomic import AtomicBoolean
from alfipy.alfipy.AlfiConfig import AlfiConfig
from alfipy.alfipy.TrafficQuery import TrafficQuery
from alfipy.alfipy.ExperimentImpact import ExperimentImpact
from alfipy.alfipy.Impact import Impact

from .util import (
    mock_json,
    test_endpoint,
    mock_headers,
    test_version,
    mock_identifier,
    mock_experiments_resp,
    mock_guid,
    mock_data,
)

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)

AlfiConfig.client_identifier = mock_identifier


class TestApiGremlinService(unittest.TestCase):
    @patch("http.client.HTTPSConnection.getresponse")
    def test_get_experiment(self, mock_res) -> None:
        helper_ac = ApplicationCoordinates()
        helper_cp = EnvironmentVariableCoordinatesProvider()
        helper_gac = GremlinApiHttpClient(
            AlfiConfig, test_endpoint, test_version
        )
        helper = ApiGremlinService(helper_ac, helper_cp, helper_gac)
        helper_tc = TrafficCoordinates()

        mock_res.return_value = http.client.HTTPSConnection(
            test_endpoint
        ).getresponse()
        mock_res.return_value.data = mock_experiments_resp
        mock_res.return_value.getheaders = mock_headers
        mock_res.return_value.status = 200

        expected_output = None
        self.assertEqual(expected_output, helper.get_experiment(helper_tc))
        helper_gac.shutdown()

    @patch("http.client.HTTPSConnection.getresponse")
    def test_has_experiments(self, mock_res) -> None:
        helper_ac = ApplicationCoordinates()
        helper_cp = EnvironmentVariableCoordinatesProvider()
        helper_gac = GremlinApiHttpClient(
            AlfiConfig, test_endpoint, test_version
        )
        helper = ApiGremlinService(helper_ac, helper_cp, helper_gac)

        mock_res.return_value = http.client.HTTPSConnection(
            test_endpoint
        ).getresponse()
        mock_res.return_value.data = mock_experiments_resp
        mock_res.return_value.getheaders = mock_headers
        mock_res.return_value.status = 200

        expected_output = False
        self.assertEqual(expected_output, helper.has_experiments())
        helper_gac.shutdown()

    @patch("http.client.HTTPSConnection.getresponse")
    def test_determine_if_experiment_applies(self, mock_res) -> None:
        helper_ac = ApplicationCoordinates("keys")
        helper_cp = EnvironmentVariableCoordinatesProvider()
        helper_gac = GremlinApiHttpClient(
            AlfiConfig, test_endpoint, test_version
        )
        helper = ApiGremlinService(helper_ac, helper_cp, helper_gac)
        helper_map_from_api: dict[TrafficQuery, ExperimentImpact] = {
            TrafficQuery(
                TrafficType("name", "keys"), mock_data
            ): ExperimentImpact(mock_guid, Impact())
        }

        mock_res.return_value = http.client.HTTPSConnection(
            test_endpoint
        ).getresponse()
        mock_res.return_value.data = mock_experiments_resp
        mock_res.return_value.getheaders = mock_headers
        mock_res.return_value.status = 200

        expected_output = None

        self.assertEqual(
            expected_output,
            helper.determine_if_experiment_applies(
                helper_map_from_api, helper_ac
            ),
        )
        helper_gac.shutdown()
