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
from alfipy.alfipy.ExperimentResponse import ExperimentResponse
from alfipy.alfipy.TrafficQueryAndImpact import TrafficQueryAndImpact
from alfipy.alfipy.alfi_messages_pb2 import (
    ExperimentResponse as ALFIMessages_ExperimentResponse,
)
from alfipy.alfipy.alfi_messages_pb2 import (
    ExperimentResponseList as ALFIMessages_ExperimentResponseList,
)

from typing import Iterator

from .util import mock_guid, mock_teamid, mock_query, mock_impact

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestExperimentResponse(unittest.TestCase):
    def test_parse_from(self) -> None:
        helper = ExperimentResponse.parse_from(
            ALFIMessages_ExperimentResponse(
                guid=mock_guid, team_id=mock_teamid
            )
        )
        expected_output = f"ExperimentResponse(guid='{mock_guid}', teamId='{mock_teamid}', traffic=[])"
        self.assertEqual(str(helper), expected_output)

    def test_list_from_message(self) -> None:
        helper_AMERL = ALFIMessages_ExperimentResponseList()
        helper_AMER = ALFIMessages_ExperimentResponse(
            guid=mock_guid, team_id=mock_teamid
        )
        helper_AMERL.responses.append(helper_AMER)
        helper: Iterator[
            ExperimentResponse
        ] = ExperimentResponse.list_from_message(helper_AMERL)
        expected_output = f"ExperimentResponse(guid='{mock_guid}', teamId='{mock_teamid}', traffic=[])"
        for _helper in helper:
            self.assertEqual(str(_helper), expected_output)
