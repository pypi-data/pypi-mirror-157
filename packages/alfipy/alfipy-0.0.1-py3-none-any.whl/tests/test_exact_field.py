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
from alfipy.alfipy.ExactField import ExactField

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)

from .util import test_key, test_val


class TestExactField(unittest.TestCase):
    def test_to_json_string(self) -> None:
        helper = ExactField(test_val)
        self.assertEqual(helper.to_json_string(), test_val)

    def test_matches(self) -> None:
        helper = ExactField(test_val)
        self.assertTrue(helper.matches(test_val))

    def test_to_string(self) -> None:
        helper = ExactField(test_val)
        expected_output = f"ExactField{{data={test_val}}}"
        self.assertEqual(helper.to_string(), expected_output)

    def test_to_message(self) -> None:
        helper = ExactField(test_val)
        expected_output = (
            'query {\n  exact_field {\n    value: "%s"\n  }\n}\n' % test_val
        )
        self.assertEqual(str(helper.to_message()), expected_output)

    def test___str__(self) -> None:
        helper = ExactField(test_val)
        expected_output = "ExactField(data=%s)" % test_val
        self.assertEqual(str(helper), expected_output)
