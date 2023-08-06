"""Main routines."""

import argparse
import re
from pathlib import Path
from typing import Optional, Sequence, Tuple, Union

from . import poetry, pre_commit
from .update import FileContent, Update


def check_updates(
    path: Optional[Union[str, Path, Sequence[Union[str, Path]]]] = None
) -> Sequence[Tuple[Sequence[Update], FileContent]]:
    """Check updates."""
    if path is None:
        path = ["."]
    elif isinstance(path, (str, Path)):
        path = [path]

    exclude_dirs = [
        "__pycache__",
        "_build",
        "build",
        "CVS",
        "dist" "node_modules",
        "target",
        r"\..*",
    ]
    exclude_dirs = [f"^{s}$" for s in exclude_dirs]

    files = []

    def _search_files(f: Path) -> None:
        if f.is_dir():
            if any(re.match(e, f.name) for e in exclude_dirs):
                return
            for f1 in f.glob("*"):
                _search_files(f1)
        elif f.is_file():
            name_lower = f.name.lower()
            if name_lower in ("pyproject.toml", ".pre-commit-config.yaml"):
                files.append(f)

    for p in path:
        if isinstance(p, str):
            p = Path(p)
        _search_files(p)
    files = sorted(set(files))

    return tuple(_check_file(f) for f in files)


def _check_file(file: Union[str, Path]) -> Tuple[Sequence[Update], FileContent]:
    if isinstance(file, str):
        file = Path(file)
    name_lower = file.name.lower()

    if name_lower == "pyproject.toml":
        return poetry.update_pyproject(str(file))

    if name_lower == ".pre-commit-config.yaml":
        return pre_commit.update_pre_commit(str(file))

    return (), FileContent(str(file), file.read_text().splitlines())


def main(args: Optional[Sequence[Union[str, Path]]] = None) -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        prog="py-check-updates",
        usage=("%(prog)s [options] [--] [file/dir ...]"),
    )
    parser.add_argument("path", nargs="*", help=argparse.SUPPRESS)
    opts = parser.parse_args(args=[str(f) for f in args] if args is not None else None)

    is_first = True
    for updates, content in check_updates(opts.path if opts.path else None):
        if is_first:
            is_first = False
        else:
            print()

        if not updates:
            print(f"{content.name}: OK")
            continue
        else:
            print(f"{content.name}:")
            print()

        # Calculate column widths.

        w_name = 0
        w_version = 0
        w_new_version = 0
        w_category = 0
        w_line_number = 0

        for u in updates:
            w_name = max(w_name, len(u.name))
            w_version = max(w_version, len(u.version))
            w_new_version = max(w_new_version, len(u.new_version))
            if u.category:
                w_category = max(w_category, len(u.category))
            if u.line_number:
                w_line_number = max(w_line_number, len(str(u.line_number)))
        if w_category:
            w_category += 2
        if w_line_number:
            w_line_number += 5

        # Print the result.

        for u in updates:
            cat = f"[{u.category}]" if u.category else ""
            lineno = f"line:{u.line_number}" if u.line_number else ""
            s = ""
            if w_category:
                s += "  " + _str_with_minwidth(cat, w_category)
            if w_line_number:
                s += "  " + _str_with_minwidth(lineno, w_line_number)
            s += "  " + _str_with_minwidth(u.name, w_name)
            s += "  " + _str_with_minwidth(u.version, w_version)
            s += "  " + _str_with_minwidth(u.new_version, w_new_version)
            print("    " + s.strip())


def _str_with_minwidth(s: str, n: int) -> str:
    return s + " " * (n - len(s))
