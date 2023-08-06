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
from alfipy.alfipy.QueryField import QueryField
from alfipy.alfipy.ExactField import ExactField
from alfipy.alfipy.WildcardField import WildcardField
from alfipy.alfipy.alfi_messages_pb2 import Field as ALFIMessages_Field
from alfipy.alfipy.alfi_messages_pb2 import WildcardField as ALFI_WildcardField
from alfipy.alfipy.alfi_messages_pb2 import ExactField as ALFI_ExactField

from .util import test_value_str, test_key

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestQueryField(unittest.TestCase):
    def test_specific(self) -> None:
        helper = ExactField(data=test_value_str)
        self.assertEqual(QueryField.specific(test_value_str), helper)

    def test_any(self) -> None:
        helper = WildcardField()
        self.assertEqual(QueryField.any(), helper)

    def test_from_message(self) -> None:
        helper_wf = WildcardField()
        helper_ef = ExactField(data="")
        test_input = ALFIMessages_Field(
            query={
                "wildcard_field": ALFI_WildcardField(),
            }
        )
        self.assertEqual(QueryField.from_message(test_input), helper_wf)
        test_input = ALFIMessages_Field(
            query={
                "exact_field": ALFI_ExactField(),
            }
        )
        self.assertEqual(QueryField.from_message(test_input), helper_ef)
