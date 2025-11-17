# SPEC-SECURITY-002 구현 계획 (Implementation Plan)

## TAG BLOCK

```yaml
spec_id: SPEC-SECURITY-002
title: DAST with OWASP ZAP - 구현 계획
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
- **Primary Goals**: ZAP 엔진 + CLI run-dast 명령어
- **Secondary Goals**: 리포터 확장 (DAST 지원)
- **Final Goals**: SAST+DAST 통합 + 고급 필터링

### 1.2 기술 스택 설정 (확장)

#### 의존성 추가
```bash
# 기존 의존성 (SPEC-SECURITY-001)
# typer, bandit, rich, pydantic, loguru

# 신규 의존성 추가
uv add python-owasp-zap-v2>=0.0.20  # ZAP API 클라이언트
uv add httpx>=0.25.0                # 비동기 HTTP 요청
uv add python-dotenv>=1.0.0         # 환경 변수 관리
uv add tenacity>=8.2.0              # 재시도 로직

# 개발 의존성
uv add --dev responses>=0.24.0      # HTTP 모킹
uv add --dev pytest-asyncio>=0.21.0 # 비동기 테스트
uv add --dev pytest-mock>=3.12.0    # Mock 지원
```

#### pyproject.toml 업데이트
```toml
[project]
version = "0.2.0"  # 버전 업그레이드
description = "Python Security Scanner - SAST + DAST"

dependencies = [
    # 기존
    "typer[all]>=0.20.0",
    "bandit>=1.8.6",
    "rich>=13.9.0",
    "pydantic>=2.10.0",
    "loguru>=0.7.0",
    # 신규 (DAST)
    "python-owasp-zap-v2>=0.0.20",
    "httpx>=0.25.0",
    "python-dotenv>=1.0.0",
    "tenacity>=8.2.0",
]
```

---

## 2. TDD 사이클

### 2.1 Red-Green-Refactor 프로세스 (DAST)

#### Phase 1: ZAP 엔진 개발

**Test 1: ZAP 연결 테스트**
```python
# tests/test_dast_engine.py
import pytest
from pysec.scanner.zap_engine import ZapScanner

@pytest.mark.asyncio
async def test_zap_connection():
    """ZAP 인스턴스와 연결 테스트 (TAG-REQ-DAST-001)"""
    scanner = ZapScanner(host="localhost", port=8080)

    # 실패할 것 예상 (ZAP 서버 미실행)
    with pytest.raises(ConnectionError):
        await scanner.health_check()
```

**구현**:
```python
# src/pysec/scanner/zap_engine.py
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class ZapScanner:
    """OWASP ZAP DAST 스캐너 (TAG-REQ-DAST-001)"""

    def __init__(self, host: str = "localhost", port: int = 8080, api_key: str = ""):
        self.host = host
        self.port = port
        self.api_key = api_key
        self.base_url = f"http://{host}:{port}"
        self.client = httpx.AsyncClient()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    async def health_check(self) -> dict:
        """ZAP 서버 상태 확인"""
        response = await self.client.get(f"{self.base_url}/json/core/view/version")
        response.raise_for_status()
        return response.json()

    async def scan(self, target_url: str, timeout: int = 600) -> dict:
        """DAST 스캔 실행 (TAG-REQ-DAST-005)"""
        # 1. 타겟 설정
        # 2. Spider 실행
        # 3. Passive Scan 대기
        # 4. 결과 조회
        pass
```

**Test 2: URL 검증**
```python
@pytest.mark.asyncio
async def test_invalid_url():
    """유효하지 않은 URL 처리 (TAG-REQ-DAST-007)"""
    scanner = ZapScanner()

    with pytest.raises(ValueError, match="Invalid URL"):
        await scanner.validate_url("not-a-url")
```

**구현**:
```python
from urllib.parse import urlparse

async def validate_url(self, url: str) -> bool:
    """URL 형식 및 접근성 검증"""
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError("Invalid URL format")

        # 접근성 테스트
        response = await self.client.head(url, follow_redirects=True, timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        raise ValueError(f"URL validation failed: {e}")
```

**Test 3: Alert 파싱**
```python
@pytest.mark.asyncio
async def test_alert_parsing():
    """ZAP Alert JSON 파싱 (TAG-REQ-DAST-006)"""
    scanner = ZapScanner()

    # Mock ZAP 응답
    mock_response = {
        "alerts": [
            {
                "id": "40018",
                "name": "SQL Injection",
                "riskid": "3",
                "confidence": "2",
                "url": "http://example.com/search?q=test",
                "evidence": "' OR '1'='1",
                ...
            }
        ]
    }

    alerts = scanner.parse_alerts(mock_response)

    assert len(alerts) == 1
    assert alerts[0].severity == "HIGH"
    assert alerts[0].owasp_category == "A03:2021 – Injection"
```

**구현**:
```python
from pysec.scanner.models import DastAlert
from pysec.config.owasp_mappings import ZAP_TO_OWASP, RISK_LEVELS

def parse_alerts(self, response: dict) -> list[DastAlert]:
    """ZAP 응답을 DastAlert로 변환"""
    alerts = []

    for idx, alert in enumerate(response.get("alerts", []), 1):
        risk_id = alert.get("riskid", "0")
        severity = self._map_severity(RISK_LEVELS.get(risk_id, "INFO"))
        confidence = self._map_confidence(alert.get("confidence", "0"))

        dast_alert = DastAlert(
            id=f"dast-{idx:03d}",
            alert_id=alert.get("id"),
            severity=severity,
            confidence=confidence,
            name=alert.get("name"),
            url=alert.get("url"),
            parameter=alert.get("parameter"),
            evidence=alert.get("evidence"),
            description=alert.get("description"),
            solution=alert.get("solution"),
            owasp_category=ZAP_TO_OWASP.get(
                alert.get("id"), "Unknown"
            ),
            cwe_id=alert.get("cweid"),
            reference=alert.get("reference")
        )
        alerts.append(dast_alert)

    return alerts

def _map_severity(self, risk_level: str) -> Literal["HIGH", "MEDIUM", "LOW", "INFO"]:
    """Risk Level을 Severity로 변환"""
    mapping = {
        "High": "HIGH",
        "Medium": "MEDIUM",
        "Low": "LOW",
        "Informational": "INFO",
    }
    return mapping.get(risk_level, "INFO")
```

#### Phase 2: CLI 통합

**Test 1: run-dast 명령어**
```python
# tests/test_dast_cli.py
from typer.testing import CliRunner
from pysec.cli.main import app

def test_run_dast_command():
    """run-dast 명령어 테스트 (TAG-REQ-DAST-005)"""
    runner = CliRunner()

    # 아직 구현 안 됨 → 실패 예상
    result = runner.invoke(app, ["run-dast", "http://example.com"])

    assert "run-dast" in app.__dict__
```

**구현**:
```python
# src/pysec/cli/commands.py (기존 scan 명령어에 추가)
import typer
from pathlib import Path

@app.command()
async def run_dast(
    target_url: Annotated[str, typer.Argument(help="스캔 대상 URL (http/https)")],
    format: Annotated[str, typer.Option(help="출력 형식 (text, json)")] = "text",
    severity: Annotated[str, typer.Option(help="심각도 필터")] = "ALL",
    confidence: Annotated[str, typer.Option(help="신뢰도 필터")] = "ALL",
    zap_host: Annotated[str, typer.Option(help="ZAP 호스트")] = "localhost",
    zap_port: Annotated[int, typer.Option(help="ZAP 포트")] = 8080,
    timeout: Annotated[int, typer.Option(help="스캔 타임아웃 (초)")] = 600,
    output: Annotated[Path | None, typer.Option(help="출력 파일")] = None,
    verbose: Annotated[bool, typer.Option(help="상세 로그")] = False,
):
    """웹 애플리케이션 동적 보안 스캔 (DAST) (TAG-REQ-DAST-005)"""

    # 1. URL 검증 (TAG-REQ-DAST-007)
    # 2. ZAP 연결 확인 (TAG-REQ-DAST-008)
    # 3. 스캔 실행 (TAG-REQ-DAST-010)
    # 4. 필터링 (TAG-REQ-DAST-013)
    # 5. 리포트 생성 (TAG-REQ-DAST-014)
    pass
```

#### Phase 3: 리포터 확장

**Test: DAST JSON 출력**
```python
def test_dast_json_reporter():
    """DAST JSON 리포터 테스트 (TAG-REQ-DAST-014)"""
    from pysec.reporter.json_reporter import JsonReporter
    from pysec.scanner.models import DastAlert

    alerts = [
        DastAlert(
            id="dast-001",
            alert_id="40018",
            severity="HIGH",
            confidence="HIGH",
            name="SQL Injection",
            url="http://example.com/search",
            parameter="q",
            evidence="' OR '1'='1",
            description="SQL injection found",
            solution="Use parameterized queries",
            owasp_category="A03:2021 – Injection",
            cwe_id="89",
        )
    ]

    reporter = JsonReporter()
    output = reporter.format_dast(alerts, "http://example.com")

    # JSON 검증
    assert "dast-001" in output
    assert "SQL Injection" in output
```

**구현**:
```python
# src/pysec/reporter/json_reporter.py (확장)
def format_dast(self, alerts: list[DastAlert], target_url: str) -> str:
    """DAST 결과를 JSON으로 포맷"""
    summary = self._generate_dast_summary(alerts)

    report = {
        "scan_id": f"dast-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "target_url": target_url,
        "summary": summary,
        "alerts": [alert.model_dump() for alert in alerts],
        "metadata": {
            "scanner": "OWASP ZAP",
            "pysec_version": "0.2.0",
            "scan_type": "Passive"
        }
    }

    return json.dumps(report, indent=2, ensure_ascii=False)
```

---

## 3. 모듈별 구현 계획

### Primary Goals (핵심 기능)

#### Phase 1: ZAP 엔진 개발

**목표**
- OWASP ZAP API 클라이언트 구현
- URL 검증 및 접근성 확인
- 스캔 실행 및 결과 조회

**TDD 순서**
1. ZAP 연결 테스트
2. URL 검증 테스트
3. Alert 파싱 테스트
4. OWASP 매핑 테스트

**구현 파일**
- `src/pysec/scanner/zap_engine.py` (신규)
- `src/pysec/scanner/models.py` (DastAlert 추가)
- `src/pysec/config/owasp_mappings.py` (신규)

**예상 결과**
- ✅ ZAP 연결 성공
- ✅ URL 검증 정상 작동
- ✅ Alert 파싱 정상 작동
- ✅ OWASP 매핑 정확성

**체크리스트**
- [ ] ZapScanner 클래스 구현
- [ ] 재시도 로직 (Tenacity) 적용
- [ ] 에러 처리 표준화
- [ ] Mypy 타입 체크 통과 (strict mode)
- [ ] 테스트 커버리지 85% 이상

---

#### Phase 2: CLI run-dast 명령어

**목표**
- run-dast 명령어 구현
- 옵션 파싱 및 검증
- 진행률 표시

**TDD 순서**
1. 기본 명령어 구조
2. URL 검증
3. ZAP 연결 에러 처리
4. 진행률 표시

**구현 파일**
- `src/pysec/cli/commands.py` (run_dast 함수 추가)

**예상 결과**
- ✅ `pysec run-dast http://example.com` 명령어 작동
- ✅ 옵션 파싱 정상
- ✅ 에러 메시지 명확

**체크리스트**
- [ ] 모든 옵션 구현 (format, severity, confidence 등)
- [ ] 에러 처리 완성
- [ ] 사용 예제 작성
- [ ] 테스트 커버리지 85% 이상

---

### Secondary Goals (부가 기능)

#### Phase 3: 리포터 확장

**목표**
- JSON 리포터에 DAST 지원 추가
- 텍스트 리포터에 DAST 포맷 추가

**TDD 순서**
1. DAST JSON 출력
2. DAST 텍스트 출력 (Rich 색상)
3. 심각도별 필터링

**구현 파일**
- `src/pysec/reporter/json_reporter.py` (format_dast 메서드 추가)
- `src/pysec/reporter/text_reporter.py` (format_dast 메서드 추가)

**예상 결과**
- ✅ JSON 출력 정상
- ✅ 텍스트 출력 가독성 우수
- ✅ 색상 구분 명확

---

### Final Goals (완성도)

#### Phase 4: SAST + DAST 통합 및 고급 기능

**목표**
- `--include-sast` 옵션으로 SAST+DAST 통합 스캔
- 신뢰도 필터링
- 구성 파일 지원

**구현 파일**
- `src/pysec/cli/commands.py` (통합 로직)
- `src/pysec/scanner/zap_config.py` (구성 파일)

**예상 결과**
- ✅ SAST + DAST 통합 스캔 작동
- ✅ 신뢰도 필터링 정상
- ✅ 구성 파일 지원

---

## 4. 기술 아키텍처

### 4.1 계층 구조 (확장)

```
┌─────────────────────────────────────┐
│         CLI Layer (Typer)           │  사용자 인터페이스
│  - main.py (엔트리포인트)            │
│  - commands.py                      │
│    ├── scan (기존 SAST)             │
│    └── run-dast (신규 DAST)         │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
┌──────────────┐  ┌──────────────────┐
│ SAST Layer   │  │  DAST Layer      │
│ (Bandit)     │  │  (ZAP API)       │
│              │  │                  │
│ bandit_      │  │ zap_engine.py    │
│ engine.py    │  │                  │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       └────────┬──────────┘
                ▼
        ┌──────────────────┐
        │  Models Layer    │
        │  (Pydantic)      │
        │                  │
        │ models.py        │
        │ owasp_mappings.py│
        └────────┬─────────┘
                 │
        ┌────────▼─────────┐
        │ Reporter Layer   │
        │ (Output)         │
        │                  │
        │ json_reporter.py │
        │ text_reporter.py │
        └──────────────────┘
```

### 4.2 데이터 흐름 (DAST)

```
사용자 입력 (CLI: run-dast)
    ↓
URL 검증 → ZAP 연결 확인
    ↓
Spider 실행 (사이트 크롤링)
    ↓
Passive Scan 자동 실행
    ↓
Alerts 조회 (ZAP API)
    ↓
DastAlert 모델 변환 & OWASP 매핑
    ↓
필터링 (severity, confidence)
    ↓
Reporter 선택 (JSON/Text)
    ↓
출력 (stdout/file)
```

### 4.3 에러 처리 전략 (확장)

```python
class PysecError(Exception):
    """Base exception"""

class ScannerError(PysecError):
    """스캐너 실행 오류"""

class DastError(ScannerError):
    """DAST 관련 오류"""

    class ConnectionError(DastError):
        """ZAP 연결 실패"""

    class ScanError(DastError):
        """스캔 실행 오류"""

    class TimeoutError(DastError):
        """스캔 타임아웃"""

class ValidationError(PysecError):
    """입력 검증 오류"""

    class UrlError(ValidationError):
        """URL 검증 오류"""
```

---

## 5. 마일스톤

### Primary Goals (핵심 기능)

#### Milestone 1: ZAP 엔진 개발
- **목표**: DAST 스캔 기능 완성
- **산출물**:
  - ✅ ZapScanner 클래스 구현
  - ✅ URL 검증 및 접근성 확인
  - ✅ Alert 파싱 및 OWASP 매핑
- **품질 기준**:
  - 테스트 커버리지 85% 이상
  - Mypy, Ruff 통과
  - 샘플 웹앱 스캔 성공

#### Milestone 2: CLI run-dast 명령어
- **목표**: DAST CLI 인터페이스 완성
- **산출물**:
  - ✅ run-dast 명령어 동작
  - ✅ 옵션 파싱 (URL, format, severity 등)
  - ✅ 에러 처리 및 도움말
- **품질 기준**:
  - 테스트 커버리지 85% 이상
  - 에러 메시지 명확

### Secondary Goals (부가 기능)

#### Milestone 3: 리포터 확장
- **목표**: DAST 리포팅 완성
- **산출물**:
  - ✅ JSON 포맷 (프로그래밍 가능)
  - ✅ 텍스트 포맷 (Rich 색상)
  - ✅ 통계 정보
- **품질 기준**:
  - JSON 스키마 유효성
  - 가독성 확인

### Final Goals (완성도)

#### Milestone 4: SAST+DAST 통합
- **목표**: 통합 보안 스캔 완성
- **산출물**:
  - ✅ SAST + DAST 순차 실행
  - ✅ 신뢰도 필터링
  - ✅ 구성 파일 지원
- **품질 기준**:
  - 통합 테스트 통과
  - TRUST 5 원칙 준수

#### Milestone 5: MVP 완성
- **목표**: DAST MVP 배포 준비
- **산출물**:
  - ✅ 전체 테스트 통과
  - ✅ README 작성 (DAST 가이드)
  - ✅ 문서 완성
- **품질 기준**:
  - Definition of Done 모두 체크
  - 버전 0.2.0 배포 준비

---

## 6. 위험 관리

### 6.1 기술적 위험

#### Risk 1: OWASP ZAP 설치/실행 문제
**확률**: MEDIUM | **영향**: HIGH

**완화 전략**:
- ✅ Docker 기반 ZAP 실행 가이드 제공
- ✅ 설치 가이드 상세 작성
- ✅ 헬스 체크 자동화

**대응 계획**:
- ZAP 미설치 시 명확한 가이드 메시지
- 자동 설치 스크립트 제공
- CI/CD에서 Docker ZAP으로 테스트

#### Risk 2: 네트워크 타임아웃
**확률**: MEDIUM | **영향**: MEDIUM

**완화 전략**:
- ✅ 재시도 로직 (Tenacity) 적용
- ✅ 구성 가능한 타임아웃
- ✅ 진행 상황 실시간 표시

**대응 계획**:
- 명확한 타임아웃 메시지
- 부분 결과 제공
- 로그 기록

#### Risk 3: ZAP API 호환성
**확률**: LOW | **영향**: HIGH

**완화 전략**:
- ✅ ZAP 버전 명시 (2.13.0+)
- ✅ API 변경사항 감시
- ✅ 호환성 테스트

**대응 계획**:
- 버전 지정 의존성
- 문서화된 호환성 매트릭스

### 6.2 프로세스 위험

#### Risk 4: 테스트 커버리지 미달
**확률**: LOW | **영향**: HIGH

**완화 전략**:
- ✅ pytest-cov로 자동 측정
- ✅ 85% 미만 시 CI 실패
- ✅ Mock 기반 ZAP 테스트

**대응 계획**:
- 누락된 테스트 우선 작성
- Mock ZAP 서버 활용

---

## 7. 품질 보증

### 7.1 자동화된 품질 검사

#### Pre-commit Hook (확장)
```bash
#!/bin/bash

# 1. 정적 분석
uv run mypy src/pysec
uv run ruff check src/pysec

# 2. 테스트
uv run pytest tests/

# 3. 커버리지
uv run pytest --cov=src/pysec --cov-fail-under=85

# 4. 통합 테스트
uv run pytest tests/test_integration.py -v
```

#### CI/CD (GitHub Actions - 확장)
```yaml
jobs:
  test-dast:
    runs-on: ubuntu-latest
    services:
      zap:
        image: owasp/zap2docker-stable
        ports:
          - 8080:8080

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install UV
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Wait for ZAP
        run: sleep 10

      - name: Run DAST tests
        run: uv run pytest tests/test_dast_*.py -v

      - name: Run integration tests
        run: uv run pytest tests/test_integration.py -v
```

### 7.2 TRUST 5 체크리스트

#### T - Test-first
- [ ] DAST 엔진 테스트 (단위 + 통합)
- [ ] CLI 명령어 테스트
- [ ] Mock ZAP 기반 테스트
- [ ] 테스트 커버리지 85% 이상

#### R - Readable
- [ ] Mypy 타입 체크 100% 통과 (strict mode)
- [ ] Ruff 린팅 규칙 모두 준수
- [ ] Docstring 작성 (Google 스타일)
- [ ] 코드 리뷰 기준 충족

#### U - Unified
- [ ] Pydantic 모델 일관성
- [ ] 에러 처리 표준화
- [ ] 로깅 포맷 통일
- [ ] 설정 관리 표준화

#### S - Secured
- [ ] URL 입력 검증
- [ ] API 키 보호 (환경 변수)
- [ ] 서브프로세스 안전 실행
- [ ] 민감 정보 로그 제외

#### T - Trackable
- [ ] 모든 커밋에 TAG 포함
- [ ] SPEC 문서와 코드 동기화
- [ ] TAG 체인 완성
- [ ] 추적성 보고서 생성

---

## 8. 다음 단계

### DAST MVP 완성 후

1. **SPEC-SECURITY-003**: SCA + 능동 스캔
   - Safety, pip-audit 통합
   - ZAP 능동 스캔 (Active Scan)
   - 인증 기반 스캔

2. **향후 개선**:
   - 웹 대시보드 (Streamlit)
   - MCP 통합
   - claude-code security-expert 에이전트
   - 자동화 스케줄링

3. **배포 준비**:
   - PyPI 배포 (버전 0.2.0)
   - Docker 이미지 제공
   - 문서 사이트 (MkDocs)

---

**문서 버전**: 0.1.0
**최종 수정**: 2025-11-17
**다음 단계**: `/alfred:2-run SPEC-SECURITY-002` 실행
