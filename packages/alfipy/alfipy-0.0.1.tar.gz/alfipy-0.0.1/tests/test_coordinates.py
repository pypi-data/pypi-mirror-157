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
from alfipy.alfipy.Coordinates import Coordinates

from .util import test_key, test_val

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestCoordinates(unittest.TestCase):
    def test_put_field_if_absent_to_message(self) -> None:
        helper = (
            Coordinates.Builder()
            .with_type("foo")
            .with_field("user", "kyle")
            .build()
        )
        helper.put_field_if_absent(test_key, test_val)
        expected_output = (
            'typed_alfi_model {\n  type: "foo"\n  fields {\n    key: "%s"\n    value {\n      element: "%s"\n    }\n  }\n  fields {\n    key: "user"\n    value {\n      element: "kyle"\n    }\n  }\n}\n'
            % (test_key, test_val)
        )
        self.assertEqual(str(helper.to_message()), expected_output)

    def test_field_to_message(self) -> None:
        helper = (
            Coordinates.Builder()
            .with_type("foo")
            .with_field("user", "kyle")
            .build()
        )
        helper.put_field(test_key, test_val)
        expected_output = 'element: "%s"\n' % test_val
        self.assertEqual(
            str(helper.field_to_message(test_key)), expected_output
        )
