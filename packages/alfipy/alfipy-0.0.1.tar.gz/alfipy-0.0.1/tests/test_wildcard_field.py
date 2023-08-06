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
from alfipy.alfipy.WildcardField import WildcardField
from alfipy.alfipy.QueryField import QueryField

from .util import test_val

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestWildcardField(unittest.TestCase):
    def test_to_json_string(self) -> None:
        helper = WildcardField()
        self.assertEqual(helper.to_json_string(), QueryField.WILDCARD_STRING)
        self.assertEqual(helper.to_json_string(), "*")

    def test_matches(self) -> None:
        helper = WildcardField()
        self.assertTrue(helper.matches("arbitrary_input"))

    def test_is_wildcard(self) -> None:
        helper = WildcardField()
        self.assertTrue(helper.is_wildcard())

    def test_to_message(self) -> None:
        helper = WildcardField()
        expected_output = "query {\n  wildcard_field {\n  }\n}\n"
        self.assertEqual(expected_output, str(helper.to_message()))

    def test___eq__(self) -> None:
        helper = WildcardField()
        helper_2 = WildcardField()
        self.assertTrue(helper.__eq__(helper))
        self.assertFalse(helper.__eq__(None))
        self.assertTrue(helper.__eq__(helper_2))

    def test___str__(self) -> None:
        helper = WildcardField()
        expected_output = "WildcardField()"
        self.assertEqual(helper.__str__(), expected_output)
        self.assertEqual(str(helper), expected_output)
