"""Routines for pre-commit."""

from __future__ import annotations

import functools
import re
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

import requests
import yaml

from .pypi import get_latest_version
from .update import FileContent, Update


def update_pre_commit(filename: str) -> Tuple[Sequence[Update], FileContent]:
    """Check updates."""
    updates: List[Update] = []
    config, content = analyze_pre_commit_config(filename)
    for p in config.packages:
        if p.language == "python":
            new_version = get_latest_version(p.name)
        else:
            raise ValueError(
                "language not implemented for additional_dependencies: " f"{p.language}"
            )
        if p.version != new_version:
            updates.append(
                Update(p.name, p.version, new_version, filename, None, p.line_number)
            )

    return (tuple(updates), content)


class PreCommitConfigPackage(NamedTuple):
    """Package in pre-commit configurations."""

    name: str
    version: str
    language: str
    filename: str
    line_number: int


class PreCommitConfigStruct(NamedTuple):
    """Pre-commit configuration."""

    filename: str
    packages: Sequence[PreCommitConfigPackage]


def analyze_pre_commit_config(
    filename: str,
) -> Tuple[PreCommitConfigStruct, FileContent]:
    """Analyze the given pre-commit config file."""
    text = Path(filename).read_text()
    lines = tuple(text.splitlines())
    root_node: yaml.Node = yaml.compose(text)  # type: ignore[no-untyped-call]
    packages: List[PreCommitConfigPackage] = []

    if isinstance(root_node, yaml.MappingNode):
        for root_node_key, root_node_value in root_node.value:
            if (
                isinstance(root_node_key, yaml.ScalarNode)
                and root_node_key.value == "repos"
                and isinstance(root_node_value, yaml.SequenceNode)
            ):
                for repo_node in root_node_value.value:
                    if isinstance(repo_node, yaml.MappingNode):
                        name: Optional[str] = None
                        rev: Optional[str] = None
                        hooks: Optional[List[yaml.Node]] = None
                        for repo_node_key, repo_node_value in repo_node.value:
                            if (
                                isinstance(repo_node_key, yaml.ScalarNode)
                                and repo_node_key.value == "repo"
                                and isinstance(repo_node_value, yaml.ScalarNode)
                            ):
                                name = repo_node_value.value
                            elif (
                                isinstance(repo_node_key, yaml.ScalarNode)
                                and repo_node_key.value == "rev"
                                and isinstance(repo_node_value, yaml.ScalarNode)
                            ):
                                rev = repo_node_value.value
                            elif (
                                isinstance(repo_node_key, yaml.ScalarNode)
                                and repo_node_key.value == "hooks"
                                and isinstance(repo_node_value, yaml.SequenceNode)
                            ):
                                hooks = repo_node_value.value
                        if name and rev and hooks:
                            languages = analyze_pre_commit_hooks(name, rev)
                            for h in hooks:
                                packages += _parse_hook(h, filename, languages)

    return PreCommitConfigStruct(filename, tuple(packages)), FileContent(
        filename, lines
    )


def _parse_hook(
    hook: yaml.Node, filename: str, languages: PreCommitHooksStruct
) -> List[PreCommitConfigPackage]:
    packages = []
    if isinstance(hook, yaml.MappingNode):
        hook_language: Optional[str] = None
        additional_dependencies: Optional[List[yaml.Node]] = None
        for key, value in hook.value:
            if (
                isinstance(key, yaml.ScalarNode)
                and key.value == "id"
                and isinstance(value, yaml.ScalarNode)
            ):
                hook_id = value.value
                hook_language = languages.languages[hook_id]
            elif (
                isinstance(key, yaml.ScalarNode)
                and key.value == "additional_dependencies"
                and isinstance(value, yaml.SequenceNode)
            ):
                additional_dependencies = value.value
        if hook_language and additional_dependencies:
            for dep_node in additional_dependencies:
                if isinstance(dep_node, yaml.ScalarNode):
                    dep_str = dep_node.value
                    if hook_language == "python":
                        m = re.match(r"^(.*)==(.*)$", dep_str)
                        if m:
                            dep_name = m.group(1).strip()
                            dep_ver = m.group(2).strip()
                            package = PreCommitConfigPackage(
                                dep_name,
                                dep_ver,
                                hook_language,
                                filename,
                                dep_node.start_mark.line + 1,
                            )
                            packages.append(package)
                    else:
                        # Ignore other languages for now.
                        pass
    return packages


HookId = str
HookLanguage = str


class PreCommitHooksStruct(NamedTuple):
    """Pre-commit hooks."""

    name: str
    rev: str
    languages: Dict[HookId, HookLanguage]


@functools.lru_cache(maxsize=None)
def analyze_pre_commit_hooks(name: str, rev: str) -> PreCommitHooksStruct:
    """Analyze the given pre-commit hooks on GitHub."""
    languages = {}
    data = yaml.load(_get_pre_commit_hook_impl(name, rev), Loader=yaml.SafeLoader)
    if isinstance(data, list):
        for d in data:
            if isinstance(d, dict):
                if "id" in d and "language" in d:
                    hook_id = d["id"]
                    hook_language = d["language"]
                    if isinstance(hook_id, str) and isinstance(hook_language, str):
                        languages[hook_id] = hook_language

    return PreCommitHooksStruct(name, rev, languages)


def _get_pre_commit_hook_impl(name: str, rev: str) -> str:
    github_prefix = "https://github.com/"
    if name.lower().startswith(github_prefix):
        url = f"https://raw.githubusercontent.com/{name[len(github_prefix):]}/{rev}"
    else:
        return ""

    r = requests.get(f"{url}/.pre-commit-hooks.yaml")
    return r.text
