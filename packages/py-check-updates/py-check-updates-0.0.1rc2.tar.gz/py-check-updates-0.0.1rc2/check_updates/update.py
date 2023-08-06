"""Update information."""

from typing import NamedTuple, Optional, Sequence


class FileContent(NamedTuple):
    """File content."""

    name: str
    lines: Sequence[str]


class Update(NamedTuple):
    """Update information."""

    name: str
    version: str
    new_version: str
    filename: str
    category: Optional[str]
    line_number: Optional[int]
