from pathlib import Path

from python_dependency_linter.config import load_config

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_yaml_config():
    config = load_config(FIXTURES / "sample_config.yaml")
    assert len(config.rules) == 2

    rule = config.rules[0]
    assert rule.name == "domain-isolation"
    assert rule.modules == "contexts.*.domain"
    assert rule.allow.standard_library == ["dataclasses", "typing"]
    assert rule.allow.third_party == ["pydantic"]
    assert rule.allow.local == ["contexts.*.domain"]
    assert rule.deny is None


def test_load_yaml_config_deny():
    config = load_config(FIXTURES / "sample_config.yaml")
    rule = config.rules[1]
    assert rule.name == "adapters-deny-boto"
    assert rule.deny.third_party == ["boto3"]
    assert rule.allow is None


def test_load_pyproject_toml():
    config = load_config(FIXTURES / "sample_pyproject.toml")
    assert len(config.rules) == 1

    rule = config.rules[0]
    assert rule.name == "domain-isolation"
    assert rule.modules == "contexts.*.domain"
    assert rule.allow.standard_library == ["dataclasses", "typing"]


def test_load_config_file_not_found():
    import pytest

    with pytest.raises(FileNotFoundError):
        load_config(Path("nonexistent.yaml"))
