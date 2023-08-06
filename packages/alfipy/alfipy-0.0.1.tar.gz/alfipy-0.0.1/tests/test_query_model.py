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
from alfipy.alfipy.QueryModel import QueryModel

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestQueryModel(unittest.TestCase):
    def test_matches(self) -> None:
        self.assertEqual(True, False)

    def test_to_string(self) -> None:
        self.assertEqual(True, False)

    def test_field_to_message(self) -> None:
        self.assertEqual(True, False)

    def test___eq__(self) -> None:
        self.assertEqual(True, False)

    def test___hash__(self) -> None:
        self.assertEqual(True, False)
