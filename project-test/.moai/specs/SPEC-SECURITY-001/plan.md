# SPEC-SECURITY-001 구현 계획 (Implementation Plan)

## TAG BLOCK

```yaml
spec_id: SPEC-SECURITY-001
title: Python 보안 스캐너 MVP - 구현 계획
document_type: implementation_plan
version: 0.1.0
created: 2025-11-17
priority: HIGH
```

---

## 📋 목차

1. [구현 전략](#1-구현-전략)
2. [TDD 사이클](#2-tdd-사이클)
3. [모듈별 구현 계획](#3-모듈별-구현-계획)
4. [기술 아키텍처](#4-기술-아키텍처)
5. [마일스톤](#5-마일스톤)
6. [위험 관리](#6-위험-관리)
7. [품질 보증](#7-품질-보증)

---

## 1. 구현 전략

### 1.1 개발 방법론

**TDD (Test-Driven Development) 강제 적용**
- **Red**: 실패하는 테스트 작성
- **Green**: 최소한의 코드로 테스트 통과
- **Refactor**: 코드 품질 개선

**우선순위 기반 개발**
- **Primary Goals**: CLI + Bandit 스캐너 (핵심 기능)
- **Secondary Goals**: JSON 리포터 (부가 기능)
- **Final Goals**: 텍스트 포맷 개선 (완성도)

### 1.2 기술 스택 설정

#### 프로젝트 초기화
```bash
# UV 패키지 매니저 사용
uv init pysec
cd pysec

# 의존성 추가
uv add typer[all]>=0.20.0
uv add bandit>=1.8.6
uv add rich>=13.9.0
uv add pydantic>=2.10.0
uv add loguru>=0.7.0

# 개발 의존성
uv add --dev pytest>=8.3.0
uv add --dev pytest-cov>=6.0.0
uv add --dev mypy>=1.13.0
uv add --dev ruff>=0.8.0
```

#### pyproject.toml 설정
```toml
[project]
name = "pysec"
version = "0.1.0"
description = "Python Security Scanner MVP - SAST with Bandit"
authors = [{name = "@user", email = "user@example.com"}]
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}

dependencies = [
    "typer[all]>=0.20.0",
    "bandit>=1.8.6",
    "rich>=13.9.0",
    "pydantic>=2.10.0",
    "loguru>=0.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-cov>=6.0.0",
    "mypy>=1.13.0",
    "ruff>=0.8.0",
]

[project.scripts]
pysec = "pysec.cli.main:app"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src/pysec --cov-report=html --cov-report=term-missing --cov-fail-under=85"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
strict = true

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "B", "C4", "UP"]
ignore = ["E501"]
```

---

## 2. TDD 사이클

### 2.1 Red-Green-Refactor 프로세스

#### Step 1: Red (실패 테스트)
```python
# tests/test_cli.py
def test_scan_command_accepts_path():
    """pysec scan 명령어가 경로를 받는지 테스트 (TAG-REQ-SEC-002)"""
    from typer.testing import CliRunner
    from pysec.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["scan", "./test_project"])

    # 아직 구현 안 됨 → 실패 예상
    assert result.exit_code == 0
```

**실행**: `pytest tests/test_cli.py::test_scan_command_accepts_path`
**예상 결과**: ❌ FAILED (명령어 미구현)

#### Step 2: Green (최소 구현)
```python
# src/pysec/cli/main.py
import typer

app = typer.Typer()

@app.command()
def scan(target_path: str):
    """Python 프로젝트 보안 스캔"""
    typer.echo(f"Scanning {target_path}...")
```

**실행**: `pytest tests/test_cli.py::test_scan_command_accepts_path`
**예상 결과**: ✅ PASSED

#### Step 3: Refactor (개선)
```python
# src/pysec/cli/commands.py
from pathlib import Path
from typing import Annotated
import typer

def scan(
    target_path: Annotated[Path, typer.Argument(help="스캔 대상 경로")],
    format: Annotated[str, typer.Option(help="출력 형식")] = "text",
    severity: Annotated[str, typer.Option(help="심각도 필터")] = "ALL",
):
    """Python 프로젝트 보안 취약점 스캔 (TAG-REQ-SEC-002, TAG-REQ-SEC-005)"""
    if not target_path.exists():
        raise typer.BadParameter(f"경로를 찾을 수 없습니다: {target_path}")

    typer.echo(f"🔍 Scanning {target_path}...")
```

**실행**: `pytest`
**예상 결과**: ✅ 모든 테스트 통과 + Mypy/Ruff 통과

---

## 3. 모듈별 구현 계획

### 3.1 Phase 1: CLI 인프라 (Primary Goal)

#### 목표
- Typer 기반 CLI 엔트리포인트 구현
- 명령어 파싱 및 검증
- 에러 처리 및 사용자 피드백

#### TDD 순서

**Test 1: CLI 엔트리포인트**
```python
# tests/test_cli.py
def test_cli_app_exists():
    """CLI 애플리케이션이 존재하는지 테스트 (TAG-REQ-SEC-002)"""
    from pysec.cli.main import app
    assert app is not None
```

**구현**:
```python
# src/pysec/cli/main.py
import typer
from pysec.cli.commands import scan

app = typer.Typer(
    name="pysec",
    help="Python Security Scanner MVP",
    add_completion=True,
)

app.command()(scan)

if __name__ == "__main__":
    app()
```

**Test 2: 경로 검증**
```python
def test_scan_rejects_invalid_path():
    """존재하지 않는 경로 거부 테스트 (TAG-REQ-SEC-007)"""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", "/nonexistent/path"])

    assert result.exit_code != 0
    assert "경로를 찾을 수 없습니다" in result.stdout
```

**Test 3: 옵션 파싱**
```python
def test_scan_accepts_format_option():
    """--format 옵션 테스트 (TAG-REQ-SEC-010)"""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", ".", "--format", "json"])

    assert result.exit_code == 0
```

#### 구현 파일
- `src/pysec/cli/__init__.py`
- `src/pysec/cli/main.py`
- `src/pysec/cli/commands.py`

#### 예상 결과
- ✅ CLI 명령어 실행 가능
- ✅ 도움말 메시지 출력
- ✅ 잘못된 경로 입력 시 에러 처리

---

### 3.2 Phase 2: Bandit 스캐너 통합 (Primary Goal)

#### 목표
- Bandit을 서브프로세스로 실행
- JSON 결과 파싱
- Pydantic 모델로 데이터 변환

#### TDD 순서

**Test 1: Bandit 실행**
```python
# tests/test_scanner.py
import pytest
from pathlib import Path
from pysec.scanner.bandit_engine import BanditScanner

def test_bandit_scanner_runs_successfully():
    """Bandit 스캐너 실행 테스트 (TAG-REQ-SEC-001)"""
    scanner = BanditScanner()
    test_project = Path("tests/fixtures/sample_project")

    result = scanner.scan(test_project)

    assert result is not None
    assert result.exit_code == 0
```

**구현**:
```python
# src/pysec/scanner/bandit_engine.py
import subprocess
import json
from pathlib import Path
from pydantic import BaseModel

class BanditResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str

class BanditScanner:
    """Bandit SAST 스캐너 (TAG-REQ-SEC-001)"""

    def scan(self, target_path: Path, timeout: int = 300) -> BanditResult:
        """Bandit 스캔 실행"""
        cmd = [
            "bandit",
            "-r",  # 재귀적 스캔
            str(target_path),
            "-f", "json",  # JSON 출력
        ]

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,  # 에러 코드 무시 (취약점 발견 시 1 반환)
            )

            return BanditResult(
                exit_code=process.returncode,
                stdout=process.stdout,
                stderr=process.stderr,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Bandit 스캔 타임아웃 ({timeout}초)")
```

**Test 2: JSON 파싱**
```python
def test_bandit_result_parsing():
    """Bandit JSON 결과 파싱 테스트 (TAG-REQ-SEC-006)"""
    scanner = BanditScanner()
    test_project = Path("tests/fixtures/sample_project")

    result = scanner.scan(test_project)
    issues = scanner.parse_results(result.stdout)

    assert isinstance(issues, list)
    assert len(issues) > 0
    assert issues[0].severity in ["HIGH", "MEDIUM", "LOW"]
```

**구현**:
```python
# src/pysec/scanner/models.py
from pydantic import BaseModel, Field
from typing import Literal

class SecurityIssue(BaseModel):
    """보안 취약점 모델 (TAG-REQ-SEC-004)"""
    id: str
    severity: Literal["HIGH", "MEDIUM", "LOW"]
    type: str
    category: str
    file: str
    line: int
    code_snippet: str
    description: str
    owasp_category: str | None = None
    remediation: str

# src/pysec/scanner/bandit_engine.py (추가)
def parse_results(self, json_output: str) -> list[SecurityIssue]:
    """Bandit JSON 결과를 SecurityIssue 리스트로 변환"""
    data = json.loads(json_output)
    issues = []

    for idx, result in enumerate(data.get("results", [])):
        issue = SecurityIssue(
            id=f"issue-{idx+1:03d}",
            severity=self._map_severity(result["issue_severity"]),
            type=result["test_id"],
            category=result["test_name"].replace("_", " ").title(),
            file=result["filename"],
            line=result["line_number"],
            code_snippet=result.get("code", ""),
            description=result["issue_text"],
            owasp_category=self._map_owasp(result["test_id"]),
            remediation=self._get_remediation(result["test_id"]),
        )
        issues.append(issue)

    return issues
```

**Test 3: 심각도 매핑**
```python
def test_severity_mapping():
    """Bandit severity를 표준 심각도로 변환 테스트 (TAG-REQ-SEC-004)"""
    scanner = BanditScanner()

    assert scanner._map_severity("HIGH") == "HIGH"
    assert scanner._map_severity("MEDIUM") == "MEDIUM"
    assert scanner._map_severity("LOW") == "LOW"
```

#### 테스트 픽스처 준비
```python
# tests/fixtures/sample_project/vulnerable_code.py
# 테스트용 취약한 코드 샘플
PASSWORD = "admin123"  # B105: Hardcoded password

import os
os.system("ls -la")  # B605: Shell injection risk
```

#### 구현 파일
- `src/pysec/scanner/__init__.py`
- `src/pysec/scanner/bandit_engine.py`
- `src/pysec/scanner/models.py`

#### 예상 결과
- ✅ Bandit 실행 성공
- ✅ JSON 결과 파싱 성공
- ✅ SecurityIssue 모델 변환 성공

---

### 3.3 Phase 3: 리포팅 (Secondary Goal)

#### 목표
- JSON 형식 리포터 구현
- 텍스트 형식 리포터 구현 (Rich 사용)
- 심각도별 통계 생성

#### TDD 순서

**Test 1: JSON 리포터**
```python
# tests/test_reporter.py
def test_json_reporter_output():
    """JSON 리포터 출력 테스트 (TAG-REQ-SEC-010)"""
    from pysec.reporter.json_reporter import JsonReporter
    from pysec.scanner.models import SecurityIssue, ScanReport

    issues = [
        SecurityIssue(
            id="issue-001",
            severity="HIGH",
            type="B105",
            category="Hardcoded Password",
            file="app/config.py",
            line=42,
            code_snippet="PASSWORD = 'admin123'",
            description="Hardcoded password detected",
            remediation="Use environment variables",
        )
    ]

    reporter = JsonReporter()
    output = reporter.format(issues)

    assert "issue-001" in output
    assert "HIGH" in output
```

**구현**:
```python
# src/pysec/reporter/json_reporter.py
import json
from datetime import datetime
from pysec.scanner.models import SecurityIssue

class JsonReporter:
    """JSON 형식 리포터 (TAG-REQ-SEC-010)"""

    def format(self, issues: list[SecurityIssue], target_path: str) -> str:
        """이슈 리스트를 JSON으로 변환"""
        summary = self._generate_summary(issues)

        report = {
            "scan_id": f"scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "target_path": target_path,
            "summary": summary,
            "issues": [issue.model_dump() for issue in issues],
            "metadata": {
                "scanner": "Bandit",
                "pysec_version": "0.1.0",
            },
        }

        return json.dumps(report, indent=2, ensure_ascii=False)

    def _generate_summary(self, issues: list[SecurityIssue]) -> dict:
        """심각도별 통계 생성"""
        return {
            "total_issues": len(issues),
            "high": sum(1 for i in issues if i.severity == "HIGH"),
            "medium": sum(1 for i in issues if i.severity == "MEDIUM"),
            "low": sum(1 for i in issues if i.severity == "LOW"),
        }
```

**Test 2: 텍스트 리포터**
```python
def test_text_reporter_output():
    """텍스트 리포터 출력 테스트 (TAG-REQ-SEC-003)"""
    from pysec.reporter.text_reporter import TextReporter

    reporter = TextReporter()
    output = reporter.format(issues)

    assert "Security Scan Report" in output
    assert "🔴 HIGH" in output
```

**구현**:
```python
# src/pysec/reporter/text_reporter.py
from rich.console import Console
from rich.table import Table
from pysec.scanner.models import SecurityIssue

class TextReporter:
    """Rich 기반 텍스트 리포터 (TAG-REQ-SEC-003)"""

    def __init__(self):
        self.console = Console()

    def format(self, issues: list[SecurityIssue]) -> str:
        """이슈 리스트를 텍스트로 포맷"""
        summary = self._generate_summary(issues)

        output = []
        output.append("🔍 Security Scan Report")
        output.append("━" * 50)
        output.append(f"\n📊 Summary")
        output.append(f"  Total Issues: {summary['total_issues']}")
        output.append(f"  🔴 HIGH: {summary['high']}")
        output.append(f"  🟡 MEDIUM: {summary['medium']}")
        output.append(f"  🟢 LOW: {summary['low']}")
        output.append("\n" + "━" * 50)

        # 심각도별 이슈 출력
        for severity in ["HIGH", "MEDIUM", "LOW"]:
            severity_issues = [i for i in issues if i.severity == severity]
            if severity_issues:
                output.append(f"\n{self._severity_icon(severity)} {severity} Severity Issues\n")
                for idx, issue in enumerate(severity_issues, 1):
                    output.append(f"[{idx}] {issue.category}")
                    output.append(f"  File: {issue.file}:{issue.line}")
                    output.append(f"  Type: {issue.type}")
                    output.append(f"  Fix: {issue.remediation}\n")

        return "\n".join(output)

    def _severity_icon(self, severity: str) -> str:
        return {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[severity]
```

#### 구현 파일
- `src/pysec/reporter/__init__.py`
- `src/pysec/reporter/json_reporter.py`
- `src/pysec/reporter/text_reporter.py`

#### 예상 결과
- ✅ JSON 출력 정상 동작
- ✅ 텍스트 출력 정상 동작 (색상 포함)
- ✅ 심각도별 통계 정확

---

### 3.4 Phase 4: CLI 통합 (Final Goal)

#### 목표
- 모든 모듈을 CLI에 통합
- 진행률 표시
- 에러 처리 완성

#### TDD 순서

**Test 1: 전체 스캔 워크플로우**
```python
# tests/test_integration.py
def test_full_scan_workflow():
    """전체 스캔 워크플로우 통합 테스트 (TAG-REQ-SEC-005)"""
    from typer.testing import CliRunner
    from pysec.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["scan", "tests/fixtures/sample_project"])

    assert result.exit_code == 0
    assert "Security Scan Report" in result.stdout
    assert "Total Issues:" in result.stdout
```

**구현**:
```python
# src/pysec/cli/commands.py (완성)
from pathlib import Path
from typing import Annotated
import typer
from rich.progress import track
from loguru import logger

from pysec.scanner.bandit_engine import BanditScanner
from pysec.reporter.json_reporter import JsonReporter
from pysec.reporter.text_reporter import TextReporter

def scan(
    target_path: Annotated[Path, typer.Argument(help="스캔 대상 경로")],
    format: Annotated[str, typer.Option(help="출력 형식 (text|json)")] = "text",
    severity: Annotated[str, typer.Option(help="심각도 필터")] = "ALL",
    output: Annotated[Path | None, typer.Option(help="출력 파일")] = None,
    verbose: Annotated[bool, typer.Option(help="상세 로그")] = False,
):
    """Python 프로젝트 보안 스캔 (TAG-REQ-SEC-005)"""

    # 1. 경로 검증 (TAG-REQ-SEC-007)
    if not target_path.exists():
        logger.error(f"경로를 찾을 수 없습니다: {target_path}")
        raise typer.BadParameter(f"경로를 찾을 수 없습니다: {target_path}")

    # 2. Bandit 스캔 실행 (TAG-REQ-SEC-001)
    typer.echo("🔍 Starting security scan...")
    scanner = BanditScanner()

    try:
        result = scanner.scan(target_path)
        issues = scanner.parse_results(result.stdout)
    except Exception as e:
        logger.error(f"스캔 실패: {e}")
        raise typer.Abort()

    # 3. 심각도 필터링 (TAG-REQ-SEC-011)
    if severity != "ALL":
        issues = [i for i in issues if i.severity == severity]

    # 4. 리포트 생성 (TAG-REQ-SEC-003, TAG-REQ-SEC-010)
    if format == "json":
        reporter = JsonReporter()
        report_output = reporter.format(issues, str(target_path))
    else:
        reporter = TextReporter()
        report_output = reporter.format(issues)

    # 5. 출력
    if output:
        output.write_text(report_output)
        typer.echo(f"✅ 리포트 저장: {output}")
    else:
        typer.echo(report_output)

    # 6. 종료 코드 (취약점 발견 시 1)
    if issues:
        raise typer.Exit(code=1)
```

#### 구현 파일
- `src/pysec/cli/commands.py` (완성)

#### 예상 결과
- ✅ 전체 워크플로우 동작
- ✅ 에러 처리 완성
- ✅ 진행률 표시

---

## 4. 기술 아키텍처

### 4.1 계층 구조

```
┌─────────────────────────────────────┐
│         CLI Layer (Typer)           │  사용자 인터페이스
│  - main.py (엔트리포인트)            │
│  - commands.py (scan 명령어)        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Scanner Layer (Bandit)        │  보안 스캔 엔진
│  - bandit_engine.py (실행/파싱)     │
│  - models.py (데이터 모델)           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Reporter Layer (Output)       │  결과 출력
│  - json_reporter.py (JSON)          │
│  - text_reporter.py (Rich)          │
└─────────────────────────────────────┘
```

### 4.2 데이터 흐름

```
사용자 입력 (CLI)
    ↓
경로 검증 → Bandit 실행 → JSON 파싱
    ↓
SecurityIssue 모델 변환
    ↓
심각도 필터링 (옵션)
    ↓
Reporter 선택 (JSON/Text)
    ↓
출력 (stdout/file)
```

### 4.3 에러 처리 전략

```python
# 에러 계층 구조
class PysecError(Exception):
    """Base exception"""

class ScannerError(PysecError):
    """스캐너 실행 오류"""

class ParserError(PysecError):
    """결과 파싱 오류"""

class ValidationError(PysecError):
    """입력 검증 오류"""
```

---

## 5. 마일스톤

### Primary Goals (핵심 기능)

#### Milestone 1: CLI 인프라
- **목표**: 기본 CLI 구조 완성
- **산출물**:
  - ✅ `pysec scan` 명령어 동작
  - ✅ 경로 검증 및 에러 처리
  - ✅ 도움말 메시지
- **품질 기준**:
  - 테스트 커버리지 90% 이상
  - Mypy, Ruff 통과

#### Milestone 2: Bandit 통합
- **목표**: SAST 스캔 기능 완성
- **산출물**:
  - ✅ Bandit 실행 및 결과 파싱
  - ✅ SecurityIssue 모델 변환
  - ✅ OWASP 카테고리 매핑
- **품질 기준**:
  - 테스트 커버리지 85% 이상
  - 샘플 프로젝트 스캔 성공

### Secondary Goals (부가 기능)

#### Milestone 3: JSON 리포터
- **목표**: 프로그래밍 가능한 출력
- **산출물**:
  - ✅ JSON 직렬화
  - ✅ 심각도별 통계
- **품질 기준**:
  - JSON 스키마 유효성 검증

### Final Goals (완성도)

#### Milestone 4: 텍스트 리포터
- **목표**: 사용자 친화적 출력
- **산출물**:
  - ✅ Rich 기반 색상 출력
  - ✅ 프로그레스 바
- **품질 기준**:
  - 터미널에서 가독성 확인

#### Milestone 5: 통합 및 배포 준비
- **목표**: MVP 완성
- **산출물**:
  - ✅ 전체 통합 테스트 통과
  - ✅ README.md 작성
  - ✅ PyPI 배포 준비
- **품질 기준**:
  - TRUST 5 원칙 모두 준수
  - Definition of Done 모두 체크

---

## 6. 위험 관리

### 6.1 기술적 위험

#### Risk 1: Bandit 설치 문제
**확률**: MEDIUM
**영향**: HIGH

**완화 전략**:
- ✅ pyproject.toml에 명시적 버전 지정
- ✅ 설치 가이드 문서 작성
- ✅ CI/CD에서 자동 설치 테스트

**대응 계획**:
- Bandit 미설치 시 명확한 에러 메시지
- 설치 명령어 제공

#### Risk 2: 크로스 플랫폼 호환성
**확률**: LOW
**영향**: MEDIUM

**완화 전략**:
- ✅ `pathlib` 사용으로 경로 처리 통일
- ✅ Windows/Linux/macOS CI 테스트

**대응 계획**:
- 플랫폼별 픽스처 준비
- 조건부 로직 최소화

### 6.2 프로세스 위험

#### Risk 3: 테스트 커버리지 미달
**확률**: LOW
**영향**: HIGH

**완화 전략**:
- ✅ pytest-cov로 자동 측정
- ✅ 85% 미만 시 CI 실패 설정

**대응 계획**:
- 누락된 테스트 우선 작성
- 엣지 케이스 추가

---

## 7. 품질 보증

### 7.1 자동화된 품질 검사

#### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# 1. 정적 분석
echo "🔍 Running Mypy..."
uv run mypy src/pysec

echo "🔍 Running Ruff..."
uv run ruff check src/pysec

# 2. 테스트
echo "🧪 Running tests..."
uv run pytest

# 3. 커버리지 체크
echo "📊 Checking coverage..."
uv run pytest --cov=src/pysec --cov-fail-under=85

if [ $? -ne 0 ]; then
    echo "❌ Quality checks failed!"
    exit 1
fi

echo "✅ All checks passed!"
```

#### CI/CD (GitHub Actions)
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: [3.11, 3.12]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install UV
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run Mypy
        run: uv run mypy src/pysec

      - name: Run Ruff
        run: uv run ruff check src/pysec

      - name: Run tests
        run: uv run pytest --cov=src/pysec --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 7.2 TRUST 5 체크리스트

#### T - Test-first
- [ ] 모든 코드는 테스트 작성 후 구현
- [ ] 테스트 커버리지 85% 이상
- [ ] 단위 테스트 + 통합 테스트 모두 작성

#### R - Readable
- [ ] Mypy 타입 체크 100% 통과
- [ ] Ruff 린팅 규칙 모두 준수
- [ ] Docstring 작성 (Google 스타일)

#### U - Unified
- [ ] Pydantic 모델 일관적 사용
- [ ] 에러 처리 표준화
- [ ] 로깅 포맷 통일

#### S - Secured
- [ ] 사용자 입력 검증 (경로 검증)
- [ ] 서브프로세스 안전 실행 (shell=False)
- [ ] 민감 정보 노출 방지

#### T - Trackable
- [ ] 모든 커밋에 TAG 포함
- [ ] SPEC 문서와 코드 동기화
- [ ] TAG 체인으로 추적성 보장

---

## 8. 다음 단계

### MVP 완성 후

1. **SPEC-SECURITY-002**: SCA + DAST 통합
   - Safety, pip-audit 통합
   - OWASP ZAP 통합
   - 의존성 CVE 검사

2. **SPEC-SECURITY-003**: 웹 대시보드 + MCP
   - FastAPI 백엔드
   - Streamlit 프론트엔드
   - Context7 MCP 통합
   - Claude Code security-expert 에이전트

3. **배포 및 유지보수**
   - PyPI 배포
   - 문서 사이트 (MkDocs)
   - 사용자 피드백 수집

---

**문서 버전**: 0.1.0
**최종 수정**: 2025-11-17
**다음 단계**: `/alfred:2-run SPEC-SECURITY-001` 실행
