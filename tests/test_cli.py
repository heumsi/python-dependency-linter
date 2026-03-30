from pathlib import Path

from click.testing import CliRunner

from python_dependency_linter.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_check_with_violations(tmp_path, monkeypatch):
    config_content = """\
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    allow:
      standard_library: [dataclasses, typing]
      third_party: [pydantic]
      local: [contexts.*.domain]
"""
    config_file = tmp_path / ".python-dependency-linter.yaml"
    config_file.write_text(config_content)

    # Copy sample project to tmp_path
    import shutil

    src = FIXTURES / "sample_project" / "contexts"
    dst = tmp_path / "contexts"
    shutil.copytree(src, dst)

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["check"])
    assert result.exit_code == 1
    assert "[domain-isolation]" in result.output
    assert "Found" in result.output


def test_cli_check_no_violations(tmp_path, monkeypatch):
    config_content = """\
rules:
  - name: allow-all
    modules: contexts.*.domain
    allow:
      standard_library: ["*"]
      third_party: ["*"]
      local: ["*"]
"""
    config_file = tmp_path / ".python-dependency-linter.yaml"
    config_file.write_text(config_content)

    import shutil

    src = FIXTURES / "sample_project" / "contexts"
    dst = tmp_path / "contexts"
    shutil.copytree(src, dst)

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["check"])
    assert result.exit_code == 0
    assert "No violations found." in result.output


def test_cli_check_with_include(tmp_path, monkeypatch):
    """Files outside include paths should be skipped."""
    config_content = """\
include:
  - src
rules:
  - name: domain-isolation
    modules: "**"
    deny:
      third_party: [pydantic]
"""
    config_file = tmp_path / ".python-dependency-linter.yaml"
    config_file.write_text(config_content)

    # Create files inside and outside include path
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    (src / "app.py").write_text("import pydantic\n")

    other = tmp_path / "other"
    other.mkdir()
    (other / "__init__.py").write_text("")
    (other / "app.py").write_text("import pydantic\n")

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["check"])
    assert result.exit_code == 1
    assert "src/app.py" in result.output
    assert "other/app.py" not in result.output


def test_cli_check_with_exclude(tmp_path, monkeypatch):
    """Files matching exclude patterns should be skipped."""
    config_content = """\
exclude:
  - generated/**
rules:
  - name: domain-isolation
    modules: "**"
    deny:
      third_party: [pydantic]
"""
    config_file = tmp_path / ".python-dependency-linter.yaml"
    config_file.write_text(config_content)

    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    (src / "app.py").write_text("import pydantic\n")

    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "__init__.py").write_text("")
    (generated / "models.py").write_text("import pydantic\n")

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["check"])
    assert result.exit_code == 1
    assert "src/app.py" in result.output
    assert "generated/" not in result.output


def test_cli_check_with_include_and_exclude(tmp_path, monkeypatch):
    """Exclude should filter within included paths."""
    config_content = """\
include:
  - src
exclude:
  - src/generated
rules:
  - name: domain-isolation
    modules: "**"
    deny:
      third_party: [pydantic]
"""
    config_file = tmp_path / ".python-dependency-linter.yaml"
    config_file.write_text(config_content)

    app = tmp_path / "src"
    app.mkdir()
    (app / "__init__.py").write_text("")
    (app / "app.py").write_text("import pydantic\n")

    generated = tmp_path / "src" / "generated"
    generated.mkdir()
    (generated / "__init__.py").write_text("")
    (generated / "models.py").write_text("import pydantic\n")

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["check"])
    assert result.exit_code == 1
    assert "src/app.py" in result.output
    assert "generated/" not in result.output


def test_cli_check_config_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["check"])
    assert result.exit_code == 2


def test_cli_check_explicit_config_not_found():
    runner = CliRunner()
    result = runner.invoke(main, ["check", "--config", "nonexistent.yaml"])
    assert result.exit_code == 2
    assert "not found" in result.output.lower()


def test_cli_check_with_explicit_config(tmp_path, monkeypatch):
    """--config should use the config file's parent as project root."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    config_content = """\
rules:
  - name: domain-isolation
    modules: "**"
    deny:
      third_party: [pydantic]
"""
    config_file = project_dir / "custom-config.yaml"
    config_file.write_text(config_content)

    src = project_dir / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    (src / "app.py").write_text("import pydantic\n")

    # Run from a different directory, but point --config to project_dir
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["check", "--config", str(config_file)])
    assert result.exit_code == 1
    assert "src/app.py" in result.output
