# SPEC-SECURITY-001: Python 보안 스캐너 MVP

## TAG BLOCK

```yaml
spec_id: SPEC-SECURITY-001
title: Python 보안 스캐너 MVP (CLI + Bandit SAST)
domain: SECURITY
status: draft
version: 0.1.0
created: 2025-11-17
author: @user
priority: HIGH
dependencies: []
related_specs: []
```

---

## 1. Environment (환경)

### 1.1 시스템 환경
- **Python 버전**: Python 3.11 이상
- **운영체제**: Linux, macOS, Windows (크로스 플랫폼)
- **터미널**: ANSI 색상 지원 터미널 권장

### 1.2 기술 스택
- **CLI 프레임워크**: typer>=0.20.0
- **SAST 스캐너**: bandit>=1.8.6
- **터미널 UI**: rich>=13.9.0
- **데이터 검증**: pydantic>=2.10.0
- **로깅**: loguru>=0.7.0

### 1.3 개발 환경
- **패키지 관리**: uv (UV) 또는 pip
- **테스트**: pytest>=8.3.0, pytest-cov>=6.0.0
- **정적 분석**: mypy>=1.13.0, ruff>=0.8.0
- **버전 관리**: Git

### 1.4 프로젝트 구조
```
src/pysec/
├── cli/          # CLI 인터페이스
├── scanner/      # Bandit 스캐너 통합
└── reporter/     # JSON/텍스트 리포터

tests/            # 테스트 코드
pyproject.toml    # 프로젝트 설정
```

---

## 2. Assumptions (가정사항)

### 2.1 사용자 가정
- 사용자는 Python 프로젝트를 스캔 대상으로 제공함
- 사용자는 터미널에서 CLI 명령어를 실행할 수 있음
- 사용자는 JSON 또는 텍스트 형식 리포트를 이해할 수 있음

### 2.2 기술적 가정
- Bandit이 Python 패키지로 정상적으로 설치 가능함
- 스캔 대상 디렉토리는 읽기 권한이 있음
- 터미널 출력이 UTF-8 인코딩을 지원함

### 2.3 범위 가정 (MVP)
- **포함**: SAST (Bandit만), CLI, 기본 리포팅
- **제외**: DAST, SCA, MCP 통합, 웹 대시보드, 데이터베이스
- 향후 SPEC-SECURITY-002, 003으로 확장 예정

---

## 3. Requirements (요구사항)

### 3.1 Ubiquitous (항상 참인 요구사항)

#### REQ-SEC-001: Bandit 통합
**설명**: 시스템은 Bandit을 사용하여 Python 코드의 보안 취약점을 탐지해야 한다.

**기준**:
- Bandit CLI를 서브프로세스로 실행
- 스캔 결과를 JSON 형식으로 파싱
- OWASP Top 10 분류 체계 매핑

**추적성**: TAG-REQ-SEC-001

#### REQ-SEC-002: CLI 인터페이스
**설명**: 시스템은 사용자 친화적인 CLI 인터페이스를 제공해야 한다.

**기준**:
- `pysec scan <path>` 명령어 지원
- `--format`, `--severity` 옵션 지원
- 도움말 및 사용 예제 제공

**추적성**: TAG-REQ-SEC-002

#### REQ-SEC-003: 리포팅 형식
**설명**: 시스템은 JSON 및 텍스트 형식으로 스캔 결과를 출력해야 한다.

**기준**:
- JSON: 구조화된 데이터 (프로그래밍 가능)
- 텍스트: 사람이 읽기 쉬운 형식 (터미널 출력)
- Rich 라이브러리를 사용한 색상 구분

**추적성**: TAG-REQ-SEC-003

#### REQ-SEC-004: 심각도 분류
**설명**: 시스템은 탐지된 취약점을 HIGH/MEDIUM/LOW로 분류해야 한다.

**기준**:
- Bandit의 severity 레벨을 표준 심각도로 변환
- 심각도별 필터링 지원
- 통계 정보 제공 (총 개수, 심각도별 개수)

**추적성**: TAG-REQ-SEC-004

### 3.2 Event-Driven (이벤트 기반 요구사항)

#### REQ-SEC-005: 스캔 실행 이벤트
**WHEN** 사용자가 `pysec scan <path>` 명령을 실행하면
- **THEN** 시스템은 다음을 수행한다:
  1. 스캔 대상 경로 유효성 검증
  2. Bandit 스캐너 실행
  3. 실시간 진행률 프로그레스 바 표시
  4. 스캔 완료 시 결과 출력

**추적성**: TAG-REQ-SEC-005

#### REQ-SEC-006: 취약점 발견 이벤트
**WHEN** Bandit이 보안 취약점을 발견하면
- **THEN** 시스템은 다음 정보를 기록한다:
  - 파일 경로 및 라인 번호
  - 취약점 유형 (예: B105 하드코딩된 패스워드)
  - 심각도 수준
  - 수정 권장사항

**추적성**: TAG-REQ-SEC-006

### 3.3 Unwanted (원하지 않는 상황 처리)

#### REQ-SEC-007: 잘못된 경로 처리
**IF** 스캔 대상 경로가 존재하지 않거나 접근 불가능하면
- **THEN** 시스템은:
  - 명확한 에러 메시지 출력
  - 예제 사용법 표시
  - 종료 코드 1로 종료

**추적성**: TAG-REQ-SEC-007

#### REQ-SEC-008: Bandit 실행 실패
**IF** Bandit 실행 중 오류가 발생하면
- **THEN** 시스템은:
  - 상세한 에러 로그 출력
  - 디버깅 정보 제공 (Bandit 버전, 명령어)
  - 종료 코드 2로 종료

**추적성**: TAG-REQ-SEC-008

### 3.4 State-Driven (상태 기반 요구사항)

#### REQ-SEC-009: 스캔 진행 중 상태
**WHILE** 스캔이 실행 중일 때
- **THEN** 시스템은:
  - Rich 프로그레스 바로 진행률 표시
  - 현재 스캔 중인 파일 표시
  - 발견된 이슈 카운트 실시간 업데이트

**추적성**: TAG-REQ-SEC-009

### 3.5 Optional (선택적 요구사항)

#### REQ-SEC-010: JSON 출력 옵션
**WHERE** 사용자가 `--format json` 옵션을 지정하면
- **THEN** 시스템은 JSON 형식으로 결과를 출력한다

**추적성**: TAG-REQ-SEC-010

#### REQ-SEC-011: 심각도 필터링 옵션
**WHERE** 사용자가 `--severity HIGH` 옵션을 지정하면
- **THEN** 시스템은 HIGH 심각도 취약점만 표시한다

**추적성**: TAG-REQ-SEC-011

---

## 4. Specifications (상세 명세)

### 4.1 CLI 명령어 인터페이스

#### 명령어 구조
```bash
pysec scan <TARGET_PATH> [OPTIONS]
```

#### 옵션
| 옵션 | 설명 | 기본값 | 예제 |
|------|------|--------|------|
| `--format` | 출력 형식 (text, json) | text | `--format json` |
| `--severity` | 심각도 필터 (ALL, HIGH, MEDIUM, LOW) | ALL | `--severity HIGH` |
| `--output` | 파일로 저장 | stdout | `--output report.json` |
| `--verbose` | 상세 로그 출력 | False | `--verbose` |

#### 사용 예제
```bash
# 기본 스캔
pysec scan ./my_project

# JSON 출력
pysec scan ./my_project --format json

# HIGH 심각도만 필터링
pysec scan ./my_project --severity HIGH

# 파일로 저장
pysec scan ./my_project --format json --output report.json
```

### 4.2 Bandit 통합 명세

#### 실행 방식
- **서브프로세스**: `subprocess.run()` 사용
- **명령어**: `bandit -r <path> -f json`
- **타임아웃**: 300초 (5분)

#### 결과 파싱
```python
# Bandit JSON 출력 구조
{
  "results": [
    {
      "filename": "app/config.py",
      "line_number": 42,
      "issue_severity": "HIGH",
      "issue_confidence": "HIGH",
      "issue_text": "Hardcoded password string",
      "test_id": "B105",
      "test_name": "hardcoded_password_string"
    }
  ],
  "metrics": {
    "total_lines": 1024,
    "total_issues": 5
  }
}
```

#### OWASP 매핑
| Bandit 테스트 ID | OWASP 카테고리 | 심각도 |
|------------------|----------------|--------|
| B105 | A02:2021 – Cryptographic Failures | HIGH |
| B201 | A03:2021 – Injection | HIGH |
| B501 | A02:2021 – Cryptographic Failures | MEDIUM |

### 4.3 리포팅 형식 명세

#### 텍스트 출력 (기본)
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

[1] Hardcoded password
  File: app/config.py:42
  Type: B105 (hardcoded_password_string)
  Fix: Use environment variables or secrets management

[2] SQL Injection Risk
  File: app/db.py:18
  Type: B608 (hardcoded_sql_expressions)
  Fix: Use parameterized queries

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### JSON 출력 (--format json)
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

### 4.4 데이터 모델 (Pydantic)

```python
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class SecurityIssue(BaseModel):
    """단일 보안 취약점 모델"""
    id: str = Field(description="고유 이슈 ID")
    severity: Literal["HIGH", "MEDIUM", "LOW"]
    type: str = Field(description="Bandit 테스트 ID (예: B105)")
    category: str = Field(description="취약점 카테고리")
    file: str = Field(description="파일 경로")
    line: int = Field(description="라인 번호")
    code_snippet: str = Field(description="문제 코드")
    description: str = Field(description="취약점 설명")
    owasp_category: str | None = Field(default=None)
    remediation: str = Field(description="수정 방법")

class ScanSummary(BaseModel):
    """스캔 요약 통계"""
    total_issues: int
    high: int
    medium: int
    low: int

class ScanReport(BaseModel):
    """전체 스캔 리포트"""
    scan_id: str
    timestamp: datetime
    target_path: str
    summary: ScanSummary
    issues: list[SecurityIssue]
    metadata: dict
```

---

## 5. Traceability (추적성)

### 5.1 TAG 체인

| TAG ID | 요구사항 | 구현 파일 | 테스트 파일 |
|--------|----------|-----------|-------------|
| TAG-REQ-SEC-001 | Bandit 통합 | `scanner/bandit_engine.py` | `tests/test_scanner.py` |
| TAG-REQ-SEC-002 | CLI 인터페이스 | `cli/main.py`, `cli/commands.py` | `tests/test_cli.py` |
| TAG-REQ-SEC-003 | 리포팅 형식 | `reporter/json_reporter.py`, `reporter/text_reporter.py` | `tests/test_reporter.py` |
| TAG-REQ-SEC-004 | 심각도 분류 | `scanner/models.py` | `tests/test_models.py` |
| TAG-REQ-SEC-005 | 스캔 실행 | `cli/commands.py` | `tests/test_cli.py::test_scan_execution` |
| TAG-REQ-SEC-006 | 취약점 발견 | `scanner/bandit_engine.py` | `tests/test_scanner.py::test_vulnerability_detection` |
| TAG-REQ-SEC-007 | 잘못된 경로 | `cli/commands.py` | `tests/test_cli.py::test_invalid_path` |
| TAG-REQ-SEC-008 | Bandit 실패 | `scanner/bandit_engine.py` | `tests/test_scanner.py::test_bandit_failure` |
| TAG-REQ-SEC-009 | 진행 상태 | `cli/commands.py` | `tests/test_cli.py::test_progress_display` |
| TAG-REQ-SEC-010 | JSON 출력 | `reporter/json_reporter.py` | `tests/test_reporter.py::test_json_output` |
| TAG-REQ-SEC-011 | 심각도 필터 | `cli/commands.py` | `tests/test_cli.py::test_severity_filter` |

### 5.2 SPEC 의존성 다이어그램

```
SPEC-SECURITY-001 (MVP)
├── CLI 모듈
│   ├── main.py (엔트리포인트)
│   └── commands.py (scan 명령어)
├── Scanner 모듈
│   ├── bandit_engine.py (Bandit 통합)
│   └── models.py (데이터 모델)
└── Reporter 모듈
    ├── json_reporter.py (JSON 출력)
    └── text_reporter.py (텍스트 출력)

향후 확장 SPEC
├── SPEC-SECURITY-002 (SCA + DAST)
└── SPEC-SECURITY-003 (웹 대시보드 + MCP)
```

---

## 6. Constraints (제약사항)

### 6.1 기술적 제약
- Python 3.11 이상 필수 (타입 힌팅, async 기능 활용)
- Bandit 설치 필요 (자동 설치 또는 수동 설치)
- ANSI 터미널 환경 권장 (Windows에서는 Windows Terminal 사용)

### 6.2 성능 제약
- 대규모 프로젝트 (10,000+ 파일) 스캔 시 5분 이상 소요 가능
- 메모리 사용량: 최대 500MB (Bandit 프로세스 포함)

### 6.3 보안 제약
- 스캔 대상 코드는 로컬 파일 시스템에서만 접근
- 네트워크 통신 없음 (오프라인 사용 가능)

### 6.4 MVP 범위 제약
- **포함되지 않음**: DAST, SCA, 웹 대시보드, 데이터베이스, MCP 통합
- **향후 추가**: SPEC-SECURITY-002, 003에서 확장

---

## 7. Quality Gates (품질 기준)

### 7.1 TRUST 5 원칙 준수

#### T - Test-first (테스트 우선)
- ✅ TDD 방식으로 개발 (Red → Green → Refactor)
- ✅ 테스트 커버리지 85% 이상
- ✅ 단위 테스트 + 통합 테스트

#### R - Readable (가독성)
- ✅ Mypy 타입 체크 통과
- ✅ Ruff 린팅 규칙 준수
- ✅ Docstring 작성 (Google 스타일)

#### U - Unified (일관성)
- ✅ Pydantic 데이터 모델 사용
- ✅ 일관된 에러 처리
- ✅ 로깅 표준화 (Loguru)

#### S - Secured (보안)
- ✅ 사용자 입력 검증 (경로 검증)
- ✅ 서브프로세스 안전 실행 (shell=False)
- ✅ 에러 메시지에 민감 정보 노출 금지

#### T - Trackable (추적성)
- ✅ TAG 체인으로 요구사항-코드-테스트 연결
- ✅ Git 커밋 메시지에 TAG 포함
- ✅ SPEC 문서와 코드 동기화

### 7.2 Definition of Done

- [ ] 모든 테스트 통과
- [ ] 테스트 커버리지 85% 이상
- [ ] Mypy, Ruff 정적 분석 통과
- [ ] README.md 작성 (설치, 사용법)
- [ ] CLI 도움말 메시지 완성
- [ ] 샘플 프로젝트 스캔 성공

---

## 8. References (참고 자료)

### 8.1 외부 문서
- [Bandit 공식 문서](https://bandit.readthedocs.io/)
- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [Typer 공식 문서](https://typer.tiangolo.com/)
- [Rich 공식 문서](https://rich.readthedocs.io/)

### 8.2 관련 SPEC
- **향후**: SPEC-SECURITY-002 (SCA + DAST)
- **향후**: SPEC-SECURITY-003 (웹 대시보드 + MCP)

### 8.3 프로젝트 문서
- `.moai/project/product.md` - 제품 비전
- `.moai/project/structure.md` - 아키텍처 설계
- `.moai/project/tech.md` - 기술 스택

---

**문서 버전**: 0.1.0
**최종 수정**: 2025-11-17
**다음 SPEC**: SPEC-SECURITY-002 (SCA + DAST 통합)
