# SPEC-SECURITY-002 인수 기준 (Acceptance Criteria)

## TAG BLOCK

```yaml
spec_id: SPEC-SECURITY-002
title: DAST with OWASP ZAP - 인수 기준
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

### Scenario 1: 기본 DAST 스캔 실행 (TAG-REQ-DAST-005)

**Given**: 사용자가 테스트 웹 애플리케이션과 OWASP ZAP 인스턴스를 가지고 있다

**When**: `pysec run-dast http://localhost:5000` 명령어를 실행한다

**Then**:
- ✅ ZAP 연결이 확인된다 (헬스 체크)
- ✅ 타겟 URL이 검증된다
- ✅ Spider 스캔이 시작된다
- ✅ 스캔 진행률이 Rich 프로그레스 바로 표시된다
- ✅ 스캔 완료 후 텍스트 리포트가 출력된다
- ✅ 리포트에는 다음 정보가 포함된다:
  - 스캔 ID, 타임스탬프, 대상 URL
  - 총 Alert 개수
  - 심각도별 통계 (HIGH/MEDIUM/LOW/INFO)
  - 각 취약점의 상세 정보

**테스트 코드**:
```python
# tests/acceptance/test_dast_basic_scan.py
import pytest
from typer.testing import CliRunner
from pysec.cli.main import app

@pytest.mark.asyncio
def test_basic_dast_scan():
    """기본 DAST 스캔 인수 테스트 (TAG-REQ-DAST-005)"""

    runner = CliRunner()

    # Given: Docker로 실행되는 ZAP과 테스트 웹앱
    # (CI/CD에서 docker-compose로 준비됨)

    # When: DAST 스캔 실행
    result = runner.invoke(app, [
        "run-dast",
        "http://localhost:5000"
    ])

    # Then: 출력 검증
    assert result.exit_code in [0, 1]  # 0: 이슈 없음, 1: 이슈 발견
    assert "Security Scan Report" in result.stdout
    assert "Target URL:" in result.stdout
    assert "Scan Summary" in result.stdout or "No alerts found" in result.stdout
```

**검증 방법**:
```bash
# 1. ZAP 서버 시작 (Docker)
docker run -d \
  -p 8080:8080 \
  --name zap \
  owasp/zap2docker-stable \
  zap.sh -cmd -port 8080

# 2. 테스트 웹 애플리케이션 시작
docker run -d \
  -p 5000:5000 \
  --name vulnerable-app \
  my-test-app:latest

# 3. DAST 스캔 실행
pysec run-dast http://localhost:5000

# 4. 출력 검증
# 예상 출력:
# 🔍 DAST Security Scan Report
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 Scan Summary
#   Target URL: http://localhost:5000
#   Duration: 45 seconds
#   🔴 HIGH: 1
#   🟡 MEDIUM: 2
#   🔵 LOW: 1
```

---

### Scenario 2: JSON 출력 형식 (TAG-REQ-DAST-014)

**Given**: 사용자가 프로그래밍 가능한 형식으로 결과를 받고 싶다

**When**: `pysec run-dast http://localhost:5000 --format json` 명령어를 실행한다

**Then**:
- ✅ JSON 형식으로 결과가 출력된다
- ✅ JSON은 유효한 구조를 가진다 (파싱 가능)
- ✅ 다음 필드들이 포함된다:
  - `scan_id`: 고유 스캔 ID
  - `timestamp`: 스캔 시간 (ISO 8601)
  - `target_url`: 스캔 대상 URL
  - `zap_version`: ZAP 버전
  - `summary`: 통계 정보 (HIGH/MEDIUM/LOW/INFO)
  - `alerts`: 취약점 리스트
  - `metadata`: 메타데이터 (스캐너, 버전 등)

**테스트 코드**:
```python
# tests/acceptance/test_dast_json_output.py
import json

@pytest.mark.asyncio
def test_dast_json_output():
    """DAST JSON 출력 인수 테스트 (TAG-REQ-DAST-014)"""

    runner = CliRunner()

    # When: JSON 형식으로 스캔 실행
    result = runner.invoke(app, [
        "run-dast",
        "http://localhost:5000",
        "--format", "json"
    ])

    # Then: JSON 검증
    assert result.exit_code in [0, 1]

    # JSON 파싱 가능성
    report = json.loads(result.stdout)

    # 필수 필드 확인
    assert "scan_id" in report
    assert "timestamp" in report
    assert "target_url" in report
    assert "zap_version" in report
    assert "summary" in report
    assert "alerts" in report
    assert "metadata" in report

    # 데이터 타입 확인
    assert isinstance(report["alerts"], list)
    assert isinstance(report["summary"], dict)
    assert "high" in report["summary"]
    assert "medium" in report["summary"]
    assert "low" in report["summary"]
```

**검증 방법**:
```bash
# JSON 출력 저장 및 검증
pysec run-dast http://localhost:5000 --format json > dast-report.json

# JSON 유효성 검사
python3 -c "import json; json.load(open('dast-report.json'))"

# jq로 필드 확인
jq '.scan_id, .timestamp, .summary' dast-report.json
```

---

### Scenario 3: 잘못된 URL 처리 (TAG-REQ-DAST-007)

**Given**: 사용자가 유효하지 않은 URL을 제공한다

**When**: `pysec run-dast not-a-url` 또는 `pysec run-dast http://nonexistent.local` 명령을 실행한다

**Then**:
- ✅ URL 형식 검증 오류가 출력된다
- ✅ 오류 메시지가 명확하고 도움이 된다
- ✅ 사용 예제가 제시된다
- ✅ 종료 코드가 1로 설정된다

**테스트 코드**:
```python
# tests/acceptance/test_dast_error_handling.py
def test_invalid_url_handling():
    """잘못된 URL 처리 인수 테스트 (TAG-REQ-DAST-007)"""

    runner = CliRunner()

    # Test 1: URL 형식 오류
    result = runner.invoke(app, [
        "run-dast",
        "not-a-valid-url"
    ])

    assert result.exit_code == 1
    assert "Invalid URL" in result.stdout or "URL format" in result.stdout

    # Test 2: 접근 불가능한 URL
    result = runner.invoke(app, [
        "run-dast",
        "http://this-domain-does-not-exist-12345.local"
    ])

    assert result.exit_code == 1
    assert "not reachable" in result.stdout or "connection" in result.stdout.lower()
```

**검증 방법**:
```bash
# 유효하지 않은 URL 테스트
pysec run-dast invalid-url 2>&1
# 예상 출력:
# ❌ Error: Invalid URL format. Please provide a valid HTTP/HTTPS URL.
# Usage: pysec run-dast <TARGET_URL> [OPTIONS]
# Example: pysec run-dast http://example.com

# 접근 불가능한 URL 테스트
pysec run-dast http://nonexistent.local 2>&1
# 예상 출력:
# ❌ Error: Target URL is not reachable. Please verify the URL.
```

---

### Scenario 4: ZAP 연결 실패 (TAG-REQ-DAST-008)

**Given**: OWASP ZAP 인스턴스가 실행되지 않음

**When**: `pysec run-dast http://localhost:5000` 명령을 실행한다

**Then**:
- ✅ ZAP 연결 실패 메시지가 출력된다
- ✅ 설치 및 실행 가이드가 제공된다
- ✅ 디버깅 정보가 표시된다 (호스트, 포트)
- ✅ 종료 코드가 2로 설정된다

**테스트 코드**:
```python
def test_zap_connection_failure():
    """ZAP 연결 실패 인수 테스트 (TAG-REQ-DAST-008)"""

    runner = CliRunner()

    # ZAP이 실행되지 않은 상태에서 스캔 시도
    result = runner.invoke(app, [
        "run-dast",
        "http://localhost:5000",
        "--zap-host", "localhost",
        "--zap-port", "9999"  # 존재하지 않는 포트
    ])

    assert result.exit_code == 2
    assert "OWASP ZAP" in result.stdout or "connection" in result.stdout.lower()
    assert "localhost" in result.stdout
    assert "9999" in result.stdout
```

**검증 방법**:
```bash
# ZAP 서버 미실행 상태에서 스캔 실행
pysec run-dast http://localhost:5000 2>&1
# 예상 출력:
# ❌ Error: Cannot connect to OWASP ZAP at localhost:8080
#
# Please install and run OWASP ZAP:
#   Docker: docker run -p 8080:8080 owasp/zap2docker-stable
#   Manual: https://www.zaproxy.org/download/
#
# Debug info:
#   Host: localhost
#   Port: 8080
#   Timeout: 5s
```

---

### Scenario 5: 심각도 및 신뢰도 필터링 (TAG-REQ-DAST-013)

**Given**: DAST 스캔이 여러 수준의 취약점을 발견했다

**When**: `pysec run-dast http://localhost:5000 --severity HIGH --confidence HIGH` 명령을 실행한다

**Then**:
- ✅ HIGH 심각도만 필터링된다
- ✅ HIGH 신뢰도만 필터링된다
- ✅ 필터된 결과만 리포트에 포함된다
- ✅ 요약에 필터 정보가 표시된다

**테스트 코드**:
```python
def test_severity_confidence_filtering():
    """심각도/신뢰도 필터링 인수 테스트 (TAG-REQ-DAST-013)"""

    runner = CliRunner()

    # HIGH 심각도 + HIGH 신뢰도 필터링
    result = runner.invoke(app, [
        "run-dast",
        "http://localhost:5000",
        "--severity", "HIGH",
        "--confidence", "HIGH"
    ])

    assert result.exit_code in [0, 1]

    # 필터링 결과 검증
    report = json.loads(result.stdout)

    # 모든 Alert이 HIGH 심각도를 가져야 함
    for alert in report["alerts"]:
        assert alert["severity"] == "HIGH"
        assert alert["confidence"] == "HIGH"
```

**검증 방법**:
```bash
# HIGH 심각도만 필터링
pysec run-dast http://localhost:5000 \
  --severity HIGH \
  --format json | jq '.alerts[] | .severity'
# 출력: "HIGH" (모두)

# HIGH 신뢰도만 필터링
pysec run-dast http://localhost:5000 \
  --confidence HIGH \
  --format json | jq '.alerts[] | .confidence'
# 출력: "HIGH" (모두)
```

---

### Scenario 6: 진행률 표시 (TAG-REQ-DAST-010)

**Given**: 사용자가 DAST 스캔을 실행한다

**When**: 스캔이 진행 중일 때

**Then**:
- ✅ Rich 프로그레스 바가 표시된다
- ✅ 진행률이 0~100%로 업데이트된다
- ✅ 현재 단계가 표시된다 (Setup → Spider → Passive Scan → Complete)
- ✅ 발견된 Alert 개수가 실시간 업데이트된다
- ✅ 경과 시간이 표시된다

**테스트 코드**:
```python
@pytest.mark.asyncio
def test_progress_display():
    """진행률 표시 인수 테스트 (TAG-REQ-DAST-010)"""

    runner = CliRunner()

    result = runner.invoke(app, [
        "run-dast",
        "http://localhost:5000",
        "--verbose"  # 상세 로그
    ])

    assert result.exit_code in [0, 1]

    # 진행 단계 확인
    assert "Setup" in result.stdout or "Connecting" in result.stdout
    assert "Scanning" in result.stdout or "Spider" in result.stdout
    assert "100%" in result.stdout or "Complete" in result.stdout
```

**검증 방법**:
```bash
# 스캔 실행 및 진행률 확인
pysec run-dast http://localhost:5000

# 예상 출력:
# 🔍 DAST Security Scan
# [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 25% | Setup
# [████████████████░░░░░░░░░░░░░░░░░░░░░░] 50% | Spider
# [████████████████████████░░░░░░░░░░░░░░░] 75% | Passive Scan
# [██████████████████████████████████████] 100% | Complete
#
# ✅ Scan completed in 45 seconds. 5 alerts found.
```

---

### Scenario 7: SAST + DAST 통합 스캔 (TAG-REQ-DAST-011)

**Given**: 사용자가 로컬 코드와 웹 애플리케이션을 모두 스캔하고 싶다

**When**: `pysec run-dast http://localhost:5000 --include-sast ./src` 명령을 실행한다

**Then**:
- ✅ SAST 스캔이 먼저 실행된다
- ✅ DAST 스캔이 다음으로 실행된다
- ✅ 최종 리포트에 모든 취약점이 통합된다
- ✅ SAST와 DAST 결과가 구분되어 표시된다

**테스트 코드**:
```python
def test_integrated_sast_dast_scan():
    """SAST+DAST 통합 스캔 인수 테스트 (TAG-REQ-DAST-011)"""

    runner = CliRunner()

    result = runner.invoke(app, [
        "run-dast",
        "http://localhost:5000",
        "--include-sast", "tests/fixtures/sample_project",
        "--format", "json"
    ])

    assert result.exit_code in [0, 1]

    report = json.loads(result.stdout)

    # SAST 결과 확인
    assert "sast_results" in report or "sast_summary" in report

    # DAST 결과 확인
    assert "dast_results" in report or "alerts" in report

    # 통합 요약 확인
    assert "combined_summary" in report
```

**검증 방법**:
```bash
# SAST + DAST 통합 스캔
pysec run-dast http://localhost:5000 \
  --include-sast ./src \
  --format json | jq '.combined_summary'

# 예상 출력:
# {
#   "total_issues": 10,
#   "sast_issues": 3,
#   "dast_issues": 7,
#   "high": 4,
#   "medium": 4,
#   "low": 2
# }
```

---

### Scenario 8: 파일로 결과 저장 (TAG-REQ-DAST-014)

**Given**: 사용자가 스캔 결과를 파일로 저장하고 싶다

**When**: `pysec run-dast http://localhost:5000 --format json --output report.json` 명령을 실행한다

**Then**:
- ✅ JSON 리포트가 `report.json` 파일로 저장된다
- ✅ 파일이 유효한 JSON을 포함한다
- ✅ 파일의 구조와 콘텐츠가 정상이다
- ✅ 터미널에 저장 확인 메시지가 출력된다

**테스트 코드**:
```python
def test_output_to_file():
    """파일 저장 인수 테스트"""

    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(app, [
            "run-dast",
            "http://localhost:5000",
            "--format", "json",
            "--output", "report.json"
        ])

        assert result.exit_code in [0, 1]
        assert "report.json" in result.stdout

        # 파일 존재 확인
        import os
        assert os.path.exists("report.json")

        # JSON 유효성 확인
        with open("report.json") as f:
            report = json.load(f)
            assert "scan_id" in report
            assert "alerts" in report
```

**검증 방법**:
```bash
# 결과를 파일로 저장
pysec run-dast http://localhost:5000 \
  --format json \
  --output dast-report.json

# 파일 확인
ls -la dast-report.json
wc -l dast-report.json

# JSON 검증
python3 -c "import json; print(json.dumps(json.load(open('dast-report.json')), indent=2))"
```

---

## 2. 품질 게이트

### 2.1 정적 분석 검사

#### Mypy 타입 체크
```bash
# 모든 코드가 strict mode에서 통과해야 함
uv run mypy src/pysec --strict

# 예상 결과: Success: no issues found in 15 source files
```

#### Ruff 린팅
```bash
# 모든 린팅 규칙 준수
uv run ruff check src/pysec

# 예상 결과: 0 errors, 0 warnings
```

### 2.2 테스트 커버리지

#### 최소 커버리지: 85%
```bash
# 커버리지 측정 및 검증
uv run pytest tests/ --cov=src/pysec --cov-report=html

# Coverage thresholds:
# - Overall: >= 85%
# - dast_engine.py: >= 90%
# - cli/commands.py (dast): >= 85%
# - reporter/*.py: >= 80%
```

### 2.3 보안 검사

#### OWASP 취약점 스캔
```bash
# Bandit을 사용한 Python 보안 검사
uv run bandit -r src/pysec --severity-level high

# 예상 결과: No issues identified
```

#### 의존성 취약점
```bash
# pip-audit으로 의존성 검사
uv run pip-audit

# 예상 결과: No known vulnerabilities found
```

---

## 3. Definition of Done

### 코드 완성도

- [ ] 모든 요구사항(REQ-DAST-001~014)이 구현되었는가?
- [ ] 모든 TAG가 코드에 주석으로 표시되었는가?
- [ ] Docstring이 모든 함수에 작성되었는가?

### 테스트 완성도

- [ ] 모든 유닛 테스트가 통과하는가?
- [ ] 모든 통합 테스트가 통과하는가?
- [ ] 테스트 커버리지가 85% 이상인가?
- [ ] 모든 시나리오(1~8)의 인수 테스트가 통과하는가?

### 품질 기준

- [ ] Mypy 타입 체크가 strict mode에서 통과하는가?
- [ ] Ruff 린팅이 통과하는가?
- [ ] Bandit 보안 검사가 통과하는가?
- [ ] pip-audit 의존성 검사가 통과하는가?

### 문서 완성도

- [ ] README.md에 DAST 사용 가이드가 작성되었는가?
- [ ] OWASP ZAP 설치 가이드가 제공되는가?
- [ ] CLI 도움말 메시지가 명확한가?
- [ ] API 문서가 생성되었는가?

### 통합 검증

- [ ] SAST + DAST 통합 스캔이 정상 작동하는가?
- [ ] 모든 명령 옵션이 정상 작동하는가?
- [ ] 에러 처리가 적절한가?
- [ ] 진행률 표시가 정상인가?

### 배포 준비

- [ ] 버전이 0.2.0으로 업데이트되었는가?
- [ ] CHANGELOG.md가 작성되었는가?
- [ ] 샘플 스캔 테스트가 성공했는가?
- [ ] Docker CI/CD 테스트가 통과했는가?

---

## 4. 검증 방법

### 4.1 수동 검증 (로컬 환경)

#### 환경 준비
```bash
# 1. ZAP 서버 시작
docker run -d -p 8080:8080 --name zap owasp/zap2docker-stable

# 2. 테스트 웹앱 시작 (예: DVWA)
docker run -d -p 80:80 vulnerables/web-dvwa

# 3. pysec 설치
cd /mnt/c/Users/ADMIN/my-project/project-test
uv sync
```

#### 기본 검증
```bash
# 1. 기본 DAST 스캔
uv run pysec run-dast http://localhost

# 2. JSON 출력
uv run pysec run-dast http://localhost --format json

# 3. 필터링
uv run pysec run-dast http://localhost --severity HIGH --confidence HIGH

# 4. 파일 저장
uv run pysec run-dast http://localhost --format json --output report.json

# 5. SAST + DAST 통합
uv run pysec run-dast http://localhost --include-sast ./src
```

### 4.2 자동화 검증 (CI/CD)

#### 테스트 실행
```bash
# 모든 테스트 실행
uv run pytest tests/test_dast_*.py tests/test_integration.py -v

# 커버리지 생성
uv run pytest tests/ --cov=src/pysec --cov-report=html
```

#### 품질 검사
```bash
# Mypy
uv run mypy src/pysec --strict

# Ruff
uv run ruff check src/pysec

# Bandit
uv run bandit -r src/pysec
```

### 4.3 시스템 검증 (E2E)

#### 샘플 프로젝트 스캔
```bash
# DVWA 스캔 및 결과 검증
pysec run-dast http://localhost \
  --format json \
  --output e2e-test-results.json

# 결과 검증
python3 -c "
import json
with open('e2e-test-results.json') as f:
    report = json.load(f)
    assert report['target_url'] == 'http://localhost/'
    assert len(report['alerts']) > 0
    print('✅ E2E test passed!')
"
```

---

## 5. OWASP 취약점 매핑 검증

### OWASP Top 10 2021 매핑 확인

모든 ZAP Alert ID가 OWASP Top 10 카테고리로 매핑되는지 검증:

```bash
# 매핑 확인
python3 << 'EOF'
from pysec.config.owasp_mappings import ZAP_TO_OWASP

# 모든 매핑이 유효한 OWASP 카테고리를 가져야 함
valid_categories = {
    "A01:2021 – Broken Access Control",
    "A02:2021 – Cryptographic Failures",
    "A03:2021 – Injection",
    "A04:2021 – Insecure Design",
    "A05:2021 – Security Misconfiguration",
    "A06:2021 – Vulnerable and Outdated Components",
    "A07:2021 – Identification and Authentication Failures",
    "A08:2021 – Software and Data Integrity Failures",
    "A09:2021 – Logging and Monitoring Failures",
    "A10:2021 – Server-Side Request Forgery (SSRF)",
}

for zap_id, category in ZAP_TO_OWASP.items():
    assert category in valid_categories, f"Invalid category for {zap_id}: {category}"

print(f"✅ All {len(ZAP_TO_OWASP)} ZAP Alert IDs mapped to valid OWASP categories")
EOF
```

---

**문서 버전**: 0.1.0
**최종 수정**: 2025-11-17
**다음 단계**: SPEC-SECURITY-002 구현 시작
