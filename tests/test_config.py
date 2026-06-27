from pathlib import Path

import pytest

from python_dependency_linter.core.config import find_config, load_config

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_yaml_config():
    config = load_config(FIXTURES / "sample_config.yaml")
    assert len(config.rules) == 2

    rule = config.rules[0]
    assert rule.name == "domain-isolation"
    assert rule.modules == "contexts.*.domain"
    assert rule.description is None
    assert rule.allow is not None
    assert rule.allow.standard_library == ["dataclasses", "typing"]
    assert rule.allow.third_party == ["pydantic"]
    assert rule.allow.local == ["contexts.*.domain"]
    assert rule.deny is None


def test_load_yaml_config_deny():
    config = load_config(FIXTURES / "sample_config.yaml")
    rule = config.rules[1]
    assert rule.name == "adapters-deny-boto"
    assert rule.deny is not None
    assert rule.deny.third_party == ["boto3"]
    assert rule.allow is None


def test_load_pyproject_toml():
    config = load_config(FIXTURES / "sample_pyproject.toml")
    assert len(config.rules) == 1

    rule = config.rules[0]
    assert rule.name == "domain-isolation"
    assert rule.modules == "contexts.*.domain"
    assert rule.allow is not None
    assert rule.allow.standard_library == ["dataclasses", "typing"]


def test_load_yaml_config_with_include_exclude(tmp_path):
    config_content = """\
include:
  - src/**
exclude:
  - src/generated/**
rules:
  - name: test
    modules: src.*
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    config = load_config(config_file)
    assert config.include == ["src/**"]
    assert config.exclude == ["src/generated/**"]


def test_load_yaml_config_without_include_exclude():
    config = load_config(FIXTURES / "sample_config.yaml")
    assert config.include is None
    assert config.exclude is None


def test_load_pyproject_toml_with_include_exclude(tmp_path):
    config_content = """\
[tool.python-dependency-linter]
include = ["src/**"]
exclude = ["src/generated/**"]

[[tool.python-dependency-linter.rules]]
name = "test"
modules = "src.*"
"""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(config_content)
    config = load_config(config_file)
    assert config.include == ["src/**"]
    assert config.exclude == ["src/generated/**"]


def test_load_config_file_not_found():
    import pytest

    with pytest.raises(FileNotFoundError):
        load_config(Path("nonexistent.yaml"))


def test_find_config_yaml_in_cwd(tmp_path, monkeypatch):
    (tmp_path / ".python-dependency-linter.yaml").write_text("rules: []\n")
    monkeypatch.chdir(tmp_path)
    assert find_config() == tmp_path / ".python-dependency-linter.yaml"


def test_find_config_yaml_in_parent(tmp_path, monkeypatch):
    (tmp_path / ".python-dependency-linter.yaml").write_text("rules: []\n")
    child = tmp_path / "sub"
    child.mkdir()
    monkeypatch.chdir(child)
    assert find_config() == tmp_path / ".python-dependency-linter.yaml"


def test_find_config_pyproject_toml(tmp_path, monkeypatch):
    toml_content = "[tool.python-dependency-linter]\nrules = []\n"
    (tmp_path / "pyproject.toml").write_text(toml_content)
    monkeypatch.chdir(tmp_path)
    assert find_config() == tmp_path / "pyproject.toml"


def test_find_config_yaml_preferred_over_toml(tmp_path, monkeypatch):
    """When both exist in the same directory, YAML wins."""
    (tmp_path / ".python-dependency-linter.yaml").write_text("rules: []\n")
    toml_content = "[tool.python-dependency-linter]\nrules = []\n"
    (tmp_path / "pyproject.toml").write_text(toml_content)
    monkeypatch.chdir(tmp_path)
    assert find_config() == tmp_path / ".python-dependency-linter.yaml"


def test_find_config_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = find_config()
    assert result is None


def test_find_config_skips_pyproject_without_section(tmp_path, monkeypatch):
    """pyproject.toml without [tool.python-dependency-linter] should be skipped."""
    (tmp_path / "pyproject.toml").write_text("[tool.other]\nfoo = 1\n")
    monkeypatch.chdir(tmp_path)
    assert find_config() is None


def test_valid_rule_names(tmp_path):
    config_content = """\
rules:
  - name: attribute-matches-type
    modules: src.*
  - name: bool_method
    modules: src.*
  - name: rule1
    modules: src.*
  - name: shared.domain
    modules: src.*
  - name: context.adapters.inbound
    modules: src.*
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    config = load_config(config_file)
    assert len(config.rules) == 5


def test_invalid_rule_name_with_space(tmp_path):
    config_content = """\
rules:
  - name: "my rule"
    modules: src.*
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    with pytest.raises(ValueError, match=r"Invalid rule name 'my rule'"):
        load_config(config_file)


def test_invalid_rule_name_with_special_char(tmp_path):
    config_content = """\
rules:
  - name: "rule!name"
    modules: src.*
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    with pytest.raises(ValueError, match=r"Invalid rule name 'rule!name'"):
        load_config(config_file)


def test_invalid_rule_name_with_mixed(tmp_path):
    config_content = """\
rules:
  - name: "rule name 123"
    modules: src.*
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    with pytest.raises(ValueError, match=r"Invalid rule name 'rule name 123'"):
        load_config(config_file)


def test_load_yaml_config_with_description(tmp_path):
    config_content = """\
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    description: Domain layer must remain pure
    allow:
      third_party: [pydantic]
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    config = load_config(config_file)
    assert config.rules[0].description == "Domain layer must remain pure"


def test_load_yaml_config_without_description(tmp_path):
    config_content = """\
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    allow:
      third_party: [pydantic]
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    config = load_config(config_file)
    assert config.rules[0].description is None


def test_load_toml_config_with_description(tmp_path):
    config_content = """\
[tool.python-dependency-linter]

[[tool.python-dependency-linter.rules]]
name = "domain-isolation"
modules = "contexts.*.domain"
description = "Domain layer must remain pure"

[tool.python-dependency-linter.rules.allow]
third_party = ["pydantic"]
"""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(config_content)
    config = load_config(config_file)
    assert config.rules[0].description == "Domain layer must remain pure"
