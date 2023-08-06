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
from alfipy.alfipy.QueryTypeProvider import QueryTypeProvider
from alfipy.alfipy.ExactField import ExactField
from alfipy.alfipy.WildcardField import WildcardField
from alfipy.alfipy.alfi_messages_pb2 import WildcardField as ALFI_WildcardField
from alfipy.alfipy.alfi_messages_pb2 import ExactField as ALFI_ExactField
from alfipy.alfipy.alfi_messages_pb2 import Field as ALFIMessages_Field

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestQueryTypeProvider(unittest.TestCase):
    def test_get_field_from_proto_entry(self) -> None:
        self.assertEqual(True, False)

    def test_get_percentage_to_impact(self) -> None:
        self.assertEqual(True, False)
