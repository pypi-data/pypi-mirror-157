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
from alfipy.alfipy.GremlinService import GremlinService

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestGremlinService(unittest.TestCase):
    def test___new__(self) -> None:
        self.assertEqual(True, False)

    def test_try_inject_impact(self) -> None:
        self.assertEqual(True, False)

    def test_has_experiments(self) -> None:
        self.assertEqual(True, False)

    def test_get_experiment(self) -> None:
        self.assertEqual(True, False)

    def test_shutdown(self) -> None:
        self.assertEqual(True, False)

    def test_apply_impact(self) -> None:
        self.assertEqual(True, False)
