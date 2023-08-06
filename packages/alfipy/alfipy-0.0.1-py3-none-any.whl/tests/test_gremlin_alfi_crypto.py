# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging
from datetime import datetime
from Crypto.PublicKey.ECC import EccKey

# import requests

from alfipy.alfipy.AlfiConstants import logger_name
from alfipy.alfipy.GremlinALFICrypto import GremlinALFICrypto

from .util import (
    cert_file,
    key_file,
    mock_teamid,
    mock_guid,
    test_value_str,
    mock_iso_timestamp,
)

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestGremlinALFICrypto(unittest.TestCase):
    def test_is_base64_encoded_certificate_or_private_key(self) -> None:
        self.assertTrue(
            GremlinALFICrypto.is_base64_encoded_certificate_or_private_key(
                cert_file
            )
        )
        self.assertFalse(
            GremlinALFICrypto.is_base64_encoded_certificate_or_private_key(
                cert_file + "error"
            )
        )

    def test__load_private_key(self) -> None:
        helper = GremlinALFICrypto._load_private_key(cert_file, key_file)
        expected_output_len = 281
        self.assertEqual(expected_output_len, len(str(helper)))
        self.assertTrue(isinstance(helper, EccKey))

    def test_build_signature(self) -> None:
        helper = GremlinALFICrypto.build_signature(
            mock_guid, cert_file, key_file
        )
        expected_output_len = 1500
        self.assertEqual(expected_output_len, len(helper))

    def test_sign_timestamp(self) -> None:
        helper = GremlinALFICrypto.sign_timestamp(
            mock_iso_timestamp, cert_file, key_file
        )
        expected_output_len = 1088
        self.assertEqual(len(helper), expected_output_len)

    def test_sign(self) -> None:
        helper_content = bytes(mock_iso_timestamp, GremlinALFICrypto.ENCODING)
        helper = GremlinALFICrypto.sign(helper_content, cert_file, key_file)
        expected_output_len = 1088
        self.assertEqual(len(helper), expected_output_len)
