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
from alfipy.alfipy.GremlinApiClient import GremlinApiClient

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestGremlinApiClient(unittest.TestCase):
    def test__initialize_conn(self) -> None:
        self.assertEqual(True, False)

    def test__build_headers(self) -> None:
        self.assertEqual(True, False)

    def test__request(self) -> None:
        self.assertEqual(True, False)

    def test_get_all_applicable_experiments(self) -> None:
        self.assertEqual(True, False)

    def test_register_client(self) -> None:
        self.assertEqual(True, False)

    def test_mark_impact(self) -> None:
        self.assertEqual(True, False)

    def test_handle_experiments(self) -> None:
        self.assertEqual(True, False)

    def test_shutdown(self) -> None:
        self.assertEqual(True, False)
