from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class AllowDeny:
    standard_library: list[str] | None = None
    third_party: list[str] | None = None
    local: list[str] | None = None


@dataclass
class Rule:
    name: str
    modules: str
    allow: AllowDeny | None = None
    deny: AllowDeny | None = None


@dataclass
class Config:
    rules: list[Rule]
    include: list[str] | None = None
    exclude: list[str] | None = None


def _parse_allow_deny(data: dict | None) -> AllowDeny | None:
    if data is None:
        return None
    return AllowDeny(
        standard_library=data.get("standard_library"),
        third_party=data.get("third_party"),
        local=data.get("local"),
    )


def _parse_rules(rules_data: list[dict]) -> list[Rule]:
    rules = []
    for r in rules_data:
        rules.append(
            Rule(
                name=r["name"],
                modules=r["modules"],
                allow=_parse_allow_deny(r.get("allow")),
                deny=_parse_allow_deny(r.get("deny")),
            )
        )
    return rules


def _load_yaml(path: Path) -> Config:
    with open(path) as f:
        data = yaml.safe_load(f)
    return Config(
        rules=_parse_rules(data["rules"]),
        include=data.get("include"),
        exclude=data.get("exclude"),
    )


def _load_pyproject_toml(path: Path) -> Config:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]

    with open(path, "rb") as f:
        data = tomllib.load(f)
    tool_config = data["tool"]["python-dependency-linter"]
    return Config(
        rules=_parse_rules(tool_config["rules"]),
        include=tool_config.get("include"),
        exclude=tool_config.get("exclude"),
    )


def load_config(path: Path) -> Config:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    if path.suffix == ".toml":
        return _load_pyproject_toml(path)
    return _load_yaml(path)
