"""Routines for Poetry."""

import re
from pathlib import Path
from typing import List, NamedTuple, Sequence, Tuple

import tomlkit
import tomlkit.container
import tomlkit.items

from .pypi import get_latest_version
from .update import FileContent, Update


def update_pyproject(filename: str) -> Tuple[Sequence[Update], FileContent]:
    """Check updates."""
    updates: List[Update] = []
    config, content = analyze_pyproject(filename)
    for p in config.packages:
        version = re.sub(r"^(?:\^|~|>=)", "", p.version)
        new_version = get_latest_version(p.name)
        if version != new_version:
            updates.append(
                Update(p.name, p.version, new_version, filename, p.category, None)
            )
    return (tuple(updates), content)


class PoetryConfigPackage(NamedTuple):
    """Package in pre-commit configurations."""

    name: str
    version: str
    category: str


class PoetryConfigStruct(NamedTuple):
    """Poetry configuration."""

    filename: str
    packages: Sequence[PoetryConfigPackage]


def analyze_pyproject(
    filename: str,
) -> Tuple[PoetryConfigStruct, FileContent]:
    """Analyze the given pre-commit config file."""
    # It seems that there is no TOML library that tracks line numbers...
    packages: List[PoetryConfigPackage] = []
    text = Path(filename).read_text()
    lines = tuple(text.splitlines())
    data = tomlkit.parse(text)

    if (
        "tool" in data
        and isinstance(
            data["tool"], (tomlkit.items.Table, tomlkit.container.OutOfOrderTableProxy)
        )
        and "poetry" in data["tool"]
        and isinstance(data["tool"]["poetry"], tomlkit.items.Table)
        and "dependencies" in data["tool"]["poetry"]
        and isinstance(data["tool"]["poetry"]["dependencies"], tomlkit.items.Table)
    ):
        deps = data["tool"]["poetry"]["dependencies"]
        packages += _parse_deps(deps, "tool.poetry.dependencies")

    if (
        "tool" in data
        and isinstance(
            data["tool"], (tomlkit.items.Table, tomlkit.container.OutOfOrderTableProxy)
        )
        and "poetry" in data["tool"]
        and isinstance(data["tool"]["poetry"], tomlkit.items.Table)
        and "dev-dependencies" in data["tool"]["poetry"]
        and isinstance(data["tool"]["poetry"]["dev-dependencies"], tomlkit.items.Table)
    ):
        deps = data["tool"]["poetry"]["dev-dependencies"]
        packages += _parse_deps(deps, "tool.poetry.dev-dependencies")

    return PoetryConfigStruct(filename, tuple(packages)), FileContent(filename, lines)


def _parse_deps(deps: tomlkit.items.Table, category: str) -> List[PoetryConfigPackage]:
    packages = []
    for d, v in deps.items():
        d = d.strip()
        if d.lower() == "python":
            continue
        if not isinstance(v, tomlkit.items.String):
            continue
        name = d
        version = str(v).strip()
        m = re.match(r"^((?:\^|~|>=)?)\s*(.*)$", version)
        if m:
            version = m.group(1) + m.group(2)
            package = PoetryConfigPackage(name, version, category)
            packages.append(package)
    return packages
