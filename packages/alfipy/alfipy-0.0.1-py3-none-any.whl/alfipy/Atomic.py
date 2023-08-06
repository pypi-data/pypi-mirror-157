# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import threading

from abc import abstractmethod, ABCMeta
from dataclasses import dataclass, field

from typing import Generic, TypeVar

long = TypeVar("long", bound=int)


@dataclass
class Atomic(metaclass=ABCMeta):
    """
    Establishes a thread-safe RW interface for object storage
    """

    value: object = field(default=None)

    def __post_init__(self):
        self._lock = threading.Lock()

    @abstractmethod
    def compare_and_set(self, expect: object, update: object) -> bool:
        """
        Set the value to `update` if the current `value` is `expect`

        :param expect:
        :param update:
        :return:
        """
        raise NotImplementedError(
            "This method needs to be implemented in a subclass"
        )

    @abstractmethod
    def get(self) -> object:
        """
        Return the contained object or value

        :return:
        """
        raise NotImplementedError(
            "This method needs to be implemented in a subclass"
        )

    @abstractmethod
    def get_and_set(self, value: object) -> object:
        """
        Automatically sets the value to `value` and returns the old value.

        :param value:
        :return:
        """
        raise NotImplementedError(
            "This method needs to be implemented in a subclass"
        )

    @abstractmethod
    def set(self, value: object) -> object:
        """
        Sets the value to `value`, returns the new `value`

        :param value:
        :return:
        """
        raise NotImplementedError(
            "This method needs to be implemented in a subclass"
        )


@dataclass
class AtomicReference(Atomic):
    value: object = field(default=None)

    def compare_and_set(self, expect: object, update: object) -> bool:
        with self._lock:
            if self.value == expect:
                self.value = update
                return True
            return False

    def get(self) -> object:
        with self._lock:
            return self.value

    def get_and_set(self, value: object) -> object:
        with self._lock:
            ov = self.value
            self.value = value
            return ov

    def set(self, value: object) -> object:
        with self._lock:
            self.value = value
            return self.value


@dataclass
class AtomicBoolean(AtomicReference):
    value: bool = field(default=False)

    def get_and_set(self, value: bool) -> bool:
        return super().get_and_set(bool(value))

    def set(self, value: bool) -> bool:
        super().set(bool(value))


@dataclass
class AtomicNumber(AtomicReference):
    value: int = field(default=0)

    def add_and_get(self, delta: int) -> int:
        with self._lock:
            self.value += delta
            return self.value

    def get_and_add(self, delta: int) -> int:
        with self._lock:
            ov = self.value
            self.value += delta
            return ov

    def get_and_subtract(self, delta: int) -> int:
        with self._lock:
            ov = self.value
            self.value -= delta
            return ov

    def subtract_and_get(self, delta: int) -> int:
        with self._lock:
            self.value -= delta
            return self.value


@dataclass
class AtomicInteger(AtomicNumber):
    value: int = field(default=0)


@dataclass
class AtomicLong(AtomicNumber, Generic[long]):
    value: long = field(default=0)


@dataclass
class AtomicFloat(AtomicNumber):
    value: float = field(default=0.0)
