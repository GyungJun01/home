"""
Data loading and parsing for dashboard (TAG-REQ-DASH-002)

Handles JSON file parsing and conversion to Pydantic models.
"""

import json
from typing import Any

from pydantic import ValidationError

from pysec.scanner.models import ScanReport


def parse_json_file(content: str) -> dict[str, Any]:
    """
    Parse JSON string and return dictionary.

    Args:
        content: JSON content as string

    Returns:
        Parsed JSON as dictionary

    Raises:
        ValueError: If JSON is invalid

    TAG-REQ-DASH-002: JSON parsing with clear error messages
    """
    try:
        data: dict[str, Any] = json.loads(content)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e


def load_scan_report(data: dict[str, Any]) -> ScanReport:
    """
    Load ScanReport from dictionary with validation.

    Args:
        data: Dictionary containing scan report data

    Returns:
        Validated ScanReport object

    Raises:
        ValueError: If data doesn't match ScanReport schema

    TAG-REQ-DASH-010: Schema validation with helpful error messages
    """
    try:
        report = ScanReport(**data)
        return report
    except ValidationError as e:
        raise ValueError(f"Invalid schema: {e}") from e


def convert_to_dataframe(report: ScanReport) -> Any:
    """
    Convert ScanReport to pandas DataFrame.

    Args:
        report: ScanReport object

    Returns:
        pandas DataFrame with issues data

    TAG-REQ-DASH-011: Large dataset handling
    """
    import pandas as pd

    issues_data = []
    for issue in report.issues:
        issues_data.append({
            "id": issue.id,
            "severity": issue.severity,
            "type": issue.type,
            "category": issue.category,
            "file": issue.file,
            "line": issue.line,
            "code_snippet": issue.code_snippet,
            "description": issue.description,
            "owasp_category": issue.owasp_category,
            "remediation": issue.remediation,
        })

    df = pd.DataFrame(issues_data)
    return df
