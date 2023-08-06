# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging

from alfipy.alfipy.AlfiConstants import logger_name
from alfipy.alfipy.BoundedConcurrentSet import BoundedConcurrentSet

from .util import test_value_str, test_value_str_2

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestBoundedConcurrentSet(unittest.TestCase):
    def test_add_contains_size(self) -> None:
        helper = BoundedConcurrentSet()
        helper.add(test_value_str)
        self.assertTrue(helper.contains(test_value_str))
        self.assertEqual(1, helper.size())
        for i in range(helper.capacity - 1):
            to_add = str(i) + test_value_str_2
            helper.add(to_add)
            self.assertTrue(helper.contains(test_value_str))
        helper.add("another string to add, that pushes the oldest value off")
        self.assertFalse(helper.contains(test_value_str))
        self.assertEqual(helper.capacity, helper.size())
