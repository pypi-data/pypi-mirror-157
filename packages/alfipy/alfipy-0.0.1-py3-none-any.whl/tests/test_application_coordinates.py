# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging

from alfipy.alfipy.AlfiConstants import logger_name
from alfipy.alfipy.ApplicationCoordinates import ApplicationCoordinates

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestApplicationCoordinates(unittest.TestCase):
    def test_to_message(self) -> None:
        helper = (
            ApplicationCoordinates.Builder()
            .with_type("test")
            .with_field("user", "kyle")
            .build()
        )
        expected_output = b'coordinates {\n  typed_alfi_model {\n    type: "test"\n    fields {\n      key: "user"\n      value {\n        element: "kyle"\n      }\n    }\n  }\n}\n'
        self.assertEqual(
            expected_output, str(helper.to_message()).encode("utf-8")
        )
