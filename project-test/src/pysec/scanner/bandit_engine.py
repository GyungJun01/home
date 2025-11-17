"""
Bandit SAST scanner integration
TAG-REQ-SEC-001: Bandit integration
TAG-REQ-SEC-006: Vulnerability detection
TAG-REQ-SEC-008: Bandit execution failure handling
"""

import json
import subprocess
from pathlib import Path
from typing import Literal

from pysec.scanner.models import ScanResult, SecurityIssue


class BanditScanner:
    """
    Bandit SAST scanner wrapper (TAG-REQ-SEC-001)

    Executes Bandit as subprocess and parses results into structured data models.
    """

    # OWASP Top 10 2021 mapping for common Bandit test IDs
    OWASP_MAPPING: dict[str, str] = {
        "B105": "A02:2021 – Cryptographic Failures",
        "B106": "A02:2021 – Cryptographic Failures",
        "B107": "A02:2021 – Cryptographic Failures",
        "B201": "A03:2021 – Injection",
        "B301": "A08:2021 – Software and Data Integrity Failures",
        "B302": "A08:2021 – Software and Data Integrity Failures",
        "B303": "A08:2021 – Software and Data Integrity Failures",
        "B304": "A08:2021 – Software and Data Integrity Failures",
        "B305": "A08:2021 – Software and Data Integrity Failures",
        "B403": "A08:2021 – Software and Data Integrity Failures",
        "B501": "A02:2021 – Cryptographic Failures",
        "B602": "A03:2021 – Injection",
        "B605": "A03:2021 – Injection",
        "B607": "A03:2021 – Injection",
        "B608": "A03:2021 – Injection",
    }

    # Remediation advice for common issues
    REMEDIATION_ADVICE: dict[str, str] = {
        "B105": "Use environment variables or secrets management systems (e.g., AWS Secrets Manager, HashiCorp Vault)",
        "B106": "Use environment variables or secrets management systems",
        "B107": "Use environment variables or secrets management systems",
        "B201": "Use parameterized queries or ORM frameworks to prevent SQL injection",
        "B301": "Avoid pickle; use JSON or other safe serialization formats",
        "B302": "Avoid marshal; use JSON or other safe serialization formats",
        "B403": "Consider security implications of the imported module",
        "B501": "Use strong hashing algorithms (SHA-256 or better)",
        "B602": "Avoid shell=True; use subprocess with list arguments",
        "B605": "Validate and sanitize all inputs before use",
        "B607": "Use absolute paths and validate executable locations",
        "B608": "Use parameterized queries to prevent SQL injection",
    }

    def scan(self, target_path: Path, timeout: int = 300) -> ScanResult:
        """
        Execute Bandit scan on target path (TAG-REQ-SEC-001)

        Args:
            target_path: Directory or file to scan
            timeout: Maximum execution time in seconds (default: 300)

        Returns:
            ScanResult with exit code and output

        Raises:
            RuntimeError: If Bandit execution fails or times out
        """
        cmd = [
            "bandit",
            "-r",  # Recursive scan
            str(target_path),
            "-f",
            "json",  # JSON output format
        ]

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,  # Don't raise on non-zero exit (Bandit returns 1 when issues found)
            )

            return ScanResult(
                exit_code=process.returncode,
                stdout=process.stdout,
                stderr=process.stderr,
            )

        except subprocess.TimeoutExpired as e:
            raise RuntimeError(
                f"Bandit scan timed out after {timeout} seconds. "
                f"Try scanning a smaller directory or increasing timeout."
            ) from e

        except FileNotFoundError as e:
            raise RuntimeError(
                "Bandit command not found. Please install: pip install bandit"
            ) from e

        except Exception as e:
            raise RuntimeError(f"Failed to execute Bandit scanner: {e}") from e

    def parse_results(self, json_output: str) -> list[SecurityIssue]:
        """
        Parse Bandit JSON output into SecurityIssue objects (TAG-REQ-SEC-006)

        Args:
            json_output: Raw JSON string from Bandit

        Returns:
            List of SecurityIssue objects

        Raises:
            ValueError: If JSON is invalid or missing required fields
        """
        try:
            data = json.loads(json_output)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON output from Bandit: {e}") from e

        issues: list[SecurityIssue] = []
        results = data.get("results", [])

        for idx, result in enumerate(results):
            try:
                issue = SecurityIssue(
                    id=f"issue-{idx + 1:03d}",
                    severity=self._map_severity(result["issue_severity"]),
                    type=result["test_id"],
                    category=self._format_category(result["test_name"]),
                    file=result["filename"],
                    line=result["line_number"],
                    code_snippet=result.get("code", "").strip(),
                    description=result["issue_text"],
                    owasp_category=self._map_owasp(result["test_id"]),
                    remediation=self._get_remediation(result["test_id"]),
                )
                issues.append(issue)
            except KeyError as e:
                # Skip malformed results but continue parsing
                print(f"Warning: Skipping malformed result at index {idx}: missing {e}")
                continue

        return issues

    def _map_severity(self, bandit_severity: str) -> Literal["HIGH", "MEDIUM", "LOW"]:
        """
        Map Bandit severity to standard levels (TAG-REQ-SEC-004)

        Args:
            bandit_severity: Bandit severity string (HIGH, MEDIUM, LOW)

        Returns:
            Standardized severity level
        """
        severity = bandit_severity.upper()
        if severity == "HIGH":
            return "HIGH"
        elif severity == "LOW":
            return "LOW"
        # Default to MEDIUM if unknown or MEDIUM
        return "MEDIUM"

    def _map_owasp(self, test_id: str) -> str | None:
        """
        Map Bandit test ID to OWASP Top 10 category

        Args:
            test_id: Bandit test identifier (e.g., B105)

        Returns:
            OWASP category string or None if not mapped
        """
        return self.OWASP_MAPPING.get(test_id)

    def _get_remediation(self, test_id: str) -> str:
        """
        Get remediation advice for test ID

        Args:
            test_id: Bandit test identifier

        Returns:
            Remediation advice string
        """
        return self.REMEDIATION_ADVICE.get(
            test_id, "Review code and apply security best practices"
        )

    def _format_category(self, test_name: str) -> str:
        """
        Format Bandit test name to human-readable category

        Args:
            test_name: Bandit test name (e.g., hardcoded_password_string)

        Returns:
            Formatted category name (e.g., Hardcoded Password String)
        """
        return test_name.replace("_", " ").title()
