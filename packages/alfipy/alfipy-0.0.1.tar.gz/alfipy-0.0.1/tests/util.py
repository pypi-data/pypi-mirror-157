# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import struct
import os

from alfipy.alfipy.Impact import Impact
from alfipy.alfipy.TrafficQuery import TrafficQuery
from alfipy.alfipy.alfi_messages_pb2 import (
    ExperimentResponseList as ALFIMessages_ExperimentResponseList,
)
from alfipy.alfipy.ExperimentImpact import ExperimentImpact
from alfipy.alfipy.ImpactType import ImpactType
from alfipy.alfipy.Impact import Impact

mock_data = {"testkey": "testval"}
mock_experiments = [128]


def mock_experiments_resp():
    return ExperimentImpact(
        experiment_guid="0dffcda1-0ae7-4b6a-bfcd-a10ae78b6a41",
        impact=Impact(
            type=ImpactType(name="", keys=None),
            fields={
                "exception_should_be_thrown": True,
                "latency_to_add_in_ms": 300.0,
            },
        ),
        impact_provider=ImpactProvider(query_keys={}),
    )


def mock_json():
    return mock_data


cert_file = os.getenv("GREMLIN_TEAM_CERTIFICATE_OR_FILE", None)
key_file = os.getenv("GREMLIN_TEAM_PRIVATE_KEY_OR_FILE", None)

test_value_str = "1234567890a"
test_value_str_2 = "anotherdifferenttesvalue"
test_value_bool = True
test_value_bool_2 = False
test_value_num = 42
test_value_num_2 = 24
test_retries = 42
test_len = 24
test_latency = 300.0
test_endpoint = "www.example.com"
test_version = "v1.2.3.4"

mock_iso_timestamp = "2021-05-07T20:17:33.112344"
mock_identifier = "aMockIdentifier"
mock_runtime = "a mock runtime"
mock_runtime_version = "mocking version 11"
mock_guid = "0dffcda1-0ae7-4b6a-bfcd-a10ae78b6a41"
mock_teamid = "jn45-dfjn-34576"
mock_query = TrafficQuery()
mock_impact = Impact()
mock_struct = struct.pack("5s i", b"string", 1234)
mock_data = {"testkey": "testval"}
mock_list = ["item1", "item two", "another item"]
mock_header = {"auth": "123yg34256iuh"}


def mock_json():
    return mock_data


def mock_headers():
    return mock_header


test_key = "testkey"
test_val = "a test value"
