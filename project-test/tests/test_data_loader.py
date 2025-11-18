"""
Tests for dashboard data loader module (TAG-REQ-DASH-002, TAG-REQ-DASH-009, TAG-REQ-DASH-010)

Tests for JSON file parsing, validation, and error handling.
"""

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from pysec.dashboard.data_loader import (
    load_scan_report,
    parse_json_file,
)


class TestDataLoader:
    """Tests for data loading and parsing"""

    def test_parse_json_file_success(self) -> None:
        """Test successful JSON parsing"""
        data = {
            "scan_id": "scan-001",
            "timestamp": "2025-11-17T12:00:00",
            "target_path": "/home/user/project",
            "summary": {"total_issues": 1, "high": 1, "medium": 0, "low": 0},
            "issues": [{
                "id": "B101",
                "severity": "HIGH",
                "type": "assert_used",
                "category": "Assert",
                "file": "/home/user/project/app.py",
                "line": 10,
                "code_snippet": "assert x",
                "description": "Use of assert",
                "owasp_category": "A05:2021",
                "remediation": "Use proper validation",
            }],
            "metadata": {"version": "1.0"},
        }

        result = parse_json_file(json.dumps(data))
        assert result["scan_id"] == "scan-001"

    def test_parse_json_file_invalid_json(self) -> None:
        """Test parsing invalid JSON"""
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_json_file("invalid json {{")

    def test_load_scan_report_from_dict(self) -> None:
        """Test loading ScanReport from dictionary"""
        data = {
            "scan_id": "scan-001",
            "timestamp": "2025-11-17T12:00:00",
            "target_path": "/home/user/project",
            "summary": {"total_issues": 0, "high": 0, "medium": 0, "low": 0},
            "issues": [],
            "metadata": {"version": "1.0"},
        }

        report = load_scan_report(data)
        assert report.scan_id == "scan-001"
        assert report.target_path == "/home/user/project"

    def test_load_scan_report_missing_fields(self) -> None:
        """Test ScanReport validation with missing fields"""
        data = {
            "scan_id": "scan-001",
            # Missing required fields
        }

        with pytest.raises(ValueError, match="Invalid schema"):
            load_scan_report(data)

    def test_load_scan_report_invalid_summary(self) -> None:
        """Test ScanReport validation with invalid summary"""
        data = {
            "scan_id": "scan-001",
            "timestamp": "2025-11-17T12:00:00",
            "target_path": "/home/user/project",
            "summary": {"total_issues": "invalid"},  # Should be int
            "issues": [],
            "metadata": {},
        }

        with pytest.raises(ValueError, match="Invalid schema"):
            load_scan_report(data)


class TestJSONParsing:
    """Tests for JSON parsing edge cases"""

    def test_parse_empty_json_object(self) -> None:
        """Test parsing empty JSON object"""
        result = parse_json_file("{}")
        assert result == {}

    def test_parse_json_with_null_values(self) -> None:
        """Test parsing JSON with null values"""
        data = {"key": None, "value": "test"}
        result = parse_json_file(json.dumps(data))
        assert result["key"] is None

    def test_parse_json_with_unicode(self) -> None:
        """Test parsing JSON with Unicode characters"""
        data = {"description": "문제 설명 with émojis 🔒"}
        result = parse_json_file(json.dumps(data))
        assert "문제" in result["description"]
