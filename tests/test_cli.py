from pathlib import Path

from click.testing import CliRunner

from python_dependency_linter.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_check_with_violations(tmp_path):
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

    runner = CliRunner()
    result = runner.invoke(
        main, ["check", "--config", str(config_file), "--project-root", str(tmp_path)]
    )
    assert result.exit_code == 1
    assert "[domain-isolation]" in result.output
    assert "Found" in result.output


def test_cli_check_no_violations(tmp_path):
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

    runner = CliRunner()
    result = runner.invoke(
        main, ["check", "--config", str(config_file), "--project-root", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "No violations found." in result.output


def test_cli_check_config_not_found():
    runner = CliRunner()
    result = runner.invoke(main, ["check", "--config", "nonexistent.yaml"])
    assert result.exit_code != 0
