# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import threading

from .GremlinTime import SystemTime

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class BoundedConcurrentSet(Generic[T]):
    """
    This is the heart of the data structure - it follows the following algorithm
        - If the object *is* already in the set, immediately return
        - If the object *is not* already in the set, check how many items are present
            - If size not yet to capacity, add the object to the set
            - If size==capacity, evict the oldest object

    Determining oldest takes O(log n) when using :ref:`Collections.OrderedDict`.
    Since the `Key` is :ref:`SystemTime.get_current_time_in_ns()`, this gives us oldest first.
    Contains takes O(log n) since it's implemented against the :ref:`OrderedDict`

    Finally, we need this method to by synchronized and thread-safe to ensure that the `insertion_timestamp`
    and `objects` remain in sync.
    """

    capacity: int = 128
    insertion_timestamps: OrderedDict = field(default_factory=OrderedDict)
    objects: list = field(default_factory=list)

    def __post_init__(self):
        self._lock = threading.Lock()

    def add(self, t: T) -> None:
        with self._lock:
            if not self.contains(t):
                if self.size() == self.capacity:
                    (oe_k, oe_v) = self.insertion_timestamps.popitem(last=False)
                    self.objects.remove(oe_v)
                ts = SystemTime.get_current_time_in_ns()
                self.insertion_timestamps[ts] = t
                self.objects.append(t)

    def contains(self, t: T) -> bool:
        return t in self.objects

    def size(self) -> int:
        return len(self.objects)
