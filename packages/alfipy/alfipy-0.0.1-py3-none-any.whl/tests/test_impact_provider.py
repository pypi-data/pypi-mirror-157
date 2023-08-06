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
from alfipy.alfipy.ImpactProvider import ImpactProvider
from alfipy.alfipy.Impact import Impact
from alfipy.alfipy.TypedAlfiModel import TypedAlfiModel
from alfipy.alfipy.alfi_messages_pb2 import Impact as ALFIMessages_Impact
from alfipy.alfipy.alfi_messages_pb2 import Field as ALFIMessages_Field

from .util import (
    test_key,
    test_val,
    mock_data,
    mock_list,
    test_value_bool,
    test_len,
    mock_struct,
)

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)

# helper_t = TypedAlfiModel.Keys([test_key], [test_key])


class TestImpactProvider(unittest.TestCase):
    def test_get_type(self) -> None:
        helper = ImpactProvider(query_keys={})
        expected_output = f"ImpactType(name='{test_key}', keys=None)"
        self.assertEqual(expected_output, str(helper.get_type(test_key)))

    def test_create_model(self) -> None:
        helper = ImpactProvider(query_keys={})
        helper_impact = Impact(helper.get_type(test_key), mock_data)
        expected_output = helper.create_model(
            helper.get_type(test_key), mock_data
        )
        self.assertEqual(expected_output, helper_impact)

    def test_deserialize_model(self) -> None:
        helper = ImpactProvider(query_keys={})
        helper_impact = ALFIMessages_Impact()
        expected_output = (
            "Impact(type=ImpactType(name='', keys=None), fields={})"
        )
        self.assertEqual(
            str(helper.deserialize_model(helper_impact)), expected_output
        )

    def test_get_field_from_proto_entry(self) -> None:
        helper = ImpactProvider(query_keys={})
        test_input = ALFIMessages_Field(
            impact={
                "null_value": True,
            }
        )
        self.assertFalse(helper.get_field_from_proto_entry(test_input))
        test_input = ALFIMessages_Field(
            impact={
                "bool_value": test_value_bool,
            }
        )
        self.assertEqual(
            helper.get_field_from_proto_entry(test_input), test_value_bool
        )
        test_input = ALFIMessages_Field(
            impact={
                "number_value": test_len,
            }
        )
        self.assertEqual(
            helper.get_field_from_proto_entry(test_input), test_len
        )
        test_input = ALFIMessages_Field(
            impact={
                "string_value": test_key,
            }
        )
        self.assertEqual(
            helper.get_field_from_proto_entry(test_input), test_key
        )
