"""
CLI tests for pysec scanner
TAG-REQ-SEC-002: CLI interface
TAG-REQ-SEC-007: Invalid path handling
TAG-REQ-SEC-010: JSON output option
TAG-REQ-SEC-011: Severity filtering option
"""

from typer.testing import CliRunner


def test_cli_app_exists() -> None:
    """CLI application exists and can be imported (TAG-REQ-SEC-002)"""
    from pysec.cli.commands import app

    assert app is not None


def test_scan_command_accepts_path() -> None:
    """pysec scan command accepts a path argument (TAG-REQ-SEC-002)"""
    from pysec.cli.commands import app

    runner = CliRunner()
    # Use current directory for now (will fail without implementation)
    result = runner.invoke(app, ["scan", "."])

    # Should not have argument parsing errors
    assert "Error" not in result.stdout or result.exit_code == 0


def test_scan_rejects_invalid_path() -> None:
    """Scan command rejects non-existent paths (TAG-REQ-SEC-007)"""
    from pysec.cli.commands import app

    runner = CliRunner()
    result = runner.invoke(app, ["scan", "/nonexistent/path/12345"])

    # Should exit with error
    assert result.exit_code != 0
    # Typer puts error messages in stdout or stderr
    error_output = result.stdout + result.stderr
    assert "does not exist" in error_output.lower() or "not found" in error_output.lower()


def test_scan_accepts_format_option() -> None:
    """Scan command accepts --format option (TAG-REQ-SEC-010)"""
    from pysec.cli.commands import app

    runner = CliRunner()
    result = runner.invoke(app, ["scan", ".", "--format", "json"])

    # Should accept the option without argument parsing error
    assert "Error: No such option: --format" not in result.stdout


def test_scan_accepts_severity_option() -> None:
    """Scan command accepts --severity option (TAG-REQ-SEC-011)"""
    from pysec.cli.commands import app

    runner = CliRunner()
    result = runner.invoke(app, ["scan", ".", "--severity", "HIGH"])

    # Should accept the option without argument parsing error
    assert "Error: No such option: --severity" not in result.stdout


def test_scan_accepts_output_option() -> None:
    """Scan command accepts --output option for file output (TAG-REQ-SEC-010)"""
    from pysec.cli.commands import app

    runner = CliRunner()
    result = runner.invoke(app, ["scan", ".", "--output", "report.json"])

    # Should accept the option without argument parsing error
    assert "Error: No such option: --output" not in result.stdout
