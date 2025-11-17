# CLI Commands Reference

**SPEC**: SPEC-SECURITY-001
**TAG Traceability**: TAG-REQ-SEC-002, TAG-REQ-SEC-005, TAG-REQ-SEC-010, TAG-REQ-SEC-011
**Last Updated**: 2025-11-17

---

## Overview

pysec provides a command-line interface for scanning Python projects for security vulnerabilities using Bandit SAST integration.

## Installation

```bash
# Using uv (recommended)
uv sync --all-extras

# Or using pip
pip install -e .
```

## Main Command: `scan`

Scan Python project for security vulnerabilities using Bandit SAST.

### Syntax

```bash
pysec scan <TARGET_PATH> [OPTIONS]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `TARGET_PATH` | Path | Yes | Target path to scan (directory or file). Must exist and be readable. |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--format` | `-f` | str | `text` | Output format: `text` or `json` |
| `--severity` | `-s` | str | `ALL` | Filter by severity: `ALL`, `HIGH`, `MEDIUM`, `LOW` |
| `--output` | `-o` | Path | stdout | Output file path (saves to file instead of stdout) |
| `--verbose` | `-v` | bool | `false` | Enable verbose logging |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Scan completed successfully, no issues found |
| 1 | Scan completed successfully, issues found |
| 2 | Scan failed due to error (invalid path, Bandit failure, etc.) |

### Examples

#### Basic Scan

Scan current directory with text output:

```bash
pysec scan .
```

**Output**:
```
🔍 Security Scan Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Summary
  Total Issues: 5
  🔴 HIGH: 2
  🟡 MEDIUM: 2
  🟢 LOW: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 HIGH Severity Issues

[1] Hardcoded password string
  File: app/config.py:42
  Type: B105 (hardcoded_password_string)
  OWASP: A02:2021 – Cryptographic Failures
  Fix: Use environment variables or secrets management
```

#### JSON Output

Generate JSON report for programmatic processing:

```bash
pysec scan ./my_project --format json
```

**Output**:
```json
{
  "scan_id": "scan-20251117-143022",
  "timestamp": "2025-11-17T14:30:22Z",
  "target_path": "/path/to/my_project",
  "summary": {
    "total_issues": 5,
    "high": 2,
    "medium": 2,
    "low": 1
  },
  "issues": [
    {
      "id": "issue-001",
      "severity": "HIGH",
      "type": "B105",
      "category": "Hardcoded Secrets",
      "file": "app/config.py",
      "line": 42,
      "code_snippet": "PASSWORD = 'admin123'",
      "description": "Hardcoded password detected",
      "owasp_category": "A02:2021 – Cryptographic Failures",
      "remediation": "Use environment variables or secrets management"
    }
  ],
  "metadata": {
    "scanner": "Bandit",
    "scanner_version": "1.8.6",
    "pysec_version": "0.1.0"
  }
}
```

#### Severity Filtering

Show only HIGH severity issues:

```bash
pysec scan ./my_project --severity HIGH
```

Filter to MEDIUM and above:

```bash
pysec scan ./my_project --severity MEDIUM
```

#### Save to File

Save JSON report to file:

```bash
pysec scan ./my_project --format json --output security-report.json
```

Save text report:

```bash
pysec scan ./my_project --output security-report.txt
```

#### Verbose Mode

Enable detailed logging for troubleshooting:

```bash
pysec scan ./my_project --verbose
```

**Additional Output**:
```
Scanning: /path/to/my_project
Format: text, Severity filter: ALL
Bandit exit code: 1
Filtered to 5 ALL issues
```

#### Combined Options

Scan with multiple options:

```bash
pysec scan ./my_project \
  --format json \
  --severity HIGH \
  --output high-severity.json \
  --verbose
```

### Error Handling

#### Invalid Path (Exit Code 2)

**TAG-REQ-SEC-007**: Handling invalid target paths

```bash
$ pysec scan /nonexistent/path
Usage: pysec scan [OPTIONS] TARGET_PATH
Try 'pysec scan --help' for help.

Error: Invalid value for 'TARGET_PATH': Path '/nonexistent/path' does not exist.
```

#### Bandit Execution Failure (Exit Code 2)

**TAG-REQ-SEC-008**: Handling Bandit execution failures

```bash
$ pysec scan ./my_project
❌ Scan failed: Bandit command not found

Troubleshooting:
  1. Ensure Bandit is installed: pip install bandit
  2. Check if target path is readable
  3. Try running with --verbose flag
```

#### Parse Failure (Exit Code 2)

```bash
$ pysec scan ./my_project --verbose
❌ Failed to parse Bandit output: Invalid JSON format
Raw output: (bandit error message...)
```

### Progress Indicators

**TAG-REQ-SEC-009**: Real-time progress display

During scan execution, pysec shows progress:

```
⠋ 🔍 Starting security scan...
⠙ ⚙️  Running Bandit scanner...
⠹ 📋 Parsing results...
⠸ 📄 Generating report...
```

### Integration with CI/CD

#### GitHub Actions

```yaml
- name: Security Scan
  run: |
    pysec scan . --format json --output security-report.json
    if [ $? -eq 1 ]; then
      echo "Security issues found!"
      exit 1
    fi
```

#### GitLab CI

```yaml
security-scan:
  script:
    - pysec scan . --format json --output security-report.json
  artifacts:
    reports:
      security: security-report.json
  allow_failure: false
```

#### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

pysec scan . --severity HIGH
if [ $? -eq 1 ]; then
  echo "❌ HIGH severity issues detected. Commit blocked."
  exit 1
fi
```

## Help Command

Display help information:

```bash
pysec --help
pysec scan --help
```

## Version Information

Check installed version:

```bash
pysec --version
```

---

**Related Documentation**:
- [Data Models](./DATA_MODELS.md)
- [Architecture](../architecture/OVERVIEW.md)
- [SPEC-SECURITY-001](../../.moai/specs/SPEC-SECURITY-001/spec.md)
