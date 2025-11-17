# SPEC-SECURITY-001 인수 기준 (Acceptance Criteria)

## TAG BLOCK

```yaml
spec_id: SPEC-SECURITY-001
title: Python 보안 스캐너 MVP - 인수 기준
document_type: acceptance_criteria
version: 0.1.0
created: 2025-11-17
priority: HIGH
```

---

## 📋 목차

1. [인수 테스트 시나리오](#1-인수-테스트-시나리오)
2. [품질 게이트](#2-품질-게이트)
3. [Definition of Done](#3-definition-of-done)
4. [검증 방법](#4-검증-방법)

---

## 1. 인수 테스트 시나리오 (Given-When-Then)

### Scenario 1: 기본 스캔 실행 (TAG-REQ-SEC-005)

**Given**: 사용자가 Python 프로젝트 디렉토리를 가지고 있다
**When**: `pysec scan ./my_project` 명령어를 실행한다
**Then**:
- ✅ Bandit 스캐너가 실행된다
- ✅ 스캔 진행률이 프로그레스 바로 표시된다
- ✅ 스캔 완료 후 텍스트 리포트가 터미널에 출력된다
- ✅ 리포트에는 다음 정보가 포함된다:
  - 총 이슈 개수
  - 심각도별 통계 (HIGH/MEDIUM/LOW)
  - 각 취약점의 상세 정보 (파일명, 라인, 설명, 수정 방법)

**테스트 코드**:
```python
# tests/acceptance/test_basic_scan.py
def test_basic_scan_execution():
    """기본 스캔 실행 인수 테스트 (TAG-REQ-SEC-005)"""
    from typer.testing import CliRunner
    from pysec.cli.main import app

    # Given: 샘플 프로젝트 준비
    runner = CliRunner()

    # When: 스캔 실행
    result = runner.invoke(app, ["scan", "tests/fixtures/sample_project"])

    # Then: 출력 검증
    assert result.exit_code in [0, 1]  # 0: 이슈 없음, 1: 이슈 발견
    assert "Security Scan Report" in result.stdout
    assert "Total Issues:" in result.stdout
    assert "Summary" in result.stdout
```

**검증 방법**:
```bash
# 수동 검증
cd tests/fixtures/sample_project
pysec scan .

# 예상 출력:
# 🔍 Security Scan Report
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 Summary
#   Total Issues: 3
#   🔴 HIGH: 1
#   🟡 MEDIUM: 1
#   🟢 LOW: 1
```

---

### Scenario 2: JSON 출력 형식 (TAG-REQ-SEC-010)

**Given**: 사용자가 프로그래밍 가능한 형식으로 결과를 받고 싶다
**When**: `pysec scan ./my_project --format json` 명령어를 실행한다
**Then**:
- ✅ JSON 형식으로 결과가 출력된다
- ✅ JSON은 유효한 구조를 가진다 (파싱 가능)
- ✅ 다음 필드들이 포함된다:
  - `scan_id`: 고유 스캔 ID
  - `timestamp`: 스캔 시간
  - `target_path`: 스캔 대상 경로
  - `summary`: 통계 정보
  - `issues`: 취약점 리스트
  - `metadata`: 메타데이터 (버전 정보 등)

**테스트 코드**:
```python
# tests/acceptance/test_json_output.py
import json

def test_json_output_format():
    """JSON 출력 인수 테스트 (TAG-REQ-SEC-010)"""
    from typer.testing import CliRunner
    from pysec.cli.main import app

    # Given: CLI runner 준비
    runner = CliRunner()

    # When: JSON 형식 스캔
    result = runner.invoke(
        app,
        ["scan", "tests/fixtures/sample_project", "--format", "json"]
    )

    # Then: JSON 유효성 검증
    assert result.exit_code in [0, 1]

    output = json.loads(result.stdout)
    assert "scan_id" in output
    assert "timestamp" in output
    assert "summary" in output
    assert "issues" in output
    assert output["summary"]["total_issues"] >= 0
```

**검증 방법**:
```bash
# JSON 출력 검증
pysec scan . --format json | jq .

# 예상 출력:
# {
#   "scan_id": "scan-20251117-143022",
#   "timestamp": "2025-11-17T14:30:22Z",
#   "summary": {
#     "total_issues": 3,
#     "high": 1,
#     "medium": 1,
#     "low": 1
#   },
#   "issues": [...]
# }
```

---

### Scenario 3: 심각도 필터링 (TAG-REQ-SEC-011)

**Given**: 사용자가 HIGH 심각도 취약점만 보고 싶다
**When**: `pysec scan ./my_project --severity HIGH` 명령어를 실행한다
**Then**:
- ✅ HIGH 심각도 취약점만 리포트에 표시된다
- ✅ MEDIUM, LOW 취약점은 제외된다
- ✅ 통계에는 필터링된 결과만 반영된다

**테스트 코드**:
```python
# tests/acceptance/test_severity_filter.py
def test_severity_filtering():
    """심각도 필터링 인수 테스트 (TAG-REQ-SEC-011)"""
    from typer.testing import CliRunner
    from pysec.cli.main import app
    import json

    # Given: CLI runner
    runner = CliRunner()

    # When: HIGH만 필터링
    result = runner.invoke(
        app,
        ["scan", "tests/fixtures/sample_project", "--severity", "HIGH", "--format", "json"]
    )

    # Then: HIGH만 포함되는지 검증
    output = json.loads(result.stdout)
    issues = output["issues"]

    for issue in issues:
        assert issue["severity"] == "HIGH"
```

**검증 방법**:
```bash
# HIGH 심각도만 필터링
pysec scan . --severity HIGH

# 예상 출력:
# 🔍 Security Scan Report
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 Summary
#   Total Issues: 1
#   🔴 HIGH: 1
```

---

### Scenario 4: 파일 출력 (TAG-REQ-SEC-010)

**Given**: 사용자가 스캔 결과를 파일로 저장하고 싶다
**When**: `pysec scan ./my_project --format json --output report.json` 명령어를 실행한다
**Then**:
- ✅ `report.json` 파일이 생성된다
- ✅ 파일 내용은 유효한 JSON이다
- ✅ 터미널에는 "✅ 리포트 저장: report.json" 메시지가 출력된다

**테스트 코드**:
```python
# tests/acceptance/test_file_output.py
import tempfile
from pathlib import Path

def test_file_output():
    """파일 출력 인수 테스트 (TAG-REQ-SEC-010)"""
    from typer.testing import CliRunner
    from pysec.cli.main import app
    import json

    # Given: 임시 출력 파일
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        output_path = Path(f.name)

    try:
        # When: 파일로 출력
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "scan",
                "tests/fixtures/sample_project",
                "--format", "json",
                "--output", str(output_path),
            ]
        )

        # Then: 파일 생성 및 내용 검증
        assert result.exit_code in [0, 1]
        assert output_path.exists()

        content = json.loads(output_path.read_text())
        assert "scan_id" in content

    finally:
        output_path.unlink(missing_ok=True)
```

**검증 방법**:
```bash
# 파일로 저장
pysec scan . --format json --output report.json

# 파일 확인
cat report.json | jq .
```

---

### Scenario 5: 잘못된 경로 처리 (TAG-REQ-SEC-007)

**Given**: 사용자가 존재하지 않는 경로를 입력한다
**When**: `pysec scan /nonexistent/path` 명령어를 실행한다
**Then**:
- ✅ 에러 메시지가 출력된다: "경로를 찾을 수 없습니다: /nonexistent/path"
- ✅ 종료 코드는 1 (실패)이다
- ✅ 도움말 힌트가 표시된다

**테스트 코드**:
```python
# tests/acceptance/test_error_handling.py
def test_invalid_path_handling():
    """잘못된 경로 처리 인수 테스트 (TAG-REQ-SEC-007)"""
    from typer.testing import CliRunner
    from pysec.cli.main import app

    # Given: 존재하지 않는 경로
    runner = CliRunner()

    # When: 스캔 시도
    result = runner.invoke(app, ["scan", "/nonexistent/path"])

    # Then: 에러 메시지 검증
    assert result.exit_code != 0
    assert "경로를 찾을 수 없습니다" in result.stdout
```

**검증 방법**:
```bash
# 잘못된 경로 테스트
pysec scan /nonexistent/path

# 예상 출력:
# Error: 경로를 찾을 수 없습니다: /nonexistent/path
# Try 'pysec scan --help' for help.
```

---

### Scenario 6: Bandit 실행 실패 처리 (TAG-REQ-SEC-008)

**Given**: Bandit이 설치되지 않았거나 실행 중 오류가 발생한다
**When**: 스캔을 시도한다
**Then**:
- ✅ 명확한 에러 메시지가 출력된다
- ✅ 디버깅 정보가 제공된다 (Bandit 버전, 명령어)
- ✅ 종료 코드는 2 (시스템 오류)이다

**테스트 코드**:
```python
# tests/acceptance/test_bandit_failure.py
from unittest.mock import patch
import subprocess

def test_bandit_execution_failure():
    """Bandit 실행 실패 인수 테스트 (TAG-REQ-SEC-008)"""
    from typer.testing import CliRunner
    from pysec.cli.main import app

    # Given: Bandit 실행 실패 시뮬레이션
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError("bandit not found")

        # When: 스캔 시도
        runner = CliRunner()
        result = runner.invoke(app, ["scan", "tests/fixtures/sample_project"])

        # Then: 에러 처리 검증
        assert result.exit_code != 0
        assert "스캔 실패" in result.stdout or "Aborted" in result.stdout
```

**검증 방법**:
```bash
# Bandit 임시 제거 후 테스트 (수동)
# (실제로는 Mock을 사용하므로 불필요)
```

---

### Scenario 7: 진행률 표시 (TAG-REQ-SEC-009)

**Given**: 대규모 프로젝트를 스캔한다
**When**: 스캔이 진행된다
**Then**:
- ✅ 프로그레스 바가 표시된다
- ✅ 현재 스캔 중인 파일이 표시된다
- ✅ 발견된 이슈 카운트가 실시간으로 업데이트된다

**테스트 코드**:
```python
# tests/acceptance/test_progress_display.py
def test_progress_display():
    """진행률 표시 인수 테스트 (TAG-REQ-SEC-009)"""
    from typer.testing import CliRunner
    from pysec.cli.main import app

    # Given: 샘플 프로젝트
    runner = CliRunner()

    # When: 스캔 실행
    result = runner.invoke(app, ["scan", "tests/fixtures/sample_project"])

    # Then: 진행 메시지 검증
    assert "Starting security scan" in result.stdout or "Scanning" in result.stdout
```

**검증 방법**:
```bash
# 대규모 프로젝트 스캔 (수동)
pysec scan /path/to/large/project

# 예상 출력:
# 🔍 Starting security scan...
# Scanning... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:05
```

---

## 2. 품질 게이트

### 2.1 테스트 커버리지

**기준**: 85% 이상

**검증 방법**:
```bash
uv run pytest --cov=src/pysec --cov-report=term-missing --cov-fail-under=85
```

**예상 결과**:
```
---------- coverage: platform linux, python 3.11.5 -----------
Name                                   Stmts   Miss  Cover   Missing
--------------------------------------------------------------------
src/pysec/__init__.py                      0      0   100%
src/pysec/cli/__init__.py                  0      0   100%
src/pysec/cli/main.py                     15      2    87%   45-46
src/pysec/cli/commands.py                 42      5    88%   67-71
src/pysec/scanner/__init__.py              0      0   100%
src/pysec/scanner/bandit_engine.py        58      7    88%   89-95
src/pysec/scanner/models.py               25      0   100%
src/pysec/reporter/__init__.py             0      0   100%
src/pysec/reporter/json_reporter.py       32      3    91%   56-58
src/pysec/reporter/text_reporter.py       38      5    87%   72-76
--------------------------------------------------------------------
TOTAL                                    210     22    90%
```

### 2.2 정적 분석

#### Mypy (타입 체크)

**기준**: 100% 타입 안전성

**검증 방법**:
```bash
uv run mypy src/pysec
```

**예상 결과**:
```
Success: no issues found in 10 source files
```

#### Ruff (린팅)

**기준**: 모든 규칙 통과

**검증 방법**:
```bash
uv run ruff check src/pysec
```

**예상 결과**:
```
All checks passed!
```

### 2.3 보안 검사

**기준**: 자체 도구로 스캔 시 HIGH 심각도 이슈 0개

**검증 방법**:
```bash
# 자기 자신 스캔 (Dogfooding)
pysec scan src/pysec --severity HIGH
```

**예상 결과**:
```
📊 Summary
  Total Issues: 0
  🔴 HIGH: 0
```

---

## 3. Definition of Done

### 3.1 기능 완성도

- [ ] **CLI 명령어**: `pysec scan` 동작
- [ ] **Bandit 통합**: SAST 스캔 성공
- [ ] **JSON 출력**: `--format json` 동작
- [ ] **텍스트 출력**: 기본 텍스트 리포트 출력
- [ ] **심각도 필터**: `--severity` 옵션 동작
- [ ] **파일 출력**: `--output` 옵션 동작
- [ ] **에러 처리**: 잘못된 경로, Bandit 실패 처리
- [ ] **진행률 표시**: 프로그레스 바 동작

### 3.2 품질 기준

- [ ] **테스트 커버리지**: 85% 이상 ✅
- [ ] **Mypy**: 타입 체크 100% 통과 ✅
- [ ] **Ruff**: 린팅 규칙 모두 준수 ✅
- [ ] **보안**: 자체 스캔 HIGH 이슈 0개 ✅

### 3.3 문서화

- [ ] **README.md**: 설치, 사용법, 예제 작성
- [ ] **Docstring**: 모든 함수/클래스 문서화 (Google 스타일)
- [ ] **CHANGELOG.md**: v0.1.0 릴리스 노트 작성

### 3.4 배포 준비

- [ ] **pyproject.toml**: 메타데이터 완성
- [ ] **LICENSE**: MIT 라이선스 추가
- [ ] **CI/CD**: GitHub Actions 설정
- [ ] **배포 테스트**: `uv build` 성공

---

## 4. 검증 방법

### 4.1 자동화된 검증

#### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Running quality checks..."

# 1. Mypy
uv run mypy src/pysec || exit 1

# 2. Ruff
uv run ruff check src/pysec || exit 1

# 3. Tests
uv run pytest --cov=src/pysec --cov-fail-under=85 || exit 1

echo "✅ All checks passed!"
```

#### CI/CD 파이프라인
```yaml
# .github/workflows/ci.yml
name: Quality Gate

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install UV
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run Mypy
        run: uv run mypy src/pysec

      - name: Run Ruff
        run: uv run ruff check src/pysec

      - name: Run tests
        run: uv run pytest --cov=src/pysec --cov-fail-under=85

      - name: Self-scan
        run: uv run pysec scan src/pysec --severity HIGH
```

### 4.2 수동 검증 체크리스트

#### 사용자 시나리오 테스트

1. **설치 테스트**
   ```bash
   # 신규 환경에서 설치
   pip install pysec
   pysec --help
   ```

2. **기본 스캔 테스트**
   ```bash
   # 샘플 프로젝트 스캔
   git clone https://github.com/example/vulnerable-app
   pysec scan vulnerable-app
   ```

3. **JSON 출력 테스트**
   ```bash
   pysec scan . --format json | jq .
   ```

4. **필터링 테스트**
   ```bash
   pysec scan . --severity HIGH
   ```

5. **파일 저장 테스트**
   ```bash
   pysec scan . --format json --output report.json
   cat report.json
   ```

6. **에러 처리 테스트**
   ```bash
   pysec scan /nonexistent/path  # 에러 메시지 확인
   ```

### 4.3 성능 검증

#### 벤치마크 테스트

**테스트 케이스**:
- 소규모 프로젝트 (10 파일, 500 줄)
- 중규모 프로젝트 (100 파일, 5,000 줄)
- 대규모 프로젝트 (1,000 파일, 50,000 줄)

**측정 항목**:
- 스캔 시간
- 메모리 사용량
- CPU 사용률

**기준**:
- 중규모 프로젝트 스캔: 30초 이내
- 메모리 사용: 500MB 이하

**검증 방법**:
```bash
# 시간 측정
time pysec scan /path/to/project

# 메모리 측정 (Linux)
/usr/bin/time -v pysec scan /path/to/project
```

---

## 5. 인수 확인서

### 5.1 체크리스트

**기능 검증**:
- [ ] 모든 Given-When-Then 시나리오 통과 (7개)
- [ ] CLI 명령어 정상 동작
- [ ] JSON/텍스트 출력 정상
- [ ] 에러 처리 완료

**품질 검증**:
- [ ] 테스트 커버리지 85% 이상
- [ ] Mypy 타입 체크 100%
- [ ] Ruff 린팅 규칙 준수
- [ ] 보안 스캔 통과 (HIGH 이슈 0개)

**문서화 검증**:
- [ ] README.md 완성
- [ ] Docstring 작성
- [ ] CHANGELOG.md 작성

**배포 검증**:
- [ ] pyproject.toml 완성
- [ ] CI/CD 설정 완료
- [ ] 빌드 테스트 성공

### 5.2 승인 기준

**MVP 완성 기준**:
- ✅ 위 모든 체크리스트 항목 완료
- ✅ 수동 검증 시나리오 모두 통과
- ✅ 성능 벤치마크 기준 충족

**승인 시 다음 단계**:
1. Git 태그 생성: `v0.1.0`
2. GitHub Release 배포
3. SPEC-SECURITY-002 계획 시작 (SCA + DAST 통합)

---

**문서 버전**: 0.1.0
**최종 수정**: 2025-11-17
**검증 책임**: @user
**승인 필요**: TRUST 5 품질 게이트 모두 통과 시
