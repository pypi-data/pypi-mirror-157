# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging
import base64
import hashlib
import datetime

# import requests

from alfipy.alfipy.AlfiConstants import logger_name, FILE_PREFIX

from alfipy.alfipy.AlfiConfigFromCertificateAndPrivateKey import (
    AlfiConfigFromCertificateAndPrivateKey,
)

from .util import cert_file, key_file

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestAlfiConfigFromCertificateAndPrivateKey(unittest.TestCase):
    def test_auth_header_value(self) -> None:
        helper = AlfiConfigFromCertificateAndPrivateKey(
            raw_certificate_or_reference=cert_file,
            raw_private_key_or_reference=key_file,
        )
        helper.gremlin_team_id = "1234"
        helper._certificate = cert_file
        helper._private_key = key_file
        expected_output_len = 1465
        self.assertEqual(expected_output_len, len(helper.auth_header_value))

    def test_resolve_certificate(self) -> None:
        helper = AlfiConfigFromCertificateAndPrivateKey(
            raw_certificate_or_reference=cert_file,
            raw_private_key_or_reference=key_file,
        )
        expected_output_len = 630
        self.assertEqual(
            expected_output_len,
            len(helper.resolve_certificate(cert_file)),
        )

    def test_resolve_private_key(self) -> None:
        helper = AlfiConfigFromCertificateAndPrivateKey(
            raw_certificate_or_reference=cert_file,
            raw_private_key_or_reference=key_file,
        )
        expected_output_len = 226
        self.assertEqual(
            expected_output_len,
            len(helper.resolve_private_key(key_file)),
        )
