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
from alfipy.alfipy.TypeProvider import TypeProvider

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestTypeProvider(unittest.TestCase):
    def test_register_type(self) -> None:
        self.assertEqual(True, False)

    def test_keys_for_type(self) -> None:
        self.assertEqual(True, False)

    def test_get_fields(self) -> None:
        self.assertEqual(True, False)

    def test_get_type(self) -> None:
        self.assertEqual(True, False)

    def test_create_model(self) -> None:
        self.assertEqual(True, False)

    def test_deserialize_model(self) -> None:
        self.assertEqual(True, False)

    def test_get_field_from_proto_entry(self) -> None:
        self.assertEqual(True, False)
