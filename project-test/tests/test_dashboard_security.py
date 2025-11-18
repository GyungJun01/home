"""
Tests for dashboard security validation (TAG-REQ-DASH-005, TAG-REQ-DASH-006)
"""

import json
from io import BytesIO

import pytest

from pysec.dashboard.security import mask_sensitive_data, validate_upload


def test_validate_upload_success() -> None:
    """Valid JSON file passes validation (TAG-REQ-DASH-005)"""
    valid_data = {
        "scan_id": "test-123",
        "target_path": "/tmp/project",
        "timestamp": "2025-11-17T10:00:00",
        "summary": {"total_issues": 1, "high": 0, "medium": 1, "low": 0},
        "issues": [
            {
                "id": "issue-001",
                "severity": "MEDIUM",
                "type": "B101",
                "category": "assert_used",
                "file": "app.py",
                "line": 10,
                "code_snippet": "assert x > 0",
                "description": "Use of assert detected",
                "remediation": "Remove assert or use proper error handling",
            }
        ],
        "metadata": {"bandit_version": "1.8.6", "python_version": "3.11"},
    }

    # Create BytesIO file object
    file_obj = BytesIO(json.dumps(valid_data).encode())
    file_obj.name = "scan_report.json"

    result = validate_upload(file_obj)
    assert result == valid_data


def test_validate_upload_rejects_large_file() -> None:
    """Files exceeding 10MB are rejected (TAG-REQ-DASH-005)"""
    # Create 11MB file
    large_data = {"data": "x" * (11 * 1024 * 1024)}
    file_obj = BytesIO(json.dumps(large_data).encode())
    file_obj.name = "large.json"

    with pytest.raises(ValueError, match="파일 크기.*10MB"):
        validate_upload(file_obj)


def test_validate_upload_rejects_invalid_json() -> None:
    """Invalid JSON format is rejected (TAG-REQ-DASH-005)"""
    file_obj = BytesIO(b"{invalid json}")
    file_obj.name = "invalid.json"

    with pytest.raises(ValueError, match="JSON 형식"):
        validate_upload(file_obj)


def test_validate_upload_rejects_missing_schema() -> None:
    """JSON missing required fields is rejected (TAG-REQ-DASH-005)"""
    invalid_data = {"some_field": "value"}
    file_obj = BytesIO(json.dumps(invalid_data).encode())
    file_obj.name = "invalid_schema.json"

    with pytest.raises(ValueError, match="스키마"):
        validate_upload(file_obj)


def test_mask_sensitive_data_username() -> None:
    """Username in file paths is masked (TAG-REQ-DASH-006)"""
    text = "/home/john/project/app.py"
    masked = mask_sensitive_data(text)
    assert "/home/***/project/app.py" in masked


def test_mask_sensitive_data_api_key() -> None:
    """API keys are masked (TAG-REQ-DASH-006)"""
    text = "api_key=abc123def456"
    masked = mask_sensitive_data(text)
    assert "api_key=***" in masked


def test_mask_sensitive_data_password() -> None:
    """Passwords are masked (TAG-REQ-DASH-006)"""
    text = 'password="secret123"'
    masked = mask_sensitive_data(text)
    assert 'password="***"' in masked
