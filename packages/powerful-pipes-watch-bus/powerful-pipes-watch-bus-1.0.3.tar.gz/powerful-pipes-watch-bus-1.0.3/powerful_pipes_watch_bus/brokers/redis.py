from __future__ import annotations

from typing import Iterator
from urllib.parse import urlparse, parse_qsl

import orjson
import redis

from powerful_pipes import read_json

from .interface import BusInterface


class RedisBus(BusInterface):

    def __init__(self, connection):
        self._connection: redis.Redis = connection

    def read_json_messages(self, queue_name: str) -> Iterator[dict]:

        while True:
            try:
                queue_name, message = self._connection.blpop(queue_name)
            except KeyboardInterrupt:
                return

            except:
                continue

            if message == "QUIT":
                break

            yield read_json(message)

    def send_json_message(self, queue_name: str, data: dict):
        self._connection.rpush(queue_name, orjson.dumps(data))


    @classmethod
    def open(cls, connection_string: str) -> RedisBus:
        parsed = urlparse(connection_string)

        query = dict(parse_qsl(parsed.query))

        port = parsed.port or 6379
        host = parsed.hostname or "localhost"
        db = query.get("db", 0)

        o = cls(
            redis.Redis(host, port, db)
        )

        return o
