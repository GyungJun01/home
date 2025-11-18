"""
Table components for dashboard (TAG-REQ-DASH-004, TAG-REQ-DASH-008, TAG-REQ-DASH-011)

Interactive tables with filtering and pagination for vulnerability display.
"""

import pandas as pd


def filter_issues_by_severity(
    df: pd.DataFrame,
    severities: list[str]
) -> pd.DataFrame:
    """
    Filter issues by severity levels.

    Args:
        df: DataFrame with 'severity' column
        severities: List of severity levels to include (e.g., ['HIGH', 'MEDIUM'])

    Returns:
        Filtered DataFrame

    TAG-REQ-DASH-004: Issue table filtering
    TAG-REQ-DASH-008: Filter change events
    """
    if not severities:
        return pd.DataFrame()

    if len(df) == 0:
        return df

    return df[df["severity"].isin(severities)]


def paginate_dataframe(
    df: pd.DataFrame,
    page: int = 1,
    page_size: int = 100
) -> pd.DataFrame:
    """
    Paginate DataFrame results.

    Args:
        df: DataFrame to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Paginated DataFrame slice

    TAG-REQ-DASH-011: Large dataset pagination
    """
    if page < 1:
        page = 1

    if page_size < 1:
        page_size = 100

    if len(df) == 0:
        return df

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    if start_idx >= len(df):
        return pd.DataFrame()

    return df.iloc[start_idx:end_idx]


def get_pagination_info(
    total_items: int,
    page: int,
    page_size: int
) -> dict[str, int]:
    """
    Get pagination information for display.

    Args:
        total_items: Total number of items
        page: Current page number
        page_size: Items per page

    Returns:
        Dictionary with pagination info

    TAG-REQ-DASH-011: Pagination information
    """
    if page < 1:
        page = 1

    if page_size < 1:
        page_size = 100

    total_pages = (total_items + page_size - 1) // page_size
    start_item = (page - 1) * page_size + 1
    end_item = min(page * page_size, total_items)

    if total_items == 0:
        start_item = 0
        end_item = 0

    return {
        "current_page": page,
        "total_pages": total_pages,
        "start_item": start_item,
        "end_item": end_item,
        "total_items": total_items,
    }
