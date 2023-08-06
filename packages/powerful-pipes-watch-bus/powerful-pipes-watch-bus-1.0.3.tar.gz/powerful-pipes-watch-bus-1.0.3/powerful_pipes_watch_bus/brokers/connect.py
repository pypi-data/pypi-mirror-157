from __future__ import annotations

from .redis import RedisBus
from .interface import BusInterface
from ..exceptions import WatchBusException

def connect_bus(connection_string: str) -> BusInterface:

    if connection_string.startswith("redis://"):
        return RedisBus.open(connection_string)

    else:
        raise WatchBusException("Invalid connection string URI")

__all__ = ("connect_bus", )
