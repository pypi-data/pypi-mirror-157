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
from alfipy.alfipy.GremlinApiRequestsClient import GremlinApiRequestsClient

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestGremlinApiRequestsClient(unittest.TestCase):
    def test__initialize_conn(self) -> None:
        self.assertEqual(True, False)

    def test__request(self) -> None:
        self.assertEqual(True, False)

    def test_shutdown(sself) -> None:
        self.assertEqual(True, False)
