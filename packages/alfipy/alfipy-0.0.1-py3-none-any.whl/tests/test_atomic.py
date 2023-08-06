# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging

from alfipy.alfipy.AlfiConstants import logger_name
from alfipy.alfipy.Atomic import (
    Atomic,
    AtomicReference,
    AtomicBoolean,
    AtomicNumber,
    AtomicInteger,
    AtomicFloat,
    AtomicLong,
)

from .util import (
    test_value_bool,
    test_value_bool_2,
    test_value_num,
    test_value_num_2,
    test_value_str,
    test_value_str_2,
)

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestAtomic(unittest.TestCase):
    def test_atomic_reference_compare_and_set(self) -> None:
        helper: AtomicReference = AtomicReference(test_value_str)
        helper.compare_and_set("badvalue", test_value_str_2)
        self.assertNotEqual(helper.get(), test_value_str_2)
        helper.compare_and_set(test_value_str, test_value_str_2)
        self.assertEqual(helper.get(), test_value_str_2)

    def test_atomic_reference_get(self) -> None:
        helper = AtomicReference(test_value_str)
        self.assertEqual(test_value_str, helper.get())

    def test_atomic_reference_get_and_set(self) -> None:
        helper: AtomicReference = AtomicReference(test_value_str)
        self.assertEqual(helper.get_and_set(test_value_str_2), test_value_str)
        self.assertEqual(helper.get_and_set(test_value_str), test_value_str_2)
        self.assertEqual(test_value_str, helper.get())

    def test_atomic_reference_set(self) -> None:
        helper: AtomicReference = AtomicReference(test_value_str)
        self.assertEqual(test_value_str, helper.get())
        helper.set(test_value_str_2)
        self.assertEqual(test_value_str_2, helper.get())

    def test_atomic_boolean_get_and_set(self) -> None:
        helper: AtomicBoolean = AtomicBoolean(test_value_bool)
        self.assertEqual(
            helper.get_and_set(test_value_bool_2), test_value_bool
        )
        self.assertEqual(
            helper.get_and_set(test_value_bool), test_value_bool_2
        )
        self.assertEqual(test_value_bool, helper.get())

    def test_atomic_boolean_set(self) -> None:
        helper: AtomicBoolean = AtomicBoolean(test_value_bool)
        self.assertEqual(test_value_bool, helper.get())
        helper.set(test_value_bool_2)
        self.assertEqual(test_value_bool_2, helper.get())

    def test_atomic_number_add_and_get(self) -> None:
        helper = AtomicNumber(test_value_num)
        self.assertEqual(helper.get(), test_value_num)
        self.assertEqual(
            helper.add_and_get(test_value_num_2),
            test_value_num_2 + test_value_num,
        )
        self.assertEqual(helper.get(), test_value_num_2 + test_value_num)

    def test_atomic_number_get_and_add(self) -> None:
        helper = AtomicNumber(test_value_num)
        self.assertEqual(helper.get(), test_value_num)
        self.assertEqual(helper.get_and_add(test_value_num_2), test_value_num)
        self.assertEqual(helper.get(), test_value_num_2 + test_value_num)

    def test_atomic_number_get_and_subtract(self) -> None:
        helper = AtomicNumber(test_value_num)
        self.assertEqual(helper.get(), test_value_num)
        self.assertEqual(
            helper.get_and_subtract(test_value_num_2), test_value_num
        )
        self.assertEqual(helper.get(), test_value_num - test_value_num_2)

    def test_atomic_number_subtract_and_get(self) -> None:
        helper = AtomicNumber(test_value_num)
        self.assertEqual(helper.get(), test_value_num)
        self.assertEqual(
            helper.subtract_and_get(test_value_num_2),
            test_value_num - test_value_num_2,
        )
        self.assertEqual(helper.get(), test_value_num - test_value_num_2)
