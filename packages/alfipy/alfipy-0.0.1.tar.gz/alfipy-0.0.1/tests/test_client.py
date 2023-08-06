# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging
import base64

from alfipy.alfipy.AlfiConstants import logger_name
from alfipy.alfipy.Client import Client
from alfipy.alfipy.ApplicationCoordinates import ApplicationCoordinates

from .util import mock_identifier, mock_runtime, mock_runtime_version

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestClient(unittest.TestCase):
    def test_to_message(self) -> None:
        helper_coords = (
            ApplicationCoordinates.Builder()
            .with_type("test")
            .with_field("user", "kyle")
            .build()
        )
        helper = Client(
            helper_coords, mock_identifier, mock_runtime, mock_runtime_version
        )
        expected_output = 'coordinates {\n  coordinates {\n    typed_alfi_model {\n      type: "test"\n      fields {\n        key: "user"\n        value {\n          element: "kyle"\n        }\n      }\n    }\n  }\n}\nidentifier: "aMockIdentifier"\nruntime: "a mock runtime"\nruntimeVersion: "mocking version 11"\n'
        self.assertEqual(str(helper.to_message()), expected_output)
