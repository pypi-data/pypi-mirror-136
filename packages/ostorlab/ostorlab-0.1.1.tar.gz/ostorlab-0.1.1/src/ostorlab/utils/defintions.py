"""Common definition types."""
import dataclasses
from typing import Optional


@dataclasses.dataclass
class Arg:
    """Data class holding a definition.

    The value is always bytes to support all arg values. The type is defined by the type attribute."""
    name: str
    type: str
    value: Optional[bytes] = None
    description: Optional[str] = None


@dataclasses.dataclass
class PortMapping:
    """Data class defining a port mapping source to destination"""
    source_port: int
    destination_port: int
