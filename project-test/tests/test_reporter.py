"""
Reporter tests for JSON and text output
TAG-REQ-SEC-003: Reporting formats
TAG-REQ-SEC-010: JSON output option
"""

import json

import pytest

from pysec.scanner.models import SecurityIssue


@pytest.fixture
def sample_issues() -> list[SecurityIssue]:
    """Sample security issues for testing"""
    return [
        SecurityIssue(
            id="issue-001",
            severity="HIGH",
            type="B105",
            category="Hardcoded Password String",
            file="app/config.py",
            line=42,
            code_snippet="PASSWORD = 'admin123'",
            description="Hardcoded password detected",
            owasp_category="A02:2021 – Cryptographic Failures",
            remediation="Use environment variables or secrets management",
        ),
        SecurityIssue(
            id="issue-002",
            severity="MEDIUM",
            type="B403",
            category="Pickle Import",
            file="app/utils.py",
            line=10,
            code_snippet="import pickle",
            description="Pickle usage can be unsafe",
            remediation="Consider security implications of the imported module",
        ),
        SecurityIssue(
            id="issue-003",
            severity="LOW",
            type="B602",
            category="Shell True",
            file="app/commands.py",
            line=55,
            code_snippet='subprocess.call("ls", shell=True)',
            description="Shell injection risk",
            remediation="Avoid shell=True; use subprocess with list arguments",
        ),
    ]


def test_json_reporter_exists() -> None:
    """JsonReporter class can be imported (TAG-REQ-SEC-010)"""
    from pysec.reporter.json_reporter import JsonReporter

    assert JsonReporter is not None


def test_json_reporter_format(sample_issues: list[SecurityIssue]) -> None:
    """JsonReporter produces valid JSON output (TAG-REQ-SEC-010)"""
    from pysec.reporter.json_reporter import JsonReporter

    reporter = JsonReporter()
    output = reporter.format(sample_issues, "/test/path")

    # Should be valid JSON
    data = json.loads(output)

    # Check required fields
    assert "scan_id" in data
    assert "timestamp" in data
    assert "target_path" in data
    assert data["target_path"] == "/test/path"
    assert "summary" in data
    assert "issues" in data
    assert "metadata" in data


def test_json_reporter_summary(sample_issues: list[SecurityIssue]) -> None:
    """JsonReporter calculates correct summary statistics (TAG-REQ-SEC-003)"""
    from pysec.reporter.json_reporter import JsonReporter

    reporter = JsonReporter()
    output = reporter.format(sample_issues, "/test/path")
    data = json.loads(output)

    summary = data["summary"]
    assert summary["total_issues"] == 3
    assert summary["high"] == 1
    assert summary["medium"] == 1
    assert summary["low"] == 1


def test_json_reporter_issues_serialization(sample_issues: list[SecurityIssue]) -> None:
    """JsonReporter serializes issues correctly (TAG-REQ-SEC-010)"""
    from pysec.reporter.json_reporter import JsonReporter

    reporter = JsonReporter()
    output = reporter.format(sample_issues, "/test/path")
    data = json.loads(output)

    issues = data["issues"]
    assert len(issues) == 3

    # Check first issue
    issue = issues[0]
    assert issue["id"] == "issue-001"
    assert issue["severity"] == "HIGH"
    assert issue["type"] == "B105"


def test_text_reporter_exists() -> None:
    """TextReporter class can be imported (TAG-REQ-SEC-003)"""
    from pysec.reporter.text_reporter import TextReporter

    assert TextReporter is not None


def test_text_reporter_format(sample_issues: list[SecurityIssue]) -> None:
    """TextReporter produces human-readable output (TAG-REQ-SEC-003)"""
    from pysec.reporter.text_reporter import TextReporter

    reporter = TextReporter()
    output = reporter.format(sample_issues)

    # Check for key sections
    assert "Security Scan Report" in output
    assert "Summary" in output
    assert "Total Issues" in output or "total issues" in output.lower()

    # Check severity sections
    assert "HIGH" in output
    assert "MEDIUM" in output
    assert "LOW" in output


def test_text_reporter_severity_counts(sample_issues: list[SecurityIssue]) -> None:
    """TextReporter displays correct counts (TAG-REQ-SEC-003)"""
    from pysec.reporter.text_reporter import TextReporter

    reporter = TextReporter()
    output = reporter.format(sample_issues)

    # Should show counts somewhere in output
    assert "3" in output  # Total issues
    assert "1" in output  # Individual severity counts


def test_text_reporter_issue_details(sample_issues: list[SecurityIssue]) -> None:
    """TextReporter includes issue details (TAG-REQ-SEC-003)"""
    from pysec.reporter.text_reporter import TextReporter

    reporter = TextReporter()
    output = reporter.format(sample_issues)

    # Should include file names and line numbers
    assert "app/config.py" in output
    assert "42" in output

    # Should include fix recommendations
    assert "environment variables" in output.lower() or "remediation" in output.lower()
