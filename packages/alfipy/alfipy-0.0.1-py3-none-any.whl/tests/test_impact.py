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
from alfipy.alfipy.Impact import Impact
from alfipy.alfipy.ImpactType import ImpactType
from alfipy.alfipy.TypedAlfiModel import TypedAlfiModel
from alfipy.alfipy.alfi_messages_pb2 import Impact as ALFIMessages_Impact


from .util import test_key, test_val

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestImpact(unittest.TestCase):
    def test_get_or_default(self) -> None:
        helper = Impact(
            type=ImpactType(name="", keys=None),
            fields={
                "exception_should_be_thrown": True,
                "latency_to_add_in_ms": 300.0,
                test_key: test_val,
            },
        )
        # test default
        self.assertEqual(
            helper.get_or_default("not the right key", test_val), test_val
        )
        # test get
        self.assertEqual(
            helper.get_or_default(test_key, "bad default key"), test_val
        )

    def test_get_impact_parameter(self) -> None:
        helper = Impact(
            type=ImpactType(name="", keys=None),
            fields={
                "exception_should_be_thrown": True,
                "latency_to_add_in_ms": 300.0,
                test_key: test_val,
            },
        )
        self.assertEqual(helper.get_impact_parameter(test_key), test_val)

    def test_to_message(self) -> None:
        helper_AMI = ALFIMessages_Impact()
        helper = Impact(
            type=ImpactType(name="", keys=None),
            fields={
                "exception_should_be_thrown": True,
                "latency_to_add_in_ms": 300.0,
                test_key: test_val,
            },
        )
        # TODO: expand when Impact populated in base code
        self.assertEqual(str(helper.to_message()), str(helper_AMI))

    def test_field_to_message(self) -> None:
        # TODO: expand when to_message populated in base code
        pass
