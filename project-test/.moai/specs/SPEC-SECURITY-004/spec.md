# SPEC-SECURITY-004: 보안 스캔 결과 시각화 웹 대시보드 (Streamlit)

## TAG BLOCK

```yaml
spec_id: SPEC-SECURITY-004
title: 보안 스캔 결과 시각화 웹 대시보드 (Streamlit 기반)
domain: SECURITY
status: draft
version: 0.1.0
created: 2025-11-17
author: @user
priority: MEDIUM
related_specs: [SPEC-SECURITY-001, SPEC-SECURITY-002]
dependencies:
  - SPEC-SECURITY-001 (SecurityIssue, ScanReport 모델 재사용)
  - SPEC-SECURITY-002 (DastAlert, 통합 리포트 구조)
  - Python 3.11+
  - Streamlit >= 1.41.0
```

---

## 1. Environment (환경)

### 1.1 시스템 환경
- **Python 버전**: Python 3.11 이상
- **운영체제**: Linux, macOS, Windows (크로스 플랫폼)
- **브라우저**: Chrome, Edge, Firefox (모던 브라우저)
- **네트워크**: 로컬 호스트 전용 (기본값) 또는 내부 네트워크

### 1.2 기술 스택 (전문가 검증 완료)
- **웹 프레임워크**: streamlit >= 1.41.0
- **인터랙티브 차트**: plotly >= 5.24.0
- **정적 차트**: altair >= 5.4.0 (빠른 렌더링)
- **데이터 처리**: pandas >= 2.2.0
- **기존 라이브러리**:
  - pydantic >= 2.10.0 (데이터 검증)
  - rich >= 13.9.0 (터미널 출력 - 선택)

### 1.3 선택 라이브러리
- **자동 새로고침**: streamlit-autorefresh >= 0.0.1 (실시간 모니터링)
- **PDF 내보내기**: reportlab (향후 확장)

### 1.4 개발 환경
- **패키지 관리**: uv 또는 pip
- **테스트**: pytest >= 8.3.0, pytest-cov >= 6.0.0
- **정적 분석**: mypy >= 1.13.0, ruff >= 0.8.0
- **모킹**: pytest-mock, streamlit-testing (UI 테스트)

### 1.5 프로젝트 구조
```
src/pysec/
├── cli/
│   ├── main.py           # CLI 엔트리포인트 (기존)
│   └── commands.py       # scan, run-dast 명령어 (기존)
├── scanner/
│   ├── bandit_engine.py  # SAST (기존)
│   ├── zap_engine.py     # DAST (기존)
│   └── models.py         # 공용 데이터 모델 (기존)
├── reporter/
│   ├── json_reporter.py  # JSON (기존)
│   └── text_reporter.py  # 텍스트 (기존)
├── dashboard/            # 신규 모듈
│   ├── app.py            # Streamlit 메인 앱
│   ├── pages/
│   │   ├── overview.py   # 대시보드 메인 페이지
│   │   ├── sast.py       # SAST 전용 뷰
│   │   └── dast.py       # DAST 전용 뷰
│   ├── components/
│   │   ├── charts.py     # Plotly/Altair 차트 생성
│   │   ├── tables.py     # 데이터 테이블 (필터링)
│   │   └── filters.py    # 필터 UI 컴포넌트
│   ├── data_loader.py    # JSON 파일 파싱 및 검증
│   └── security.py       # 보안 검증 (파일 업로드, 마스킹)
└── config/
    └── dashboard_config.py # 대시보드 설정

tests/
├── test_dashboard_app.py
├── test_charts.py
├── test_data_loader.py
└── test_security.py
```

---

## 2. Assumptions (가정사항)

### 2.1 사용자 가정
- 사용자는 SPEC-001/002에서 생성된 JSON 리포트를 보유함
- 사용자는 브라우저를 통해 대시보드에 접근 가능
- 사용자는 파일 업로드 및 기본 UI 조작 가능
- 사용자는 보안 전문가 또는 개발자 (도메인 지식 보유)

### 2.2 기술적 가정
- Streamlit이 로컬 또는 서버에 설치되어 있음
- JSON 리포트가 SPEC-001/002 스키마를 준수함
- 브라우저가 JavaScript 및 WebGL 지원
- 파일 업로드 시스템 메모리 10MB 이상 가용

### 2.3 범위 가정 (MVP)
- **포함**: 파일 업로드, 시각화, 필터링, 민감 정보 마스킹
- **제외**: 실시간 스캔 트리거, 데이터베이스, 다중 사용자 인증
- **향후**: SPEC-SECURITY-005 (MCP 통합 - 실시간 스캔 트리거)

### 2.4 보안 가정
- 로컬 호스트 전용 배포 (기본값)
- 신뢰할 수 있는 네트워크 환경 (내부망)
- 업로드된 JSON 파일은 검증된 스캔 도구 출력
- 민감 데이터 자동 마스킹 활성화

---

## 3. Requirements (요구사항)

### 3.1 Ubiquitous (항상 참인 요구사항)

#### REQ-DASH-001: Streamlit 웹 대시보드 제공
**설명**: 시스템은 Streamlit 기반 웹 대시보드를 제공해야 한다.

**기준**:
- Streamlit 앱이 로컬 호스트에서 실행됨
- 브라우저를 통해 http://localhost:8501 접근 가능
- 반응형 레이아웃 지원 (데스크톱 중심)

**추적성**: TAG-REQ-DASH-001

#### REQ-DASH-002: SAST/DAST JSON 리포트 파싱
**설명**: 시스템은 SPEC-001/002의 JSON 리포트를 파싱하고 시각화해야 한다.

**기준**:
- 파일 업로드 UI (st.file_uploader)
- Pydantic 모델 검증 (ScanReport, DastAlert)
- 파싱 실패 시 명확한 에러 메시지

**추적성**: TAG-REQ-DASH-002

#### REQ-DASH-003: 심각도 분포 차트
**설명**: 시스템은 취약점 심각도 분포를 Plotly Pie 차트로 표시해야 한다.

**기준**:
- Plotly Pie Chart (HIGH, MEDIUM, LOW, INFO)
- 색상 코드 (🔴 RED, 🟡 YELLOW, 🔵 BLUE, ℹ️ GRAY)
- 호버 시 개수 및 비율 표시

**추적성**: TAG-REQ-DASH-003

#### REQ-DASH-004: 취약점 상세 테이블
**설명**: 시스템은 취약점 목록을 필터링 및 정렬 가능한 테이블로 표시해야 한다.

**기준**:
- st.dataframe 사용 (인터랙티브 테이블)
- 컬럼: 심각도, 유형, 파일/URL, 라인, 설명, OWASP 카테고리
- 심각도/유형별 필터링 (st.multiselect)

**추적성**: TAG-REQ-DASH-004

#### REQ-DASH-005: 보안 검증 (파일 업로드)
**설명**: 시스템은 업로드된 파일의 보안 검증을 수행해야 한다.

**기준**:
- 파일 크기 제한 (10MB)
- 확장자 검증 (.json만 허용)
- Pydantic 스키마 검증 (ScanReport/DastAlert)

**추적성**: TAG-REQ-DASH-005

#### REQ-DASH-006: 민감 정보 자동 마스킹
**설명**: 시스템은 파일 경로 및 코드 스니펫에서 민감 정보를 자동 마스킹해야 한다.

**기준**:
- 사용자명 마스킹 (/home/user → /home/***)
- API 키/토큰 패턴 마스킹 (api_key=abc123 → api_key=***)
- 비밀번호 패턴 마스킹

**추적성**: TAG-REQ-DASH-006

### 3.2 Event-Driven (이벤트 기반 요구사항)

#### REQ-DASH-007: 파일 업로드 이벤트
**WHEN** 사용자가 JSON 파일을 업로드하면
- **THEN** 시스템은 다음을 수행한다:
  1. 파일 크기/확장자/스키마 검증
  2. JSON 파싱 및 Pydantic 모델 매핑
  3. 민감 정보 자동 마스킹
  4. 대시보드 자동 렌더링

**추적성**: TAG-REQ-DASH-007

#### REQ-DASH-008: 필터 변경 이벤트
**WHEN** 사용자가 심각도 또는 유형 필터를 변경하면
- **THEN** 시스템은:
  - 차트 및 테이블을 즉시 업데이트
  - 필터된 항목 개수 표시
  - 빈 결과 시 "필터 조건과 일치하는 항목이 없습니다" 메시지

**추적성**: TAG-REQ-DASH-008

### 3.3 Unwanted (원하지 않는 상황 처리)

#### REQ-DASH-009: 잘못된 파일 형식 처리
**IF** 업로드된 파일이 유효하지 않은 JSON이면
- **THEN** 시스템은:
  - "유효하지 않은 JSON 형식입니다" 에러 메시지
  - 재업로드 버튼 표시
  - 샘플 JSON 형식 안내

**추적성**: TAG-REQ-DASH-009

#### REQ-DASH-010: 스키마 불일치 처리
**IF** JSON이 ScanReport 스키마와 일치하지 않으면
- **THEN** 시스템은:
  - "스캔 리포트 형식이 올바르지 않습니다" 메시지
  - 필수 필드 목록 표시
  - SPEC-001/002 문서 링크 제공

**추적성**: TAG-REQ-DASH-010

#### REQ-DASH-011: 대용량 데이터 처리
**IF** 업로드된 파일에 1000개 이상의 이슈가 있으면
- **THEN** 시스템은:
  - 처음 100개만 테이블에 표시
  - "전체 {count}개 중 100개 표시" 메시지
  - 페이지네이션 또는 "더보기" 버튼

**추적성**: TAG-REQ-DASH-011

### 3.4 State-Driven (상태 기반 요구사항)

#### REQ-DASH-012: 대시보드 실행 중 상태
**WHILE** 대시보드가 실행 중일 때
- **THEN** 시스템은:
  - 사이드바에 필터 UI 표시
  - 메인 패널에 차트 및 테이블 표시
  - 상태바에 "실행 중" 표시

**추적성**: TAG-REQ-DASH-012

#### REQ-DASH-013: 실시간 모니터링 상태 (선택)
**WHILE** 자동 새로고침이 활성화되어 있으면
- **THEN** 시스템은:
  - 30초마다 JSON 파일 재로드 (파일 경로 지정 시)
  - 새로운 이슈 자동 감지
  - 변경 사항 알림 표시

**추적성**: TAG-REQ-DASH-013

### 3.5 Optional (선택적 요구사항)

#### REQ-DASH-014: OWASP Top 10 매핑 차트
**WHERE** DAST 리포트가 업로드되면
- **THEN** 시스템은 OWASP Top 10 카테고리별 Bar 차트를 표시한다 (Altair)

**추적성**: TAG-REQ-DASH-014

#### REQ-DASH-015: 과거 스캔 비교 (트렌드)
**WHERE** 여러 스캔 리포트가 업로드되면
- **THEN** 시스템은 시간별 심각도 추세 Line 차트를 표시한다 (Plotly)

**추적성**: TAG-REQ-DASH-015

#### REQ-DASH-016: 다크 모드 지원
**WHERE** 사용자가 다크 모드를 선택하면
- **THEN** 시스템은 다크 테마로 차트 및 UI를 변경한다

**추적성**: TAG-REQ-DASH-016

---

## 4. Specifications (상세 명세)

### 4.1 Streamlit 앱 구조

#### 메인 앱 (app.py)
```python
import streamlit as st
from dashboard.pages import overview, sast, dast
from dashboard.data_loader import load_scan_report
from dashboard.security import validate_upload, mask_sensitive_data

st.set_page_config(
    page_title="Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바
with st.sidebar:
    st.title("🛡️ Security Dashboard")

    # 파일 업로드
    uploaded_file = st.file_uploader(
        "Upload JSON Report",
        type=["json"],
        help="SPEC-001/002에서 생성된 JSON 리포트"
    )

    if uploaded_file:
        # 보안 검증
        try:
            data = validate_upload(uploaded_file)
            st.success("✅ 파일 검증 완료")
        except ValueError as e:
            st.error(f"❌ {e}")
            st.stop()

    # 필터
    severity_filter = st.multiselect(
        "Severity Filter",
        ["HIGH", "MEDIUM", "LOW", "INFO"],
        default=["HIGH", "MEDIUM", "LOW"]
    )

    # 페이지 선택
    page = st.selectbox("View", ["Overview", "SAST Details", "DAST Details"])

# 메인 패널
if uploaded_file:
    if page == "Overview":
        overview.render(data, severity_filter)
    elif page == "SAST Details":
        sast.render(data, severity_filter)
    else:
        dast.render(data, severity_filter)
else:
    st.info("👈 JSON 리포트를 업로드하세요")
```

### 4.2 차트 생성 명세 (전문가 권장)

#### Plotly Pie Chart (심각도 분포)
```python
import plotly.express as px

def create_severity_pie_chart(df):
    """심각도 분포 Pie Chart (Plotly)"""
    severity_counts = df['severity'].value_counts()

    colors = {
        'HIGH': '#FF4B4B',    # RED
        'MEDIUM': '#FFA500',  # ORANGE
        'LOW': '#4B9FFF',     # BLUE
        'INFO': '#808080'     # GRAY
    }

    fig = px.pie(
        values=severity_counts.values,
        names=severity_counts.index,
        title='Severity Distribution',
        color=severity_counts.index,
        color_discrete_map=colors,
        hole=0.4  # Donut chart
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}'
    )

    return fig
```

#### Altair Bar Chart (OWASP Top 10)
```python
import altair as alt

def create_owasp_bar_chart(df):
    """OWASP Top 10 카테고리 Bar Chart (Altair)"""
    owasp_counts = df['owasp_category'].value_counts().reset_index()
    owasp_counts.columns = ['category', 'count']

    chart = alt.Chart(owasp_counts).mark_bar().encode(
        x=alt.X('count:Q', title='Number of Issues'),
        y=alt.Y('category:N', title='OWASP Category', sort='-x'),
        color=alt.Color('count:Q', scale=alt.Scale(scheme='reds')),
        tooltip=['category', 'count']
    ).properties(
        title='OWASP Top 10 Distribution',
        width=600,
        height=400
    )

    return chart
```

### 4.3 데이터 로더 및 검증

#### 파일 업로드 검증 (보안)
```python
import json
from pathlib import Path
from pydantic import ValidationError
from scanner.models import ScanReport

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = [".json"]

def validate_upload(file) -> dict:
    """파일 업로드 보안 검증 (3단계)"""
    # 1. 크기 검증
    if file.size > MAX_FILE_SIZE:
        raise ValueError("파일 크기는 10MB 이하여야 합니다")

    # 2. 확장자 검증
    if not file.name.endswith(tuple(ALLOWED_EXTENSIONS)):
        raise ValueError("JSON 파일만 업로드 가능합니다")

    # 3. JSON 파싱
    try:
        data = json.load(file)
    except json.JSONDecodeError as e:
        raise ValueError(f"유효하지 않은 JSON 형식입니다: {e}")

    # 4. 스키마 검증 (Pydantic)
    try:
        ScanReport(**data)
    except ValidationError as e:
        raise ValueError(f"스캔 리포트 형식이 올바르지 않습니다: {e}")

    return data
```

#### 민감 정보 마스킹
```python
import re

def mask_sensitive_data(text: str) -> str:
    """민감 정보 자동 마스킹 (정규식 기반)"""
    # 파일 경로 사용자명 마스킹
    text = re.sub(r'/home/[^/]+/', '/home/***/', text)
    text = re.sub(r'C:\\Users\\[^\\]+\\', 'C:\\Users\\***\\', text)

    # API 키 패턴
    text = re.sub(
        r'(api[_-]?key|token|secret)["\']?\s*[:=]\s*["\']?[\w-]{20,}',
        r'\1=***REDACTED***',
        text,
        flags=re.IGNORECASE
    )

    # 비밀번호 패턴
    text = re.sub(
        r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']?[^\s"\']+',
        r'\1=***REDACTED***',
        text,
        flags=re.IGNORECASE
    )

    return text
```

### 4.4 대용량 데이터 최적화 (전문가 권장)

#### 페이지네이션 전략
```python
import streamlit as st
import pandas as pd

@st.cache_data
def load_scan_data(file):
    """JSON 파일 로드 및 캐싱"""
    return pd.read_json(file)

def render_paginated_table(df, page_size=100):
    """페이지네이션 테이블"""
    total_rows = len(df)
    total_pages = (total_rows + page_size - 1) // page_size

    # 페이지 선택
    page = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=1
    )

    # 현재 페이지 데이터
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_rows)

    st.info(f"Showing {start_idx + 1} - {end_idx} of {total_rows} issues")
    st.dataframe(df.iloc[start_idx:end_idx])
```

### 4.5 Streamlit 설정 (.streamlit/config.toml)

```toml
[server]
port = 8501
address = "localhost"  # 로컬 전용
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 10  # 10MB

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[browser]
gatherUsageStats = false
```

---

## 5. Traceability (추적성)

### 5.1 TAG 체인

| TAG ID | 요구사항 | 구현 파일 | 테스트 파일 |
|--------|----------|-----------|-------------|
| TAG-REQ-DASH-001 | Streamlit 앱 | `dashboard/app.py` | `tests/test_dashboard_app.py` |
| TAG-REQ-DASH-002 | JSON 파싱 | `dashboard/data_loader.py` | `tests/test_data_loader.py` |
| TAG-REQ-DASH-003 | 심각도 차트 | `dashboard/components/charts.py` | `tests/test_charts.py::test_severity_pie` |
| TAG-REQ-DASH-004 | 취약점 테이블 | `dashboard/components/tables.py` | `tests/test_tables.py` |
| TAG-REQ-DASH-005 | 보안 검증 | `dashboard/security.py` | `tests/test_security.py::test_validate_upload` |
| TAG-REQ-DASH-006 | 민감 정보 마스킹 | `dashboard/security.py` | `tests/test_security.py::test_mask_sensitive` |
| TAG-REQ-DASH-007 | 파일 업로드 | `dashboard/app.py` | `tests/test_dashboard_app.py::test_file_upload` |
| TAG-REQ-DASH-008 | 필터 변경 | `dashboard/components/filters.py` | `tests/test_filters.py` |
| TAG-REQ-DASH-009 | 잘못된 형식 | `dashboard/data_loader.py` | `tests/test_data_loader.py::test_invalid_json` |
| TAG-REQ-DASH-010 | 스키마 불일치 | `dashboard/data_loader.py` | `tests/test_data_loader.py::test_schema_mismatch` |
| TAG-REQ-DASH-011 | 대용량 데이터 | `dashboard/components/tables.py` | `tests/test_tables.py::test_pagination` |
| TAG-REQ-DASH-012 | 실행 상태 | `dashboard/app.py` | `tests/test_dashboard_app.py::test_state` |
| TAG-REQ-DASH-013 | 자동 새로고침 | `dashboard/app.py` | `tests/test_dashboard_app.py::test_autorefresh` |
| TAG-REQ-DASH-014 | OWASP 차트 | `dashboard/components/charts.py` | `tests/test_charts.py::test_owasp_bar` |
| TAG-REQ-DASH-015 | 트렌드 분석 | `dashboard/pages/overview.py` | `tests/test_overview.py::test_trend_chart` |
| TAG-REQ-DASH-016 | 다크 모드 | `.streamlit/config.toml` | `tests/test_theme.py` |

### 5.2 SPEC 의존성 다이어그램

```
SPEC-SECURITY-001 (SAST MVP - 완료)
├── SecurityIssue 모델
├── ScanReport 모델
└── JSON 출력 형식

SPEC-SECURITY-002 (DAST - 완료)
├── DastAlert 모델
├── 통합 리포트 구조
└── OWASP Top 10 매핑

SPEC-SECURITY-004 (Dashboard - 신규)
├── 데이터 소스: SPEC-001/002 JSON 출력
├── 모델 재사용: SecurityIssue, ScanReport, DastAlert
├── 시각화 레이어
│   ├── Plotly (인터랙티브 차트)
│   ├── Altair (정적 차트)
│   └── Streamlit (웹 UI)
└── 보안 레이어
    ├── 파일 업로드 검증
    └── 민감 정보 마스킹

향후 확장 SPEC
└── SPEC-SECURITY-005 (MCP 통합)
    └── 실시간 스캔 트리거 → 대시보드 자동 업데이트
```

---

## 6. Constraints (제약사항)

### 6.1 기술적 제약
- Python 3.11 이상 필수 (Streamlit 최신 버전)
- 모던 브라우저 필수 (Chrome, Edge, Firefox)
- JavaScript 및 WebGL 지원 필요 (Plotly)
- 시스템 메모리 최소 512MB (대용량 JSON 처리 시)

### 6.2 성능 제약
- 파일 업로드 최대 10MB (Streamlit 기본 제한)
- 1000개 이상 이슈 시 페이지네이션 필수
- 차트 렌더링 시간: 100개 이슈 기준 1초 이하
- 자동 새로고침 간격: 최소 30초 (서버 부하 방지)

### 6.3 보안 제약
- 로컬 호스트 전용 배포 (기본값)
- 파일 업로드 크기/확장자/스키마 3단계 검증
- 민감 정보 자동 마스킹 필수
- HTTPS 사용 권장 (원격 접근 시)

### 6.4 MVP 범위 제약
- **포함**: 파일 업로드, 시각화, 필터링, 보안 검증
- **제외**: 실시간 스캔 트리거, 데이터베이스, 다중 사용자 인증, PDF 내보내기
- **향후**: SPEC-SECURITY-005 (MCP 통합), 006 (인증 레이어)

---

## 7. Quality Gates (품질 기준)

### 7.1 TRUST 5 원칙 준수

#### T - Test-first
- ✅ TDD 방식 개발 (Red → Green → Refactor)
- ✅ 테스트 커버리지 85% 이상
- ✅ 단위 테스트 + Streamlit UI 테스트 (streamlit-testing)

#### R - Readable
- ✅ Mypy 타입 체크 100% 통과
- ✅ Ruff 린팅 규칙 준수
- ✅ Docstring 작성 (Google 스타일)

#### U - Unified
- ✅ Pydantic 모델 재사용 (SPEC-001/002)
- ✅ 일관된 차트 색상 스키마
- ✅ 에러 처리 표준화

#### S - Secured
- ✅ 파일 업로드 3단계 검증
- ✅ 민감 정보 자동 마스킹
- ✅ OWASP 보안 권장사항 준수

#### T - Trackable
- ✅ TAG 체인으로 요구사항-코드-테스트 연결
- ✅ Git 커밋 메시지에 TAG 포함
- ✅ SPEC 문서와 코드 동기화

### 7.2 Definition of Done

- [ ] 모든 테스트 통과 (pytest + streamlit-testing)
- [ ] 테스트 커버리지 85% 이상
- [ ] Mypy, Ruff 정적 분석 통과
- [ ] Streamlit 앱 로컬 실행 성공
- [ ] SAST 및 DAST JSON 파일 업로드 및 시각화 성공
- [ ] 민감 정보 마스킹 동작 확인
- [ ] 1000개 이슈 데이터 페이지네이션 테스트
- [ ] 보안 검증 (파일 크기/확장자/스키마) 통과
- [ ] README 및 사용자 가이드 작성
- [ ] TRUST 5 원칙 모두 준수 확인

---

## 8. References (참고 자료)

### 8.1 외부 문서
- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [Plotly 공식 문서](https://plotly.com/python/)
- [Altair 공식 문서](https://altair-viz.github.io/)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

### 8.2 관련 SPEC
- **SPEC-SECURITY-001**: Python 보안 스캐너 MVP (SAST)
- **SPEC-SECURITY-002**: 웹 애플리케이션 동적 보안 분석 (DAST)
- **향후**: SPEC-SECURITY-005 (MCP 통합 - 실시간 스캔)

### 8.3 프로젝트 문서
- `.moai/specs/SPEC-SECURITY-001/` - SAST 스펙 (데이터 모델)
- `.moai/specs/SPEC-SECURITY-002/` - DAST 스펙 (통합 리포트)
- `.moai/project/tech.md` - 기술 스택
- CLAUDE.md - 프로젝트 지침

### 8.4 전문가 상담 결과
- **Frontend Expert**: Streamlit + Plotly/Altair 하이브리드 권장
- **Security Expert**: 3단계 파일 검증 + 민감 정보 마스킹 필수

---

**문서 버전**: 0.1.0
**최종 수정**: 2025-11-17
**다음 SPEC**: SPEC-SECURITY-005 (MCP 통합 - 실시간 스캔 트리거)
