"""
Filter components for dashboard UI (TAG-REQ-DASH-004, TAG-REQ-DASH-008)

Helper functions for building filter UI components.
"""



def get_severity_options() -> list[str]:
    """
    Get available severity levels for filtering.

    Returns:
        List of severity levels

    TAG-REQ-DASH-004: Severity filtering
    """
    return ["HIGH", "MEDIUM", "LOW", "INFO"]


def get_confidence_options() -> list[str]:
    """
    Get available confidence levels for filtering.

    Returns:
        List of confidence levels
    """
    return ["HIGH", "MEDIUM", "LOW"]


def validate_severity_filter(severities: list[str]) -> bool:
    """
    Validate severity filter values.

    Args:
        severities: List of severity values to validate

    Returns:
        True if all values are valid

    TAG-REQ-DASH-008: Filter validation
    """
    if not severities:
        return False
    valid = set(get_severity_options())
    return all(s in valid for s in severities)


def validate_confidence_filter(confidences: list[str]) -> bool:
    """
    Validate confidence filter values.

    Args:
        confidences: List of confidence values to validate

    Returns:
        True if all values are valid
    """
    valid = set(get_confidence_options())
    return all(c in valid for c in confidences)


def filter_empty_message(filter_type: str) -> str:
    """
    Get message for empty filter results.

    Args:
        filter_type: Type of filter applied

    Returns:
        User-friendly message in Korean

    TAG-REQ-DASH-008: Empty result messages
    """
    filter_names = {
        "severity": "심각도",
        "confidence": "신뢰도",
        "type": "유형",
    }
    filter_name = filter_names.get(filter_type, filter_type)
    return f"{filter_name} 필터 조건과 일치하는 항목이 없습니다."
