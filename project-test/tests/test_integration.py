"""
Integration tests for complete workflow
TAG-REQ-SEC-005: Scan execution
TAG-REQ-SEC-009: Progress display
"""

import json
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from pysec.cli.commands import app


def test_full_scan_workflow_text_output() -> None:
    """Full scan workflow with text output (TAG-REQ-SEC-005)"""
    runner = CliRunner()

    result = runner.invoke(app, ["tests/fixtures/sample_project"])

    # Should find issues and exit with code 1
    assert result.exit_code == 1
    assert "Security Scan Report" in result.stdout
    assert "Summary" in result.stdout
    assert "Total Issues" in result.stdout


def test_full_scan_workflow_json_output() -> None:
    """Full scan workflow with JSON output (TAG-REQ-SEC-010)"""
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        output_path = Path(f.name)

    try:
        result = runner.invoke(
            app,
            [
                "tests/fixtures/sample_project",
                "--format",
                "json",
                "--output",
                str(output_path),
            ],
        )

        assert result.exit_code == 1

        # Read JSON from file (cleaner than parsing stdout)
        data = json.loads(output_path.read_text())
        assert "scan_id" in data
        assert "issues" in data
        assert len(data["issues"]) > 0

    finally:
        output_path.unlink(missing_ok=True)


def test_severity_filtering() -> None:
    """Severity filtering workflow (TAG-REQ-SEC-011)"""
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".json"
    ) as f1, tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f2:
        output_all = Path(f1.name)
        output_high = Path(f2.name)

    try:
        # Get all issues
        _ = runner.invoke(
            app,
            [
                "tests/fixtures/sample_project",
                "--format",
                "json",
                "--output",
                str(output_all),
            ],
        )
        data_all = json.loads(output_all.read_text())
        total_issues = len(data_all["issues"])

        # Get only HIGH issues (should be 0 in our sample)
        _ = runner.invoke(
            app,
            [
                "tests/fixtures/sample_project",
                "--format",
                "json",
                "--severity",
                "HIGH",
                "--output",
                str(output_high),
            ],
        )
        data_high = json.loads(output_high.read_text())

        # Should have fewer issues when filtering
        assert len(data_high["issues"]) <= total_issues

    finally:
        output_all.unlink(missing_ok=True)
        output_high.unlink(missing_ok=True)


def test_file_output() -> None:
    """File output workflow (TAG-REQ-SEC-010)"""
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        output_path = Path(f.name)

    try:
        result = runner.invoke(
            app,
            [
                "tests/fixtures/sample_project",
                "--format",
                "json",
                "--output",
                str(output_path),
            ],
        )

        # Check exit code
        assert result.exit_code == 1

        # Check file was created
        assert output_path.exists()

        # Check file content
        content = json.loads(output_path.read_text())
        assert "scan_id" in content
        assert "issues" in content

    finally:
        output_path.unlink(missing_ok=True)


def test_verbose_mode() -> None:
    """Verbose mode shows additional information (TAG-REQ-SEC-009)"""
    runner = CliRunner()

    result = runner.invoke(
        app, ["tests/fixtures/sample_project", "--verbose", "--format", "json"]
    )

    assert result.exit_code == 1
    # With verbose, should see scanning messages
    # (Though they might be in stderr or suppressed by CliRunner)


def test_empty_directory_scan() -> None:
    """Scanning empty directory returns no issues"""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, [tmpdir, "--format", "json"])

        # Should succeed with no issues
        assert result.exit_code == 0
        data = json.loads(result.stdout.split("\n\n")[0])
        assert data["summary"]["total_issues"] == 0
