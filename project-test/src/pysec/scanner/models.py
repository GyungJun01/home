"""
Data models for pysec scanner
TAG-REQ-SEC-004: Severity classification
TAG-REQ-SEC-006: Vulnerability detection data
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SecurityIssue(BaseModel):
    """
    Single security vulnerability model (TAG-REQ-SEC-004, TAG-REQ-SEC-006)

    Represents a security issue detected by the scanner with full context
    and remediation guidance.
    """

    id: str = Field(description="Unique issue identifier")
    severity: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        description="Severity level (HIGH, MEDIUM, LOW)"
    )
    type: str = Field(description="Issue type (e.g., Bandit test ID B105)")
    category: str = Field(description="Human-readable category name")
    file: str = Field(description="File path where issue was found")
    line: int = Field(description="Line number in file")
    code_snippet: str = Field(description="Problematic code snippet")
    description: str = Field(description="Issue description")
    owasp_category: str | None = Field(
        default=None, description="OWASP Top 10 category mapping"
    )
    remediation: str = Field(description="How to fix the issue")


class ScanSummary(BaseModel):
    """
    Scan statistics summary (TAG-REQ-SEC-004)

    Provides aggregate counts by severity level.
    """

    total_issues: int = Field(ge=0, description="Total number of issues found")
    high: int = Field(ge=0, description="Number of HIGH severity issues")
    medium: int = Field(ge=0, description="Number of MEDIUM severity issues")
    low: int = Field(ge=0, description="Number of LOW severity issues")


class ScanReport(BaseModel):
    """
    Complete scan report model (TAG-REQ-SEC-001)

    Contains all scan results, summary statistics, and metadata.
    """

    scan_id: str = Field(description="Unique scan identifier")
    timestamp: datetime = Field(description="Scan execution timestamp")
    target_path: str = Field(description="Path that was scanned")
    summary: ScanSummary = Field(description="Scan statistics")
    issues: list[SecurityIssue] = Field(description="List of detected issues")
    metadata: dict[str, str] = Field(description="Scanner metadata (versions, etc.)")


class ScanResult(BaseModel):
    """
    Raw scan execution result (TAG-REQ-SEC-001)

    Stores raw output from Bandit scanner execution.
    """

    exit_code: int = Field(description="Process exit code")
    stdout: str = Field(description="Standard output (JSON from Bandit)")
    stderr: str = Field(description="Standard error (logs, warnings)")
