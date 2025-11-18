"""
Tests for dashboard table and filtering (TAG-REQ-DASH-004, TAG-REQ-DASH-008)
"""

import pandas as pd
import pytest

from pysec.dashboard.components.tables import (
    filter_issues_by_severity,
    get_pagination_info,
    paginate_dataframe,
)


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create sample issue dataframe for testing."""
    return pd.DataFrame(
        [
            {
                "severity": "HIGH",
                "type": "B201",
                "file": "app.py",
                "line": 10,
                "description": "Flask app running with debug=True",
            },
            {
                "severity": "MEDIUM",
                "type": "B101",
                "file": "test.py",
                "line": 20,
                "description": "Use of assert detected",
            },
            {
                "severity": "LOW",
                "type": "B404",
                "file": "util.py",
                "line": 30,
                "description": "Consider possible security implications",
            },
            {
                "severity": "HIGH",
                "type": "B501",
                "file": "api.py",
                "line": 40,
                "description": "Insecure SSL/TLS protocol version",
            },
        ]
    )


def test_filter_issues_by_severity_single(sample_dataframe: pd.DataFrame) -> None:
    """Filter by single severity level (TAG-REQ-DASH-008)"""
    filtered = filter_issues_by_severity(sample_dataframe, ["HIGH"])
    assert len(filtered) == 2
    assert all(filtered["severity"] == "HIGH")


def test_filter_issues_by_severity_multiple(sample_dataframe: pd.DataFrame) -> None:
    """Filter by multiple severity levels (TAG-REQ-DASH-008)"""
    filtered = filter_issues_by_severity(sample_dataframe, ["HIGH", "MEDIUM"])
    assert len(filtered) == 3
    assert set(filtered["severity"].unique()) == {"HIGH", "MEDIUM"}


def test_filter_issues_by_severity_all(sample_dataframe: pd.DataFrame) -> None:
    """Filter with all severities returns all rows (TAG-REQ-DASH-008)"""
    filtered = filter_issues_by_severity(
        sample_dataframe, ["HIGH", "MEDIUM", "LOW", "INFO"]
    )
    assert len(filtered) == len(sample_dataframe)


def test_filter_issues_by_severity_empty(sample_dataframe: pd.DataFrame) -> None:
    """Filter with no matches returns empty dataframe (TAG-REQ-DASH-008)"""
    filtered = filter_issues_by_severity(sample_dataframe, ["INFO"])
    assert len(filtered) == 0


def test_get_pagination_info_first_page() -> None:
    """Pagination info for first page (TAG-REQ-DASH-004)"""
    info = get_pagination_info(total_items=100, page=1, page_size=10)
    assert info["total_items"] == 100
    assert info["total_pages"] == 10
    assert info["current_page"] == 1
    assert info["start_item"] == 1
    assert info["end_item"] == 10


def test_get_pagination_info_last_page() -> None:
    """Pagination info for last page (TAG-REQ-DASH-004)"""
    info = get_pagination_info(total_items=95, page=10, page_size=10)
    assert info["total_pages"] == 10
    assert info["start_item"] == 91
    assert info["end_item"] == 95


def test_get_pagination_info_single_page() -> None:
    """Pagination info when all items fit in one page (TAG-REQ-DASH-004)"""
    info = get_pagination_info(total_items=5, page=1, page_size=10)
    assert info["total_pages"] == 1
    assert info["start_item"] == 1
    assert info["end_item"] == 5


def test_paginate_dataframe_first_page(sample_dataframe: pd.DataFrame) -> None:
    """Paginate to first page (TAG-REQ-DASH-004)"""
    paginated = paginate_dataframe(sample_dataframe, page=1, page_size=2)
    assert len(paginated) == 2
    assert paginated.iloc[0]["file"] == "app.py"


def test_paginate_dataframe_second_page(sample_dataframe: pd.DataFrame) -> None:
    """Paginate to second page (TAG-REQ-DASH-004)"""
    paginated = paginate_dataframe(sample_dataframe, page=2, page_size=2)
    assert len(paginated) == 2
    assert paginated.iloc[0]["file"] == "util.py"


def test_paginate_dataframe_last_page_partial(sample_dataframe: pd.DataFrame) -> None:
    """Last page with fewer items than page_size (TAG-REQ-DASH-004)"""
    paginated = paginate_dataframe(sample_dataframe, page=2, page_size=3)
    assert len(paginated) == 1
    assert paginated.iloc[0]["file"] == "api.py"
