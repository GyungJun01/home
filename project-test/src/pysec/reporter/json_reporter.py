"""
JSON format reporter
TAG-REQ-SEC-003: Reporting formats
TAG-REQ-SEC-010: JSON output option
"""

import json
from datetime import UTC, datetime

from pysec.scanner.models import SecurityIssue


class JsonReporter:
    """
    JSON format reporter for scan results (TAG-REQ-SEC-010)

    Produces machine-readable JSON output suitable for programmatic processing
    and integration with CI/CD pipelines.
    """

    def format(self, issues: list[SecurityIssue], target_path: str) -> str:
        """
        Format issues as JSON string (TAG-REQ-SEC-010)

        Args:
            issues: List of security issues
            target_path: Path that was scanned

        Returns:
            JSON-formatted string with complete scan report
        """
        summary = self._generate_summary(issues)
        timestamp = datetime.now(UTC)

        report = {
            "scan_id": f"scan-{timestamp.strftime('%Y%m%d-%H%M%S')}",
            "timestamp": timestamp.isoformat(),
            "target_path": target_path,
            "summary": summary,
            "issues": [issue.model_dump() for issue in issues],
            "metadata": {
                "scanner": "Bandit",
                "pysec_version": "0.1.0",
            },
        }

        return json.dumps(report, indent=2, ensure_ascii=False)

    def _generate_summary(self, issues: list[SecurityIssue]) -> dict[str, int]:
        """
        Generate summary statistics by severity (TAG-REQ-SEC-003)

        Args:
            issues: List of security issues

        Returns:
            Dictionary with counts by severity level
        """
        return {
            "total_issues": len(issues),
            "high": sum(1 for i in issues if i.severity == "HIGH"),
            "medium": sum(1 for i in issues if i.severity == "MEDIUM"),
            "low": sum(1 for i in issues if i.severity == "LOW"),
        }
