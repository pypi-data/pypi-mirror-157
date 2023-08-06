# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

from .alfi_messages_pb2 import Client as ALFIMessages_Client

from .Coordinates import Coordinates

from dataclasses import dataclass, field


@dataclass
class Client:
    """
    Protobuff serialization/deserialization of `client` messages
    """

    coordinates: Coordinates
    identifier: str
    runtime: str
    runtime_version: str

    def to_message(self) -> ALFIMessages_Client:
        client = ALFIMessages_Client()
        client.identifier = self.identifier
        client.runtime = self.runtime
        client.runtimeVersion = self.runtime_version
        client.coordinates.CopyFrom(self.coordinates.to_message())
        return client
