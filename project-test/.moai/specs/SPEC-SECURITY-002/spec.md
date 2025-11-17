# SPEC-SECURITY-002: 동적 보안 분석 도구 (DAST with OWASP ZAP)

## TAG BLOCK

```yaml
spec_id: SPEC-SECURITY-002
title: 웹 애플리케이션 동적 보안 분석 도구 (DAST with OWASP ZAP)
domain: SECURITY
status: draft
version: 0.1.0
created: 2025-11-17
author: @user
priority: HIGH
related_specs: [SPEC-SECURITY-001]
dependencies:
  - SPEC-SECURITY-001 (Reporter, Models 재사용)
  - Java Runtime (OWASP ZAP 실행)
  - Python 3.11+
```

---

## 1. Environment (환경)

### 1.1 시스템 환경
- **Python 버전**: Python 3.11 이상
- **Java 버전**: Java 8 이상 (OWASP ZAP 요구사항)
- **운영체제**: Linux, macOS, Windows (크로스 플랫폼)
- **네트워크**: 대상 애플리케이션과 통신 가능한 네트워크

### 1.2 기술 스택
- **DAST 엔진**: OWASP ZAP >= 2.13.0
- **ZAP API 클라이언트**: python-owasp-zap-v2 >= 0.0.20
- **기존 라이브러리**:
  - typer >= 0.20.0 (CLI 프레임워크)
  - pydantic >= 2.10.0 (데이터 검증)
  - rich >= 13.9.0 (터미널 UI)
  - loguru >= 0.7.0 (로깅)

### 1.3 개발 환경
- **패키지 관리**: uv 또는 pip
- **테스트**: pytest >= 8.3.0, pytest-cov >= 6.0.0
- **정적 분석**: mypy >= 1.13.0, ruff >= 0.8.0
- **모킹**: pytest-mock, responses (HTTP 모킹)

### 1.4 프로젝트 구조
```
src/pysec/
├── cli/
│   ├── main.py           # CLI 엔트리포인트
│   └── commands.py       # scan, run-dast 명령어
├── scanner/
│   ├── bandit_engine.py  # SAST (기존)
│   ├── zap_engine.py     # DAST (신규)
│   └── models.py         # 공용 데이터 모델
├── reporter/
│   ├── json_reporter.py  # JSON (기존)
│   └── text_reporter.py  # 텍스트 (기존)
└── config/
    └── owasp_mappings.py # OWASP Top 10 매핑

tests/
├── test_dast_engine.py
├── test_dast_cli.py
└── fixtures/
    ├── sample_project/   # SAST 테스트용
    └── sample_webapp/    # DAST 테스트용 (docker-compose)
```

---

## 2. Assumptions (가정사항)

### 2.1 사용자 가정
- 사용자는 OWASP ZAP을 로컬에 설치하거나 Docker로 실행할 수 있음
- 사용자는 스캔 대상 웹 애플리케이션의 기본 URL을 알고 있음
- 사용자는 터미널 환경에서 명령어 실행 가능
- 사용자는 JSON 또는 텍스트 형식의 리포트를 이해할 수 있음

### 2.2 기술적 가정
- OWASP ZAP이 로컬 또는 원격 서버에 설치되어 있음
- ZAP API가 포트 8080 (기본값) 또는 구성된 포트에서 접근 가능
- 스캔 대상 애플리케이션이 안정적으로 실행 중임
- 대상 URL이 읽기 권한으로 접근 가능함

### 2.3 범위 가정 (DAST MVP)
- **포함**: OWASP ZAP 수동 스캔, OWASP Top 10 2021 매핑, CLI 통합
- **제외**: 능동 스캔 (공격 벡터), 인증 기반 스캔, SCA/IAST
- **향후**: SPEC-SECURITY-003에서 능동 스캔, SCA 통합 예정

### 2.4 보안 가정
- 사용자는 신뢰할 수 있는 네트워크 환경에서 DAST 실행
- 스캔 대상 URL에 민감 데이터 없음 (테스트 환경)
- ZAP 인스턴스는 방화벽 뒤에 격리된 환경

---

## 3. Requirements (요구사항)

### 3.1 Ubiquitous (항상 참인 요구사항)

#### REQ-DAST-001: OWASP ZAP 통합
**설명**: 시스템은 OWASP ZAP을 사용하여 웹 애플리케이션의 동적 보안 취약점을 탐지해야 한다.

**기준**:
- OWASP ZAP API를 통해 스캔 시작
- 수동 스캔(Passive Scan) 실행
- ZAP JSON 결과를 파싱
- OWASP Top 10 2021 카테고리로 분류

**추적성**: TAG-REQ-DAST-001

#### REQ-DAST-002: 웹 애플리케이션 스캔
**설명**: 시스템은 주어진 URL의 웹 애플리케이션을 대상으로 동적 스캔을 실행해야 한다.

**기준**:
- `pysec run-dast <target-url>` 명령어 지원
- URL 형식 검증 (http/https)
- 스캔 진행 상황 실시간 표시
- 스캔 완료 후 결과 출력

**추적성**: TAG-REQ-DAST-002

#### REQ-DAST-003: 통합 리포팅
**설명**: 시스템은 SAST와 DAST 결과를 통합된 리포트로 출력해야 한다.

**기준**:
- JSON 형식: 구조화된 통합 데이터
- 텍스트 형식: 심각도별 분류 (Rich 색상)
- 메타데이터: ZAP 버전, 스캔 시간, 스캔 대상

**추적성**: TAG-REQ-DAST-003

#### REQ-DAST-004: 취약점 분류
**설명**: 시스템은 ZAP에서 탐지된 취약점을 OWASP Top 10 카테고리로 자동 분류해야 한다.

**기준**:
- A01:2021 – Broken Access Control
- A02:2021 – Cryptographic Failures
- A03:2021 – Injection
- A04:2021 – Insecure Design
- ... (A01~A10 전체 매핑)
- 신뢰도(Confidence) 및 심각도(Risk) 수준 표시

**추적성**: TAG-REQ-DAST-004

### 3.2 Event-Driven (이벤트 기반 요구사항)

#### REQ-DAST-005: DAST 스캔 실행 이벤트
**WHEN** 사용자가 `pysec run-dast <url>` 명령을 실행하면
- **THEN** 시스템은 다음을 수행한다:
  1. URL 유효성 및 접근성 검증
  2. OWASP ZAP 연결 확인
  3. 수동 스캔 시작
  4. 진행 상황 실시간 표시 (프로그레스 바)
  5. 스캔 완료 시 결과 출력

**추적성**: TAG-REQ-DAST-005

#### REQ-DAST-006: 취약점 발견 이벤트
**WHEN** OWASP ZAP이 웹 취약점을 발견하면
- **THEN** 시스템은 다음 정보를 기록한다:
  - 취약점 URL 및 엔드포인트
  - 취약점 유형 (예: Cross Site Scripting - XSS)
  - 심각도 수준 (High, Medium, Low, Informational)
  - 신뢰도 (Confidence: High, Medium, Low)
  - OWASP 카테고리 (A01~A10)
  - 수정 권장사항

**추적성**: TAG-REQ-DAST-006

### 3.3 Unwanted (원하지 않는 상황 처리)

#### REQ-DAST-007: 잘못된 URL 처리
**IF** 스캔 대상 URL이 유효하지 않거나 접근 불가능하면
- **THEN** 시스템은:
  - URL 형식 에러 메시지 출력
  - 접근성 테스트 결과 표시
  - 예제 사용법 안내
  - 종료 코드 1로 종료

**추적성**: TAG-REQ-DAST-007

#### REQ-DAST-008: ZAP 연결 실패
**IF** OWASP ZAP 인스턴스에 연결할 수 없으면
- **THEN** 시스템은:
  - 상세한 연결 에러 메시지 출력
  - ZAP 설치 및 실행 가이드 제공
  - 디버깅 정보 (호스트, 포트, 타임아웃)
  - 종료 코드 2로 종료

**추적성**: TAG-REQ-DAST-008

#### REQ-DAST-009: 스캔 타임아웃
**IF** 스캔이 최대 시간(600초)을 초과하면
- **THEN** 시스템은:
  - 진행 중인 스캔 중단
  - "스캔 타임아웃" 메시지 출력
  - 부분 결과 (있으면) 출력
  - 종료 코드 3으로 종료

**추적성**: TAG-REQ-DAST-009

### 3.4 State-Driven (상태 기반 요구사항)

#### REQ-DAST-010: 스캔 진행 중 상태
**WHILE** DAST 스캔이 실행 중일 때
- **THEN** 시스템은:
  - Rich 프로그레스 바로 진행률 표시 (0~100%)
  - 현재 스캔 단계 표시 (Setup → Spider → Passive Scan → Complete)
  - 발견된 이슈 카운트 실시간 업데이트
  - 경과 시간 및 예상 남은 시간 표시

**추적성**: TAG-REQ-DAST-010

#### REQ-DAST-011: SAST + DAST 통합 상태
**WHILE** 사용자가 `-include-sast` 옵션을 사용하면
- **THEN** 시스템은:
  - 먼저 SAST 스캔 실행
  - 다음으로 DAST 스캔 실행
  - 최종 리포트에 모든 취약점 통합

**추적성**: TAG-REQ-DAST-011

### 3.5 Optional (선택적 요구사항)

#### REQ-DAST-012: 구성 파일 지원
**WHERE** 사용자가 `--config zap-config.json` 옵션을 지정하면
- **THEN** 시스템은 커스텀 ZAP 설정(호스트, 포트, 인증)을 적용한다

**추적성**: TAG-REQ-DAST-012

#### REQ-DAST-013: 신뢰도 필터링
**WHERE** 사용자가 `--confidence HIGH` 옵션을 지정하면
- **THEN** 시스템은 높은 신뢰도의 취약점만 표시한다

**추적성**: TAG-REQ-DAST-013

#### REQ-DAST-014: 출력 포맷 옵션
**WHERE** 사용자가 `--format json` 옵션을 지정하면
- **THEN** 시스템은 JSON 형식으로 결과를 출력한다

**추적성**: TAG-REQ-DAST-014

---

## 4. Specifications (상세 명세)

### 4.1 CLI 명령어 인터페이스

#### 명령어 구조 (신규)
```bash
pysec run-dast <TARGET_URL> [OPTIONS]
```

#### 옵션
| 옵션 | 설명 | 기본값 | 예제 |
|------|------|--------|------|
| `--format` | 출력 형식 (text, json) | text | `--format json` |
| `--severity` | 심각도 필터 (ALL, HIGH, MEDIUM, LOW) | ALL | `--severity HIGH` |
| `--confidence` | 신뢰도 필터 (ALL, HIGH, MEDIUM, LOW) | ALL | `--confidence HIGH` |
| `--output` | 파일로 저장 | stdout | `--output report.json` |
| `--zap-host` | ZAP 호스트 주소 | localhost | `--zap-host 192.168.1.10` |
| `--zap-port` | ZAP 포트 | 8080 | `--zap-port 8090` |
| `--timeout` | 스캔 타임아웃 (초) | 600 | `--timeout 1200` |
| `--include-sast` | SAST 함께 실행 | False | `--include-sast` |
| `--verbose` | 상세 로그 출력 | False | `--verbose` |

#### 사용 예제
```bash
# 기본 DAST 스캔
pysec run-dast http://example.com

# JSON 출력
pysec run-dast http://example.com --format json

# HIGH 심각도 + HIGH 신뢰도만 필터링
pysec run-dast http://example.com --severity HIGH --confidence HIGH

# 파일로 저장
pysec run-dast http://example.com --format json --output dast-report.json

# SAST + DAST 통합 스캔 (로컬 코드도 함께)
pysec run-dast http://localhost:3000 --include-sast ./src

# 커스텀 ZAP 서버
pysec run-dast http://example.com --zap-host 192.168.1.10 --zap-port 8090
```

### 4.2 OWASP ZAP 통합 명세

#### ZAP 연결 설정
```python
# OWASP ZAP 기본 설정
ZAP_HOST: str = "localhost"
ZAP_PORT: int = 8080
ZAP_API_KEY: str = ""  # 선택적
ZAP_TIMEOUT: int = 600  # 10분
ZAP_SPIDER_TIMEOUT: int = 60  # 1분 내 스파이더 완료
```

#### 스캔 프로세스
```
1. ZAP 연결 확인 (GET /json/core/action/version)
2. 타겟 URL 설정 (POST /json/core/action/newContext?contextName=target)
3. Spider 실행 (POST /json/spider/action/scan?url=<target>)
4. Passive 스캔 실행 (자동, Spider 중)
5. 결과 조회 (GET /json/core/view/alerts)
6. 스캔 완료 및 정리
```

#### ZAP JSON 응답 파싱
```python
# ZAP alerts 구조
{
  "alerts": [
    {
      "id": "40018",
      "name": "SQL Injection",
      "riskid": "3",  # 0=Info, 1=Low, 2=Medium, 3=High
      "confidence": "2",  # 0=Low, 1=Medium, 2=High
      "count": 1,
      "url": "http://example.com/product?id=1",
      "other": "Evidence of SQL Injection",
      "description": "SQL injection attack...",
      "solution": "Parameterize queries",
      "reference": "https://owasp.org/www-community/attacks/SQL_Injection",
      "cweid": "89"
    }
  ]
}
```

#### OWASP Top 10 2021 매핑
```python
ZAP_TO_OWASP = {
    "40018": "A03:2021 – Injection",  # SQL Injection
    "40019": "A03:2021 – Injection",  # LDAP Injection
    "40020": "A03:2021 – Injection",  # OS Command Injection
    "40021": "A07:2021 – Cross-Site Scripting (XSS)",  # XSS
    "40022": "A01:2021 – Broken Access Control",  # Directory Traversal
    ...
}

RISK_LEVELS = {
    "0": "Informational",
    "1": "Low",
    "2": "Medium",
    "3": "High",
}

CONFIDENCE_LEVELS = {
    "0": "LOW",
    "1": "MEDIUM",
    "2": "HIGH",
}
```

### 4.3 데이터 모델 (확장)

#### DAST 데이터 모델
```python
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class DastAlert(BaseModel):
    """OWASP ZAP 취약점 모델"""
    id: str = Field(description="고유 이슈 ID (scan-{timestamp}-{idx})")
    alert_id: str = Field(description="ZAP Alert ID (예: 40018)")
    severity: Literal["HIGH", "MEDIUM", "LOW", "INFO"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    name: str = Field(description="취약점 이름 (예: SQL Injection)")
    url: str = Field(description="취약한 URL")
    parameter: str | None = Field(description="취약한 파라미터 (예: id)")
    evidence: str = Field(description="증거 코드/응답")
    description: str = Field(description="취약점 상세 설명")
    solution: str = Field(description="해결 방법")
    owasp_category: str = Field(description="OWASP Top 10 카테고리 (A01~A10)")
    cwe_id: str | None = Field(description="CWE ID (예: 89)")
    reference: str | None = Field(description="참고 URL")

class DastScanResult(BaseModel):
    """DAST 스캔 결과"""
    scan_id: str
    timestamp: datetime
    target_url: str
    zap_version: str
    scan_duration: int = Field(description="스캔 소요 시간 (초)")
    summary: dict  # {total: int, high: int, medium: int, low: int, info: int}
    alerts: list[DastAlert]
    metadata: dict

class UnifiedReport(BaseModel):
    """SAST + DAST 통합 리포트"""
    report_id: str
    timestamp: datetime
    sast_result: dict | None = None  # SPEC-SECURITY-001 결과
    dast_result: dict | None = None  # SPEC-SECURITY-002 결과
    combined_summary: dict
    all_issues: list  # 통합 이슈 리스트
```

### 4.4 리포팅 형식 명세

#### 텍스트 출력 예제
```
🔍 DAST Security Scan Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Scan Summary
  Target URL: http://example.com
  Scan Time: 2025-11-17 14:30:22
  ZAP Version: 2.14.0
  Duration: 120 seconds

📈 Results
  Total Alerts: 5
  🔴 HIGH: 2
  🟡 MEDIUM: 2
  🔵 LOW: 1
  ℹ️  INFO: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 HIGH Severity Issues

[1] SQL Injection
  URL: http://example.com/search?q=test
  Parameter: q
  Confidence: HIGH
  OWASP: A03:2021 – Injection
  Evidence: ' OR '1'='1
  Solution: Use parameterized queries
  Reference: https://owasp.org/www-community/attacks/SQL_Injection

[2] Cross-Site Scripting (XSS)
  URL: http://example.com/comment
  Parameter: comment
  Confidence: MEDIUM
  OWASP: A07:2021 – XSS
  Evidence: <script>alert('XSS')</script>
  Solution: Properly encode and sanitize user input
  Reference: https://owasp.org/www-community/attacks/xss/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### JSON 출력 예제
```json
{
  "scan_id": "dast-scan-20251117-143022",
  "timestamp": "2025-11-17T14:30:22Z",
  "target_url": "http://example.com",
  "zap_version": "2.14.0",
  "scan_duration": 120,
  "summary": {
    "total_alerts": 5,
    "high": 2,
    "medium": 2,
    "low": 1,
    "info": 0
  },
  "alerts": [
    {
      "id": "dast-scan-20251117-143022-001",
      "alert_id": "40018",
      "severity": "HIGH",
      "confidence": "HIGH",
      "name": "SQL Injection",
      "url": "http://example.com/search?q=test",
      "parameter": "q",
      "evidence": "' OR '1'='1",
      "description": "SQL injection vulnerability detected",
      "solution": "Use parameterized queries",
      "owasp_category": "A03:2021 – Injection",
      "cwe_id": "89",
      "reference": "https://owasp.org/www-community/attacks/SQL_Injection"
    }
  ],
  "metadata": {
    "scanner": "OWASP ZAP",
    "pysec_version": "0.2.0",
    "scan_type": "Passive"
  }
}
```

---

## 5. Traceability (추적성)

### 5.1 TAG 체인

| TAG ID | 요구사항 | 구현 파일 | 테스트 파일 |
|--------|----------|-----------|-------------|
| TAG-REQ-DAST-001 | ZAP 통합 | `scanner/zap_engine.py` | `tests/test_dast_engine.py` |
| TAG-REQ-DAST-002 | 웹 스캔 | `cli/commands.py` | `tests/test_dast_cli.py` |
| TAG-REQ-DAST-003 | 통합 리포팅 | `reporter/*.py` | `tests/test_reporter.py` |
| TAG-REQ-DAST-004 | 취약점 분류 | `config/owasp_mappings.py` | `tests/test_owasp_mapping.py` |
| TAG-REQ-DAST-005 | 스캔 실행 | `cli/commands.py` | `tests/test_dast_cli.py::test_run_dast` |
| TAG-REQ-DAST-006 | 취약점 발견 | `scanner/zap_engine.py` | `tests/test_dast_engine.py::test_alert_parsing` |
| TAG-REQ-DAST-007 | 잘못된 URL | `cli/commands.py` | `tests/test_dast_cli.py::test_invalid_url` |
| TAG-REQ-DAST-008 | ZAP 연결 실패 | `scanner/zap_engine.py` | `tests/test_dast_engine.py::test_zap_connection_error` |
| TAG-REQ-DAST-009 | 스캔 타임아웃 | `scanner/zap_engine.py` | `tests/test_dast_engine.py::test_scan_timeout` |
| TAG-REQ-DAST-010 | 진행 상태 | `cli/commands.py` | `tests/test_dast_cli.py::test_progress_display` |
| TAG-REQ-DAST-011 | SAST+DAST 통합 | `cli/commands.py` | `tests/test_integration.py::test_combined_sast_dast` |
| TAG-REQ-DAST-012 | 구성 파일 | `scanner/zap_config.py` | `tests/test_zap_config.py` |
| TAG-REQ-DAST-013 | 신뢰도 필터링 | `cli/commands.py` | `tests/test_dast_cli.py::test_confidence_filter` |
| TAG-REQ-DAST-014 | 출력 포맷 | `reporter/json_reporter.py` | `tests/test_reporter.py::test_json_format` |

### 5.2 SPEC 의존성 다이어그램

```
SPEC-SECURITY-001 (SAST MVP - 완료)
│
├── CLI 모듈
│   ├── main.py
│   └── commands.py (기존 scan 명령어)
│
├── Scanner 모듈
│   ├── bandit_engine.py (기존)
│   └── models.py (기존)
│
└── Reporter 모듈
    ├── json_reporter.py (기존, 확장)
    └── text_reporter.py (기존, 확장)

SPEC-SECURITY-002 (DAST - 신규)
│
├── CLI 모듈 (확장)
│   └── commands.py (신규 run-dast 명령어)
│
├── Scanner 모듈 (확장)
│   ├── zap_engine.py (신규 DAST)
│   └── config/owasp_mappings.py (신규)
│
├── Reporter 모듈 (확장)
│   └── json_reporter.py (DAST 지원)
│
└── Config 모듈
    └── zap_config.py (신규)

향후 확장 SPEC
├── SPEC-SECURITY-003 (SCA + 능동 스캔 + MCP)
└── SPEC-SECURITY-004 (웹 대시보드)
```

---

## 6. Constraints (제약사항)

### 6.1 기술적 제약
- Java 8 이상 필수 (OWASP ZAP 실행)
- OWASP ZAP 설치 필요 (수동 또는 Docker)
- 네트워크 접근성: 스캔 대상 URL에 접근 가능해야 함
- 방화벽 정책: localhost:8080 (또는 구성된 포트) 통신 필요

### 6.2 성능 제약
- 스캔 시간: 작은 애플리케이션 기준 1~2분
- 메모리 사용: ZAP 프로세스 500MB~1GB
- 스캔 범위: 기본 수동 스캔만 (능동 스캔 제외)

### 6.3 보안 제약
- 테스트 환경 전용 (프로덕션 시스템 스캔 금지)
- 민감 데이터 없는 URL만 스캔
- 권한 있는 사용자만 실행
- ZAP 인스턴스는 신뢰 가능한 네트워크에 격리

### 6.4 MVP 범위 제약
- **포함**: 수동 스캔(Passive Scan), OWASP Top 10 매핑, CLI 통합
- **제외**: 능동 스캔(Active Scan), 인증 기반 스캔, SCA/IAST
- **향후**: SPEC-SECURITY-003에서 확장 예정

---

## 7. Quality Gates (품질 기준)

### 7.1 TRUST 5 원칙 준수

#### T - Test-first
- ✅ TDD 방식 개발 (Red → Green → Refactor)
- ✅ 테스트 커버리지 85% 이상
- ✅ 단위 테스트 + 통합 테스트 + 인수 테스트

#### R - Readable
- ✅ Mypy 타입 체크 100% 통과
- ✅ Ruff 린팅 규칙 모두 준수
- ✅ Docstring 작성 (Google 스타일)

#### U - Unified
- ✅ Pydantic 데이터 모델 일관성
- ✅ 에러 처리 표준화
- ✅ 로깅 포맷 통일

#### S - Secured
- ✅ URL 입력 검증
- ✅ 서브프로세스 안전 실행
- ✅ 민감 정보(API 키) 보호

#### T - Trackable
- ✅ TAG 체인으로 요구사항-코드-테스트 연결
- ✅ Git 커밋 메시지에 TAG 포함
- ✅ SPEC 문서와 코드 동기화

### 7.2 Definition of Done

- [ ] 모든 테스트 통과 (pytest)
- [ ] 테스트 커버리지 85% 이상
- [ ] Mypy, Ruff 정적 분석 통과
- [ ] README 및 DAST 가이드 작성
- [ ] DAST 명령어 도움말 완성
- [ ] OWASP ZAP 설치 가이드 제공
- [ ] 샘플 웹앱 스캔 성공
- [ ] SAST + DAST 통합 스캔 성공
- [ ] TRUST 5 원칙 모두 준수 확인

---

## 8. References (참고 자료)

### 8.1 외부 문서
- [OWASP ZAP 공식 문서](https://www.zaproxy.org/)
- [OWASP ZAP API 가이드](https://www.zaproxy.org/docs/api/)
- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP ZAP Python Client](https://pypi.org/project/python-owasp-zap-v2/)

### 8.2 관련 SPEC
- **SPEC-SECURITY-001**: Python 보안 스캐너 MVP (SAST)
- **향후**: SPEC-SECURITY-003 (SCA + 능동 스캔)

### 8.3 프로젝트 문서
- `.moai/specs/SPEC-SECURITY-001/` - 기존 SAST 스펙
- `.moai/project/tech.md` - 기술 스택
- CLAUDE.md - 프로젝트 지침

---

**문서 버전**: 0.1.0
**최종 수정**: 2025-11-17
**다음 SPEC**: SPEC-SECURITY-003 (SCA + 능동 스캔 + MCP)
