"""
Scanner tests for Bandit integration
TAG-REQ-SEC-001: Bandit integration
TAG-REQ-SEC-004: Severity classification
TAG-REQ-SEC-006: Vulnerability detection
TAG-REQ-SEC-008: Bandit execution failure
"""

from pathlib import Path
from unittest.mock import patch

import pytest


def test_bandit_scanner_exists() -> None:
    """BanditScanner class can be imported (TAG-REQ-SEC-001)"""
    from pysec.scanner.bandit_engine import BanditScanner

    assert BanditScanner is not None


def test_bandit_scanner_runs_successfully() -> None:
    """Bandit scanner executes successfully on sample project (TAG-REQ-SEC-001)"""
    from pysec.scanner.bandit_engine import BanditScanner

    scanner = BanditScanner()
    test_project = Path("tests/fixtures/sample_project")

    result = scanner.scan(test_project)

    assert result is not None
    assert hasattr(result, "exit_code")
    assert hasattr(result, "stdout")
    assert hasattr(result, "stderr")


def test_bandit_result_parsing() -> None:
    """Bandit JSON results are parsed into SecurityIssue objects (TAG-REQ-SEC-006)"""
    from pysec.scanner.bandit_engine import BanditScanner

    scanner = BanditScanner()
    test_project = Path("tests/fixtures/sample_project")

    result = scanner.scan(test_project)
    issues = scanner.parse_results(result.stdout)

    assert isinstance(issues, list)
    # Our sample has at least one issue (hardcoded password)
    assert len(issues) > 0

    # Check first issue has required fields
    issue = issues[0]
    assert hasattr(issue, "severity")
    assert issue.severity in ["HIGH", "MEDIUM", "LOW"]
    assert hasattr(issue, "type")
    assert hasattr(issue, "file")
    assert hasattr(issue, "line")


def test_security_issue_model() -> None:
    """SecurityIssue model validates data correctly (TAG-REQ-SEC-004)"""
    from pysec.scanner.models import SecurityIssue

    issue = SecurityIssue(
        id="issue-001",
        severity="HIGH",
        type="B105",
        category="Hardcoded Password",
        file="test.py",
        line=42,
        code_snippet="PASSWORD = 'secret'",
        description="Hardcoded password detected",
        remediation="Use environment variables",
    )

    assert issue.id == "issue-001"
    assert issue.severity == "HIGH"
    assert issue.type == "B105"


def test_severity_mapping() -> None:
    """Bandit severity levels map correctly to standard levels (TAG-REQ-SEC-004)"""
    from pysec.scanner.bandit_engine import BanditScanner

    scanner = BanditScanner()

    assert scanner._map_severity("HIGH") == "HIGH"
    assert scanner._map_severity("MEDIUM") == "MEDIUM"
    assert scanner._map_severity("LOW") == "LOW"


def test_bandit_execution_failure_handling() -> None:
    """Scanner handles Bandit execution failures gracefully (TAG-REQ-SEC-008)"""

    from pysec.scanner.bandit_engine import BanditScanner

    scanner = BanditScanner()

    # Mock subprocess to simulate failure
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError("bandit command not found")

        with pytest.raises(RuntimeError) as exc_info:
            scanner.scan(Path("."))

        assert "bandit" in str(exc_info.value).lower()


def test_bandit_timeout_handling() -> None:
    """Scanner handles timeouts correctly (TAG-REQ-SEC-008)"""
    import subprocess

    from pysec.scanner.bandit_engine import BanditScanner

    scanner = BanditScanner()

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired("bandit", 1)

        with pytest.raises(RuntimeError) as exc_info:
            scanner.scan(Path("."), timeout=1)

        assert "timeout" in str(exc_info.value).lower()


def test_scan_result_model() -> None:
    """ScanResult model stores scan metadata correctly (TAG-REQ-SEC-001)"""
    from pysec.scanner.models import ScanResult

    result = ScanResult(
        exit_code=0,
        stdout='{"results": []}',
        stderr="",
    )

    assert result.exit_code == 0
    assert result.stdout is not None
