# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging
from time import monotonic, sleep, time_ns
import timeit
from datetime import datetime

from alfipy.alfipy.AlfiConstants import logger_name
from alfipy.alfipy.GremlinTime import GremlinTime, SystemTime

from .util import mock_json

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestGremlinTime(unittest.TestCase):
    # GremlinTime
    def test_gremlintime_measure_execution_time(self) -> None:
        helper = GremlinTime.measure_execution_time(mock_json)()
        self.assertEqual(mock_json(), helper)

    # # SystemTime
    def test_systemtime_advance_millis(self) -> None:
        num_millis = 100

        def wrap_test():
            return SystemTime.advance_millis(num_millis)

        helper = timeit.timeit(stmt=wrap_test, number=1)
        self.assertGreaterEqual(helper, num_millis / 1000)

    def test_systemtime_get_current_time_in_ms(self) -> None:
        expected_output = datetime.utcnow().timestamp() * 1000
        self.assertGreaterEqual(
            SystemTime.get_current_time_in_ms(), expected_output
        )

    def test_systemtime_get_current_time_in_ns(self) -> None:
        expected_output = time_ns()
        self.assertGreaterEqual(
            SystemTime.get_current_time_in_ns(), expected_output
        )
