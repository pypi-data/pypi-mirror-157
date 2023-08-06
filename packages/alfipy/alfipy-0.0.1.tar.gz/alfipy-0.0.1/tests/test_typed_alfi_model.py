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
from alfipy.alfipy.TypedAlfiModel import TypedAlfiModel

from .util import test_key, test_val

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestTypedAlfiModel(unittest.TestCase):
    def test_get_or_default(self) -> None:
        helper_t = TypedAlfiModel.Type(str, [test_key])
        helper = TypedAlfiModel(str, {test_key: test_val})
        self.assertEqual(True, False)

    # def test_get_field(self) -> None:
    #     self.assertEqual(True, False)

    # def test_get_fields(self) -> None:
    #     self.assertEqual(True, False)

    # def test_to_message(self) -> None:
    #     self.assertEqual(True, False)

    # def test_field_to_message(self) -> None:
    #     self.assertEqual(True, False)

    # def test_populate_proto_builder(self) -> None:
    #     self.assertEqual(True, False)

    # def test___eq__(self) -> None:
    #     self.assertEqual(True, False)

    # def test___hash__(self) -> None:
    #     self.assertEqual(True, False)
