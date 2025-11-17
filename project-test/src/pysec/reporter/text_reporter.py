"""
Human-readable text format reporter with Rich formatting
TAG-REQ-SEC-003: Reporting formats
"""

from rich.console import Console

from pysec.scanner.models import SecurityIssue


class TextReporter:
    """
    Human-readable text reporter with Rich formatting (TAG-REQ-SEC-003)

    Produces colorful, well-formatted terminal output for human consumption.
    """

    def __init__(self) -> None:
        """Initialize text reporter with Rich console"""
        self.console = Console()

    def format(self, issues: list[SecurityIssue]) -> str:
        """
        Format issues as human-readable text (TAG-REQ-SEC-003)

        Args:
            issues: List of security issues

        Returns:
            Formatted text string with colors and formatting
        """
        output_lines: list[str] = []

        # Header
        output_lines.append("🔍 Security Scan Report")
        output_lines.append("━" * 70)
        output_lines.append("")

        # Summary section
        summary = self._generate_summary(issues)
        output_lines.append("📊 Summary")
        output_lines.append(f"  Total Issues: {summary['total_issues']}")
        output_lines.append(f"  🔴 HIGH: {summary['high']}")
        output_lines.append(f"  🟡 MEDIUM: {summary['medium']}")
        output_lines.append(f"  🟢 LOW: {summary['low']}")
        output_lines.append("")
        output_lines.append("━" * 70)
        output_lines.append("")

        # Issues by severity
        for severity in ["HIGH", "MEDIUM", "LOW"]:
            severity_issues = [i for i in issues if i.severity == severity]
            if severity_issues:
                icon = self._severity_icon(severity)
                output_lines.append(f"{icon} {severity} Severity Issues")
                output_lines.append("")

                for idx, issue in enumerate(severity_issues, 1):
                    output_lines.append(f"[{idx}] {issue.category}")
                    output_lines.append(f"  File: {issue.file}:{issue.line}")
                    output_lines.append(f"  Type: {issue.type}")
                    output_lines.append(f"  Description: {issue.description}")

                    if issue.owasp_category:
                        output_lines.append(f"  OWASP: {issue.owasp_category}")

                    output_lines.append(f"  Fix: {issue.remediation}")
                    output_lines.append("")

                output_lines.append("━" * 70)
                output_lines.append("")

        return "\n".join(output_lines)

    def _generate_summary(self, issues: list[SecurityIssue]) -> dict[str, int]:
        """
        Generate summary statistics (TAG-REQ-SEC-003)

        Args:
            issues: List of security issues

        Returns:
            Dictionary with counts by severity
        """
        return {
            "total_issues": len(issues),
            "high": sum(1 for i in issues if i.severity == "HIGH"),
            "medium": sum(1 for i in issues if i.severity == "MEDIUM"),
            "low": sum(1 for i in issues if i.severity == "LOW"),
        }

    def _severity_icon(self, severity: str) -> str:
        """
        Get emoji icon for severity level

        Args:
            severity: Severity level (HIGH, MEDIUM, LOW)

        Returns:
            Emoji icon string
        """
        icons = {
            "HIGH": "🔴",
            "MEDIUM": "🟡",
            "LOW": "🟢",
        }
        return icons.get(severity, "⚪")
