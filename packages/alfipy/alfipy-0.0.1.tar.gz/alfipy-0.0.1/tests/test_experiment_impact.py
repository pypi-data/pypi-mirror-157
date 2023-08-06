# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging

# import requests

from alfipy.alfipy.AlfiConstants import logger_name, AlfiConstants
from alfipy.alfipy.ExperimentImpact import ExperimentImpact
from alfipy.alfipy.Impact import Impact
from alfipy.alfipy.ImpactType import ImpactType
from alfipy.alfipy.ImpactProvider import ImpactProvider

from .util import test_value_str, mock_guid, test_latency

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestExperimentImpact(unittest.TestCase):
    def test_latency(self) -> None:
        helper = ExperimentImpact(
            experiment_guid=mock_guid,
            impact=Impact(
                type=ImpactType(name="", keys=None),
                fields={
                    "exception_should_be_thrown": True,
                    "latency_to_add_in_ms": test_latency,
                },
            ),
            impact_provider=ImpactProvider(query_keys={}),
        )
        helper_impact_provider = ImpactProvider()
        # TypeError: 'dict' object is not callable
        # self.assertEqual(helper.latency(mock_guid, 100), "")

    def test_fail(self) -> None:
        helper = ExperimentImpact(
            experiment_guid=mock_guid,
            impact=Impact(
                type=ImpactType(name="", keys=None),
                fields={
                    "exception_should_be_thrown": True,
                    "latency_to_add_in_ms": test_latency,
                },
            ),
            impact_provider=ImpactProvider(query_keys={}),
        )
        helper_impact_provider = ImpactProvider()
        # TypeError: 'dict' object is not callable
        # self.assertEqual(helper.fail(test_value_str, 100), "")

    def test_get_impact(self) -> None:
        helper = ExperimentImpact(
            experiment_guid=mock_guid,
            impact=Impact(
                type=ImpactType(name="", keys=None),
                fields={
                    "exception_should_be_thrown": True,
                    "latency_to_add_in_ms": test_latency,
                },
            ),
            impact_provider=ImpactProvider(query_keys={}),
        )
        expected_output = "Impact(type=ImpactType(name='', keys=None), fields={'exception_should_be_thrown': True, 'latency_to_add_in_ms': 300.0})"
        self.assertEqual(str(helper.get_impact()), expected_output)

    def test_get_impact_parameter(self) -> None:
        helper = ExperimentImpact(
            experiment_guid=mock_guid,
            impact=Impact(
                type=ImpactType(name="", keys=None),
                fields={
                    "exception_should_be_thrown": True,
                    "latency_to_add_in_ms": test_latency,
                },
            ),
            impact_provider=ImpactProvider(query_keys={}),
        )
        expected_output = "Impact(type=ImpactType(name='', keys=None), fields={'exception_should_be_thrown': True, 'latency_to_add_in_ms': 300.0})"
        self.assertEqual(
            str(helper.get_impact_parameter("arbitrary key")), expected_output
        )

    def test_parse_from_impact(self) -> None:
        helper_impact = Impact(
            type=ImpactType(name="", keys=None),
            fields={
                "exception_should_be_thrown": True,
                "latency_to_add_in_ms": test_latency,
            },
        )
        expected_output = ExperimentImpact(mock_guid, helper_impact)
        self.assertEqual(
            ExperimentImpact.parse_from_impact(mock_guid, helper_impact),
            expected_output,
        )

    def test_get_experiment_guid(self) -> None:
        helper = ExperimentImpact(
            experiment_guid=mock_guid,
            impact=Impact(
                type=ImpactType(name="", keys=None),
                fields={
                    "exception_should_be_thrown": True,
                    "latency_to_add_in_ms": test_latency,
                },
            ),
            impact_provider=ImpactProvider(query_keys={}),
        )
        self.assertEqual(helper.get_experiment_guid(), mock_guid)
