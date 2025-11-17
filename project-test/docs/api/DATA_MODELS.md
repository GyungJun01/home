# Data Models Reference

**SPEC**: SPEC-SECURITY-001
**TAG Traceability**: TAG-REQ-SEC-004, TAG-REQ-SEC-006
**Last Updated**: 2025-11-17

---

## Overview

pysec uses **Pydantic** models for data validation and serialization. All models follow strict type checking and provide automatic validation.

**Implementation**: `src/pysec/scanner/models.py`

---

## Models

### 1. SecurityIssue

**TAG**: TAG-REQ-SEC-004, TAG-REQ-SEC-006

Represents a single security vulnerability detected by the scanner.

#### Schema

```python
class SecurityIssue(BaseModel):
    id: str
    severity: Literal["HIGH", "MEDIUM", "LOW"]
    type: str
    category: str
    file: str
    line: int
    code_snippet: str
    description: str
    owasp_category: str | None
    remediation: str
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | str | Yes | Unique issue identifier (e.g., `issue-001`) |
| `severity` | Literal | Yes | Severity level: `HIGH`, `MEDIUM`, or `LOW` |
| `type` | str | Yes | Bandit test ID (e.g., `B105`) |
| `category` | str | Yes | Human-readable category name |
| `file` | str | Yes | File path where issue was found |
| `line` | int | Yes | Line number in file (1-indexed) |
| `code_snippet` | str | Yes | Problematic code snippet |
| `description` | str | Yes | Detailed issue description |
| `owasp_category` | str \| None | No | OWASP Top 10 category mapping |
| `remediation` | str | Yes | How to fix the issue |

#### Example

```json
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
```

#### Validation Rules

- `severity` must be one of: `HIGH`, `MEDIUM`, `LOW`
- `line` must be a positive integer
- All string fields must be non-empty

---

### 2. ScanSummary

**TAG**: TAG-REQ-SEC-004

Aggregate statistics for scan results.

#### Schema

```python
class ScanSummary(BaseModel):
    total_issues: int
    high: int
    medium: int
    low: int
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `total_issues` | int | >= 0 | Total number of issues found |
| `high` | int | >= 0 | Number of HIGH severity issues |
| `medium` | int | >= 0 | Number of MEDIUM severity issues |
| `low` | int | >= 0 | Number of LOW severity issues |

#### Example

```json
{
  "total_issues": 5,
  "high": 2,
  "medium": 2,
  "low": 1
}
```

#### Validation Rules

- All counts must be >= 0
- `total_issues` should equal `high + medium + low` (not enforced by model)

---

### 3. ScanReport

**TAG**: TAG-REQ-SEC-001

Complete scan report containing all results, summary, and metadata.

#### Schema

```python
class ScanReport(BaseModel):
    scan_id: str
    timestamp: datetime
    target_path: str
    summary: ScanSummary
    issues: list[SecurityIssue]
    metadata: dict[str, str]
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | str | Unique scan identifier (e.g., `scan-20251117-143022`) |
| `timestamp` | datetime | Scan execution timestamp (ISO 8601 format) |
| `target_path` | str | Path that was scanned |
| `summary` | ScanSummary | Scan statistics |
| `issues` | list[SecurityIssue] | List of detected issues (can be empty) |
| `metadata` | dict[str, str] | Scanner metadata (versions, etc.) |

#### Example

```json
{
  "scan_id": "scan-20251117-143022",
  "timestamp": "2025-11-17T14:30:22Z",
  "target_path": "/home/user/my_project",
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

#### Metadata Fields

| Key | Description |
|-----|-------------|
| `scanner` | Scanner name (`Bandit`) |
| `scanner_version` | Bandit version (e.g., `1.8.6`) |
| `pysec_version` | pysec version (e.g., `0.1.0`) |

---

### 4. ScanResult

**TAG**: TAG-REQ-SEC-001

Raw scan execution result from Bandit subprocess.

#### Schema

```python
class ScanResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| `exit_code` | int | Process exit code (0 = success, 1 = issues found, 2+ = error) |
| `stdout` | str | Standard output (JSON from Bandit) |
| `stderr` | str | Standard error (logs, warnings) |

#### Example

```python
ScanResult(
    exit_code=1,
    stdout='{"results": [...], "metrics": {...}}',
    stderr='[bandit] INFO: Running on Python 3.11\n'
)
```

---

## OWASP Top 10 Mapping

**TAG**: TAG-REQ-SEC-004

pysec maps Bandit test IDs to OWASP Top 10 2021 categories:

| Bandit Test | Category | OWASP Category |
|-------------|----------|----------------|
| B105 | Hardcoded Secrets | A02:2021 – Cryptographic Failures |
| B106 | Hardcoded Secrets | A02:2021 – Cryptographic Failures |
| B107 | Hardcoded Secrets | A02:2021 – Cryptographic Failures |
| B201 | SQL Injection | A03:2021 – Injection |
| B608 | SQL Injection | A03:2021 – Injection |
| B501 | Weak Cryptography | A02:2021 – Cryptographic Failures |
| B502 | Weak Cryptography | A02:2021 – Cryptographic Failures |
| B301 | Pickle Usage | A08:2021 – Software and Data Integrity Failures |
| B403 | Import Usage | A05:2021 – Security Misconfiguration |

---

## Severity Classification

**TAG**: TAG-REQ-SEC-004

Severity levels are mapped from Bandit's confidence and severity:

### Bandit → pysec Severity Mapping

| Bandit Severity | Bandit Confidence | pysec Severity |
|----------------|-------------------|----------------|
| HIGH | HIGH | **HIGH** |
| HIGH | MEDIUM | **HIGH** |
| HIGH | LOW | **MEDIUM** |
| MEDIUM | HIGH | **MEDIUM** |
| MEDIUM | MEDIUM | **MEDIUM** |
| MEDIUM | LOW | **LOW** |
| LOW | * | **LOW** |

### Severity Guidelines

- **HIGH**: Critical security vulnerabilities requiring immediate action
  - Hardcoded secrets, SQL injection, command injection
  - Direct path to exploitation

- **MEDIUM**: Important security issues requiring attention
  - Weak cryptography, insecure configurations
  - Requires additional conditions to exploit

- **LOW**: Minor security concerns or best practice violations
  - Deprecated functions, low-confidence detections
  - Limited exploitability

---

## Usage Examples

### Creating a SecurityIssue

```python
from pysec.scanner.models import SecurityIssue

issue = SecurityIssue(
    id="issue-001",
    severity="HIGH",
    type="B105",
    category="Hardcoded Secrets",
    file="app/config.py",
    line=42,
    code_snippet="PASSWORD = 'admin123'",
    description="Hardcoded password detected",
    owasp_category="A02:2021 – Cryptographic Failures",
    remediation="Use environment variables or secrets management"
)

print(issue.model_dump_json(indent=2))
```

### Parsing Bandit JSON Output

```python
import json
from pysec.scanner.models import SecurityIssue, ScanSummary

# Parse Bandit JSON
bandit_output = json.loads(stdout)

# Create issues
issues = []
for result in bandit_output["results"]:
    issue = SecurityIssue(
        id=f"issue-{len(issues)+1:03d}",
        severity=result["issue_severity"],
        type=result["test_id"],
        category=result["test_name"],
        file=result["filename"],
        line=result["line_number"],
        code_snippet=result["code"],
        description=result["issue_text"],
        owasp_category=map_owasp_category(result["test_id"]),
        remediation=get_remediation(result["test_id"])
    )
    issues.append(issue)

# Create summary
summary = ScanSummary(
    total_issues=len(issues),
    high=len([i for i in issues if i.severity == "HIGH"]),
    medium=len([i for i in issues if i.severity == "MEDIUM"]),
    low=len([i for i in issues if i.severity == "LOW"])
)
```

### Filtering by Severity

```python
# Get only HIGH severity issues
high_issues = [i for i in issues if i.severity == "HIGH"]

# Get MEDIUM and above
critical_issues = [i for i in issues if i.severity in ["HIGH", "MEDIUM"]]
```

---

## Validation and Error Handling

### Pydantic Validation

All models use Pydantic's automatic validation:

```python
# This will raise ValidationError
SecurityIssue(
    id="",  # ❌ Empty string not allowed
    severity="CRITICAL",  # ❌ Must be HIGH/MEDIUM/LOW
    line=-1,  # ❌ Must be positive
    # ... missing required fields
)
```

### Type Safety

Models provide full type safety with MyPy:

```python
# Type-checked by MyPy
issue: SecurityIssue = get_issue()
severity: Literal["HIGH", "MEDIUM", "LOW"] = issue.severity

# MyPy error: incompatible types
severity: str = issue.severity  # ❌
```

---

**Related Documentation**:
- [CLI Commands](./CLI_COMMANDS.md)
- [Scanner Implementation](../architecture/SCANNER.md)
- [SPEC-SECURITY-001](../../.moai/specs/SPEC-SECURITY-001/spec.md)
