"""
Tests for dashboard filter components (TAG-REQ-DASH-008)
"""

from pysec.dashboard.components.filters import (
    filter_empty_message,
    get_severity_options,
    validate_severity_filter,
)


def test_get_severity_options() -> None:
    """Get all available severity options (TAG-REQ-DASH-008)"""
    options = get_severity_options()
    assert options == ["HIGH", "MEDIUM", "LOW", "INFO"]


def test_validate_severity_filter_valid() -> None:
    """Validate correct severity filter (TAG-REQ-DASH-008)"""
    assert validate_severity_filter(["HIGH", "MEDIUM"]) is True
    assert validate_severity_filter(["LOW"]) is True
    assert validate_severity_filter(["HIGH", "MEDIUM", "LOW", "INFO"]) is True


def test_validate_severity_filter_invalid() -> None:
    """Reject invalid severity values (TAG-REQ-DASH-008)"""
    assert validate_severity_filter(["CRITICAL"]) is False
    assert validate_severity_filter(["HIGH", "INVALID"]) is False
    assert validate_severity_filter([]) is False


def test_filter_empty_message_severity() -> None:
    """Get message for empty severity filter results (TAG-REQ-DASH-008)"""
    message = filter_empty_message("severity")
    assert "심각도" in message
    assert "필터" in message
    assert "일치하는" in message


def test_filter_empty_message_confidence() -> None:
    """Get message for empty confidence filter results (TAG-REQ-DASH-008)"""
    message = filter_empty_message("confidence")
    assert "신뢰도" in message
