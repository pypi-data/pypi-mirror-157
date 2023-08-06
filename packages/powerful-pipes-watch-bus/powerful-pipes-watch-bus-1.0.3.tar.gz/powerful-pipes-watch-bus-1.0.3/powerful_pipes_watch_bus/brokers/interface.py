from __future__ import annotations

import abc

from typing import Iterator


class BusInterface(metaclass=abc.ABCMeta):

    @classmethod
    @abc.abstractmethod
    def open(cls, connection_string: str) -> BusInterface:
        raise NotImplementedError()

    @abc.abstractmethod
    def read_json_messages(self, queue_name: str) -> Iterator[dict]:
        raise NotImplementedError()

    @abc.abstractmethod
    def send_json_message(self, queue_name: str, data: dict):
        raise NotImplementedError()


__all__ = ("BusInterface", )
