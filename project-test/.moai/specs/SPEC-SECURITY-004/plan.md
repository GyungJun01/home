# SPEC-SECURITY-004 구현 계획서 (Implementation Plan)

## TAG BLOCK

```yaml
spec_id: SPEC-SECURITY-004
title: 보안 스캔 결과 시각화 웹 대시보드 구현 계획
domain: SECURITY
status: draft
version: 0.1.0
created: 2025-11-17
author: @user
```

---

## 1. 개요 (Overview)

### 1.1 목표
Streamlit 기반 웹 대시보드를 구축하여 SPEC-001/002에서 생성된 보안 스캔 리포트를 시각화하고, 사용자 친화적인 인터페이스를 통해 취약점 분석 및 필터링 기능을 제공한다.

### 1.2 전문가 검증 완료
- **Frontend Expert**: Streamlit + Plotly/Altair 하이브리드 아키텍처 승인
- **Security Expert**: 파일 업로드 검증 + 민감 정보 마스킹 전략 승인

### 1.3 예상 복잡도
- **전체 복잡도**: **Medium** (프론트엔드 시각화 + 보안 검증)
- **도메인**: Frontend (Streamlit), Security (파일 검증), Data Visualization (Plotly/Altair)

---

## 2. 기술 아키텍처 (Technical Architecture)

### 2.1 시스템 구조

```
┌─────────────────────────────────────────────────────────────┐
│                  Browser (User Interface)                   │
│  http://localhost:8501                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│          Streamlit Frontend (dashboard/app.py)              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │  File Upload   │  │  Filters UI    │  │  Navigation   │ │
│  │  (st.file_uploader) │  (st.multiselect) │  (st.selectbox) │
│  └────────────────┘  └────────────────┘  └───────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│          Data Layer (dashboard/data_loader.py)              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  validate_upload() → 3-step validation               │  │
│  │    1. File size check (10MB limit)                   │  │
│  │    2. Extension check (.json only)                   │  │
│  │    3. Pydantic schema validation                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  mask_sensitive_data() → Regex-based masking         │  │
│  │    - User names in paths (/home/user → /home/***)   │  │
│  │    - API keys (api_key=abc → api_key=***)           │  │
│  │    - Passwords (password=123 → password=***)        │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│      Visualization Layer (dashboard/components/)            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │  Plotly Charts   │  │  Altair Charts   │  │  Tables   │ │
│  │  (Interactive)   │  │  (Static/Fast)   │  │  (Pandas) │ │
│  │  - Severity Pie  │  │  - OWASP Bar     │  │  - Issues │ │
│  │  - Trend Line    │  │  - Category Bar  │  │  - Filter │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│      Data Models (scanner/models.py - Reused)               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SecurityIssue (SPEC-001)                            │  │
│  │  ScanReport (SPEC-001)                               │  │
│  │  DastAlert (SPEC-002)                                │  │
│  │  UnifiedReport (SPEC-002)                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 기술 스택 정리

| 레이어 | 라이브러리 | 버전 | 용도 |
|--------|-----------|------|------|
| **웹 프레임워크** | streamlit | >=1.41.0 | 웹 앱 기반 |
| **인터랙티브 차트** | plotly | >=5.24.0 | Pie, Line 차트 |
| **정적 차트** | altair | >=5.4.0 | Bar 차트 (빠른 렌더링) |
| **데이터 처리** | pandas | >=2.2.0 | 필터링/집계 |
| **데이터 검증** | pydantic | >=2.10.0 | 스키마 검증 (재사용) |
| **자동 새로고침** | streamlit-autorefresh | >=0.0.1 | 실시간 모니터링 (선택) |

### 2.3 모듈 분리 전략

```
dashboard/
├── app.py               # 메인 앱 (엔트리포인트)
├── pages/               # 페이지별 뷰
│   ├── overview.py      # 통합 대시보드 (SAST+DAST)
│   ├── sast.py          # SAST 전용 뷰
│   └── dast.py          # DAST 전용 뷰
├── components/          # 재사용 가능한 UI 컴포넌트
│   ├── charts.py        # Plotly/Altair 차트 생성
│   ├── tables.py        # DataGrid + 필터링
│   └── filters.py       # 필터 UI (심각도/유형)
├── data_loader.py       # JSON 파싱 + 캐싱
├── security.py          # 보안 검증 + 마스킹
└── config/
    └── dashboard_config.py  # 설정 (포트, 테마 등)
```

---

## 3. 구현 계획 (4단계 마일스톤)

### 🎯 Primary Goal (필수 기능 - 1주차)

**목표**: MVP 대시보드 완성 (파일 업로드 → 시각화 → 필터링)

#### Phase 1A: 프로젝트 초기화 및 기본 구조 생성
**TAG**: TAG-REQ-DASH-001, TAG-REQ-DASH-002

**작업 내역**:
1. **프로젝트 구조 생성**
   ```bash
   mkdir -p src/pysec/dashboard/{pages,components,config}
   touch src/pysec/dashboard/app.py
   touch src/pysec/dashboard/{data_loader.py,security.py}
   touch src/pysec/dashboard/pages/{overview.py,sast.py,dast.py}
   touch src/pysec/dashboard/components/{charts.py,tables.py,filters.py}
   ```

2. **의존성 설치**
   ```bash
   # pyproject.toml 업데이트
   [project.optional-dependencies]
   dashboard = [
       "streamlit>=1.41.0",
       "plotly>=5.24.0",
       "altair>=5.4.0",
       "pandas>=2.2.0",
   ]

   # 설치
   uv pip install -e ".[dashboard]"
   ```

3. **Streamlit 기본 설정**
   ```bash
   mkdir -p .streamlit
   cat <<EOF > .streamlit/config.toml
   [server]
   port = 8501
   address = "localhost"
   enableCORS = false
   enableXsrfProtection = true
   maxUploadSize = 10

   [theme]
   primaryColor = "#FF4B4B"
   backgroundColor = "#FFFFFF"
   textColor = "#262730"
   EOF
   ```

4. **메인 앱 뼈대 구현 (TDD)**
   - **Test First**:
     ```python
     # tests/test_dashboard_app.py
     def test_app_initialization():
         """앱이 정상적으로 초기화되는지 검증"""
         assert st.title("Security Dashboard")

     def test_sidebar_file_uploader():
         """사이드바에 파일 업로더 존재 확인"""
         assert st.sidebar.file_uploader("Upload JSON Report")
     ```

   - **Implementation**:
     ```python
     # dashboard/app.py
     import streamlit as st

     st.set_page_config(
         page_title="Security Dashboard",
         page_icon="🛡️",
         layout="wide"
     )

     with st.sidebar:
         st.title("🛡️ Security Dashboard")
         uploaded_file = st.file_uploader(
             "Upload JSON Report",
             type=["json"]
         )
     ```

**완료 기준**:
- ✅ Streamlit 앱 실행 성공 (`streamlit run src/pysec/dashboard/app.py`)
- ✅ 파일 업로더 UI 표시
- ✅ 테스트 통과 (pytest)

---

#### Phase 1B: 보안 검증 및 데이터 로더 구현
**TAG**: TAG-REQ-DASH-005, TAG-REQ-DASH-006

**작업 내역**:
1. **파일 업로드 검증 (TDD)**
   - **Test First**:
     ```python
     # tests/test_security.py
     def test_validate_upload_success():
         """유효한 JSON 파일 업로드 성공"""
         valid_file = create_mock_json_file(VALID_SAST_REPORT)
         data = validate_upload(valid_file)
         assert data['scan_id'] == 'scan-001'

     def test_validate_upload_size_limit():
         """10MB 초과 파일 업로드 실패"""
         large_file = create_mock_json_file(size=11*1024*1024)
         with pytest.raises(ValueError, match="10MB 이하"):
             validate_upload(large_file)

     def test_validate_upload_invalid_extension():
         """JSON 외 확장자 업로드 실패"""
         invalid_file = create_mock_file("report.txt")
         with pytest.raises(ValueError, match="JSON 파일만"):
             validate_upload(invalid_file)

     def test_validate_upload_schema_mismatch():
         """스키마 불일치 파일 업로드 실패"""
         invalid_json = create_mock_json_file({"invalid": "data"})
         with pytest.raises(ValueError, match="형식이 올바르지 않습니다"):
             validate_upload(invalid_json)
     ```

   - **Implementation**:
     ```python
     # dashboard/security.py
     import json
     from pydantic import ValidationError
     from scanner.models import ScanReport

     MAX_FILE_SIZE = 10 * 1024 * 1024
     ALLOWED_EXTENSIONS = [".json"]

     def validate_upload(file) -> dict:
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

         # 4. 스키마 검증
         try:
             ScanReport(**data)
         except ValidationError as e:
             raise ValueError(f"스캔 리포트 형식이 올바르지 않습니다: {e}")

         return data
     ```

2. **민감 정보 마스킹 (TDD)**
   - **Test First**:
     ```python
     # tests/test_security.py
     def test_mask_user_paths():
         """파일 경로 사용자명 마스킹"""
         text = "/home/alice/project/app.py"
         masked = mask_sensitive_data(text)
         assert masked == "/home/***/project/app.py"

     def test_mask_api_keys():
         """API 키 패턴 마스킹"""
         text = "api_key = 'abcdef123456789'"
         masked = mask_sensitive_data(text)
         assert "***REDACTED***" in masked
     ```

   - **Implementation**:
     ```python
     # dashboard/security.py
     import re

     def mask_sensitive_data(text: str) -> str:
         # 파일 경로 사용자명
         text = re.sub(r'/home/[^/]+/', '/home/***/', text)
         text = re.sub(r'C:\\Users\\[^\\]+\\', 'C:\\Users\\***\\', text)

         # API 키
         text = re.sub(
             r'(api[_-]?key|token|secret)["\']?\s*[:=]\s*["\']?[\w-]{20,}',
             r'\1=***REDACTED***',
             text,
             flags=re.IGNORECASE
         )

         # 비밀번호
         text = re.sub(
             r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']?[^\s"\']+',
             r'\1=***REDACTED***',
             text,
             flags=re.IGNORECASE
         )

         return text
     ```

**완료 기준**:
- ✅ 파일 검증 테스트 통과 (크기/확장자/스키마)
- ✅ 민감 정보 마스킹 테스트 통과
- ✅ 테스트 커버리지 85% 이상

---

#### Phase 1C: 심각도 분포 차트 구현 (Plotly)
**TAG**: TAG-REQ-DASH-003

**작업 내역**:
1. **차트 생성 함수 (TDD)**
   - **Test First**:
     ```python
     # tests/test_charts.py
     import pandas as pd

     def test_create_severity_pie_chart():
         """심각도 Pie 차트 생성 검증"""
         df = pd.DataFrame({
             'severity': ['HIGH', 'HIGH', 'MEDIUM', 'LOW']
         })
         fig = create_severity_pie_chart(df)
         assert fig.data[0].type == 'pie'
         assert fig.data[0].hole == 0.4  # Donut chart

     def test_severity_chart_colors():
         """색상 코드 검증"""
         df = pd.DataFrame({'severity': ['HIGH', 'MEDIUM', 'LOW']})
         fig = create_severity_pie_chart(df)
         # Plotly color map 검증
         assert '#FF4B4B' in str(fig)  # RED for HIGH
     ```

   - **Implementation**:
     ```python
     # dashboard/components/charts.py
     import plotly.express as px

     def create_severity_pie_chart(df):
         severity_counts = df['severity'].value_counts()

         colors = {
             'HIGH': '#FF4B4B',
             'MEDIUM': '#FFA500',
             'LOW': '#4B9FFF',
             'INFO': '#808080'
         }

         fig = px.pie(
             values=severity_counts.values,
             names=severity_counts.index,
             title='Severity Distribution',
             color=severity_counts.index,
             color_discrete_map=colors,
             hole=0.4
         )

         fig.update_traces(
             textposition='inside',
             textinfo='percent+label',
             hovertemplate='<b>%{label}</b><br>Count: %{value}'
         )

         return fig
     ```

2. **Overview 페이지 통합**
   ```python
   # dashboard/pages/overview.py
   import streamlit as st
   from dashboard.components.charts import create_severity_pie_chart

   def render(data, severity_filter):
       st.header("Overview Dashboard")

       # 데이터 필터링
       df = pd.DataFrame(data['issues'])
       filtered_df = df[df['severity'].isin(severity_filter)]

       # 차트 표시
       col1, col2 = st.columns([2, 1])
       with col1:
           fig = create_severity_pie_chart(filtered_df)
           st.plotly_chart(fig, use_container_width=True)

       with col2:
           st.metric("Total Issues", len(filtered_df))
           st.metric("HIGH", len(filtered_df[filtered_df['severity'] == 'HIGH']))
   ```

**완료 기준**:
- ✅ Plotly Pie 차트 생성 테스트 통과
- ✅ 대시보드에서 차트 렌더링 성공
- ✅ 호버 인터랙션 동작 확인

---

#### Phase 1D: 취약점 테이블 및 필터링
**TAG**: TAG-REQ-DASH-004, TAG-REQ-DASH-008

**작업 내역**:
1. **데이터 테이블 구현 (TDD)**
   - **Test First**:
     ```python
     # tests/test_tables.py
     def test_render_issues_table():
         """취약점 테이블 렌더링 검증"""
         df = create_mock_issues_df()
         table_html = render_issues_table(df)
         assert 'severity' in table_html
         assert 'description' in table_html

     def test_filter_by_severity():
         """심각도 필터링 검증"""
         df = create_mock_issues_df()
         filtered = filter_issues(df, severity=['HIGH'])
         assert all(filtered['severity'] == 'HIGH')
     ```

   - **Implementation**:
     ```python
     # dashboard/components/tables.py
     import streamlit as st
     import pandas as pd

     def render_issues_table(df):
         """취약점 테이블 렌더링 (페이지네이션 포함)"""
         st.subheader("Detailed Issues")

         # 필터링된 데이터
         total_rows = len(df)

         # 페이지네이션 (100개씩)
         if total_rows > 100:
             st.info(f"Showing first 100 of {total_rows} issues")
             df = df.head(100)

         # 테이블 표시
         st.dataframe(
             df[['severity', 'type', 'file', 'line', 'description', 'owasp_category']],
             use_container_width=True
         )
     ```

2. **필터 UI 구현**
   ```python
   # dashboard/components/filters.py
   import streamlit as st

   def render_severity_filter(default=None):
       """심각도 필터 UI"""
       return st.multiselect(
           "Severity Filter",
           ["HIGH", "MEDIUM", "LOW", "INFO"],
           default=default or ["HIGH", "MEDIUM", "LOW"]
       )

   def render_type_filter(df):
       """유형 필터 UI (동적)"""
       unique_types = df['type'].unique()
       return st.multiselect(
           "Issue Type Filter",
           unique_types,
           default=unique_types
       )
   ```

**완료 기준**:
- ✅ 테이블 렌더링 테스트 통과
- ✅ 필터링 기능 동작 확인
- ✅ 페이지네이션 동작 확인 (1000+ 이슈 테스트)

---

### 🎯 Secondary Goal (부가 기능 - 2주차)

**목표**: OWASP 매핑, 민감 정보 마스킹, 고급 필터링

#### Phase 2A: OWASP Top 10 Bar 차트 (Altair)
**TAG**: TAG-REQ-DASH-014

**작업 내역**:
1. **Altair 차트 생성 (TDD)**
   - **Test First**:
     ```python
     # tests/test_charts.py
     def test_create_owasp_bar_chart():
         """OWASP Bar 차트 생성 검증"""
         df = pd.DataFrame({
             'owasp_category': ['A01:2021', 'A03:2021', 'A01:2021']
         })
         chart = create_owasp_bar_chart(df)
         assert chart.mark == 'bar'
     ```

   - **Implementation**:
     ```python
     # dashboard/components/charts.py
     import altair as alt

     def create_owasp_bar_chart(df):
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

**완료 기준**:
- ✅ Altair 차트 생성 테스트 통과
- ✅ DAST 리포트에서 OWASP 차트 렌더링 확인

---

#### Phase 2B: 민감 정보 마스킹 UI 통합
**TAG**: TAG-REQ-DASH-006

**작업 내역**:
1. **마스킹 토글 UI**
   ```python
   # dashboard/app.py (사이드바 추가)
   with st.sidebar:
       mask_enabled = st.checkbox("Mask Sensitive Data", value=True)

   # 데이터 로더에 전달
   if mask_enabled:
       data = mask_all_fields(data)
   ```

2. **통합 테스트**
   ```python
   # tests/test_integration.py
   def test_mask_sensitive_in_dashboard():
       """대시보드에서 민감 정보 마스킹 검증"""
       data = load_mock_report_with_secrets()
       masked_data = mask_all_fields(data)
       assert "***" in masked_data['issues'][0]['file']
   ```

**완료 기준**:
- ✅ 마스킹 토글 UI 동작 확인
- ✅ 파일 경로/API 키 마스킹 적용 확인

---

### 🎯 Final Goal (선택 기능 - 3주차)

**목표**: 과거 스캔 비교, 자동 새로고침, 다크 모드

#### Phase 3A: 트렌드 분석 (과거 스캔 비교)
**TAG**: TAG-REQ-DASH-015

**작업 내역**:
1. **여러 파일 업로드 지원**
   ```python
   # dashboard/app.py
   uploaded_files = st.file_uploader(
       "Upload Multiple JSON Reports",
       type=["json"],
       accept_multiple_files=True
   )
   ```

2. **트렌드 Line 차트 (Plotly)**
   ```python
   # dashboard/components/charts.py
   def create_trend_chart(reports_list):
       """시간별 심각도 추세 차트"""
       trend_data = []
       for report in reports_list:
           timestamp = report['timestamp']
           summary = report['summary']
           trend_data.append({
               'timestamp': timestamp,
               'HIGH': summary['high'],
               'MEDIUM': summary['medium'],
               'LOW': summary['low']
           })

       df = pd.DataFrame(trend_data)

       fig = px.line(
           df,
           x='timestamp',
           y=['HIGH', 'MEDIUM', 'LOW'],
           title='Vulnerability Trend Over Time'
       )

       return fig
   ```

**완료 기준**:
- ✅ 여러 파일 업로드 지원
- ✅ 트렌드 차트 렌더링 성공

---

#### Phase 3B: 자동 새로고침 (실시간 모니터링)
**TAG**: TAG-REQ-DASH-013

**작업 내역**:
1. **streamlit-autorefresh 통합**
   ```python
   # dashboard/app.py
   from streamlit_autorefresh import st_autorefresh

   # 사이드바에 토글
   with st.sidebar:
       enable_autorefresh = st.checkbox("Enable Auto-Refresh", value=False)

   if enable_autorefresh:
       # 30초마다 새로고침
       st_autorefresh(interval=30000, key="autorefresh")
   ```

**완료 기준**:
- ✅ 자동 새로고침 동작 확인
- ✅ 30초 간격 테스트

---

#### Phase 3C: 다크 모드 지원
**TAG**: TAG-REQ-DASH-016

**작업 내역**:
1. **테마 설정 추가**
   ```toml
   # .streamlit/config.toml
   [theme]
   base = "dark"
   primaryColor = "#FF4B4B"
   backgroundColor = "#0E1117"
   secondaryBackgroundColor = "#262730"
   textColor = "#FAFAFA"
   ```

2. **테마 토글 UI**
   ```python
   # dashboard/app.py
   with st.sidebar:
       theme = st.radio("Theme", ["Light", "Dark"])
       # 동적 테마 변경은 Streamlit 재시작 필요
       st.info("테마 변경 후 앱을 재시작하세요")
   ```

**완료 기준**:
- ✅ 다크 모드 설정 적용
- ✅ 차트 색상 다크 모드 호환 확인

---

## 4. 위험 관리 (Risk Management)

### 4.1 주요 위험 요소 및 대응

| 위험 | 발생 확률 | 영향도 | 대응 방안 |
|------|----------|--------|----------|
| **대용량 JSON 처리 지연** | Medium | High | - st.cache_data 캐싱<br>- 페이지네이션 (100개씩)<br>- 집계 데이터만 차트화 |
| **Streamlit 성능 이슈** | Medium | Medium | - 불필요한 재렌더링 방지<br>- 세션 상태 최적화<br>- 차트 렌더링 최소화 |
| **민감 정보 노출 위험** | Low | Critical | - 정규식 기반 자동 마스킹<br>- 로컬 호스트 전용 배포<br>- 테스트 케이스 강화 |
| **브라우저 호환성 문제** | Low | Low | - 모던 브라우저만 지원 공지<br>- Chrome/Edge 권장 |

### 4.2 품질 게이트

**Phase별 품질 체크**:
- **Phase 1**: 테스트 커버리지 85% 이상, Mypy 타입 체크 통과
- **Phase 2**: OWASP 차트 렌더링 성공, 민감 정보 마스킹 검증
- **Phase 3**: 트렌드 차트 정확도 검증, 자동 새로고침 안정성 테스트

---

## 5. 테스트 전략 (Testing Strategy)

### 5.1 단위 테스트 (Unit Tests)

**커버리지 목표**: 85% 이상

```python
# tests/test_security.py
- test_validate_upload_success()
- test_validate_upload_size_limit()
- test_validate_upload_invalid_extension()
- test_validate_upload_schema_mismatch()
- test_mask_user_paths()
- test_mask_api_keys()
- test_mask_passwords()

# tests/test_charts.py
- test_create_severity_pie_chart()
- test_severity_chart_colors()
- test_create_owasp_bar_chart()
- test_create_trend_chart()

# tests/test_tables.py
- test_render_issues_table()
- test_filter_by_severity()
- test_pagination_large_dataset()
```

### 5.2 통합 테스트 (Integration Tests)

```python
# tests/test_integration.py
def test_upload_sast_report_end_to_end():
    """SAST 리포트 업로드 → 시각화 전체 플로우"""
    # 1. 파일 업로드
    # 2. 검증 통과
    # 3. 차트 렌더링
    # 4. 테이블 표시

def test_upload_dast_report_end_to_end():
    """DAST 리포트 업로드 → OWASP 차트 렌더링"""
    # 1. DAST 파일 업로드
    # 2. OWASP Top 10 매핑
    # 3. Bar 차트 렌더링
```

### 5.3 UI 테스트 (Streamlit Testing)

```python
# tests/test_ui.py (streamlit-testing 사용)
from streamlit.testing.v1 import AppTest

def test_sidebar_file_uploader():
    """사이드바에 파일 업로더 표시 확인"""
    at = AppTest.from_file("dashboard/app.py")
    at.run()
    assert at.sidebar.file_uploader[0].label == "Upload JSON Report"

def test_filter_interaction():
    """필터 변경 시 차트 업데이트 확인"""
    at = AppTest.from_file("dashboard/app.py")
    at.run()
    # 필터 변경
    at.sidebar.multiselect[0].set_value(["HIGH"])
    at.run()
    # 차트 업데이트 확인
    assert at.plotly_chart[0] is not None
```

---

## 6. 배포 전략 (Deployment Strategy)

### 6.1 로컬 배포 (기본값)

```bash
# 로컬 호스트 전용
streamlit run src/pysec/dashboard/app.py --server.address localhost
```

### 6.2 팀 공유 (Docker)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .
RUN pip install -e ".[dashboard]"

EXPOSE 8501

CMD ["streamlit", "run", "src/pysec/dashboard/app.py", "--server.address", "0.0.0.0"]
```

```bash
# Docker Compose
docker-compose up -d
# 팀 내부망에서 http://<server-ip>:8501 접근
```

### 6.3 클라우드 배포 (Streamlit Cloud)

```yaml
# .streamlit/secrets.toml (Streamlit Cloud)
[server]
enableXsrfProtection = true

[general]
environment = "production"
```

**보안 고려사항**:
- 로컬 전용: 기본 배포 방식 (권장)
- 팀 공유: Docker + VPN (내부망 한정)
- 클라우드: Streamlit Cloud + Secrets 관리

---

## 7. 문서화 (Documentation)

### 7.1 사용자 가이드

**README.md 추가 내용**:
```markdown
## 대시보드 실행

### 설치
\`\`\`bash
uv pip install -e ".[dashboard]"
\`\`\`

### 실행
\`\`\`bash
streamlit run src/pysec/dashboard/app.py
\`\`\`

### 사용법
1. 브라우저에서 http://localhost:8501 접근
2. 사이드바에서 JSON 리포트 업로드 (SPEC-001/002 출력)
3. 필터를 조정하여 원하는 심각도 선택
4. Overview/SAST/DAST 페이지 전환
```

### 7.2 API 문서 (Docstring)

```python
# dashboard/components/charts.py
def create_severity_pie_chart(df: pd.DataFrame) -> go.Figure:
    """심각도 분포 Pie 차트 생성

    Args:
        df: SecurityIssue 또는 DastAlert 데이터프레임
            - 필수 컬럼: 'severity' (HIGH/MEDIUM/LOW/INFO)

    Returns:
        Plotly Figure 객체 (Donut Pie Chart)

    Example:
        >>> df = pd.DataFrame({'severity': ['HIGH', 'MEDIUM', 'LOW']})
        >>> fig = create_severity_pie_chart(df)
        >>> st.plotly_chart(fig)
    """
```

---

## 8. 성공 지표 (Success Metrics)

### 8.1 기술 지표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| **테스트 커버리지** | ≥85% | pytest-cov |
| **타입 체크** | 100% | mypy |
| **린팅 오류** | 0건 | ruff |
| **렌더링 시간** | <1초 (100 이슈) | Streamlit profiler |

### 8.2 사용자 경험 지표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| **파일 업로드 성공률** | ≥95% | 수동 테스트 |
| **차트 인터랙션 응답** | <500ms | 브라우저 DevTools |
| **필터 적용 시간** | <200ms | Streamlit timer |

---

## 9. 다음 단계 (Next Steps)

### 9.1 즉시 실행 가능

```bash
# 1. 프로젝트 초기화
mkdir -p src/pysec/dashboard/{pages,components,config}

# 2. 의존성 설치
uv pip install -e ".[dashboard]"

# 3. TDD 시작
pytest tests/test_security.py --cov

# 4. Streamlit 앱 실행
streamlit run src/pysec/dashboard/app.py
```

### 9.2 향후 SPEC 연계

- **SPEC-SECURITY-005**: MCP 통합 (실시간 스캔 트리거)
  - 대시보드에서 스캔 시작 버튼 → MCP 서버 호출 → 자동 업데이트

- **SPEC-SECURITY-006**: 다중 사용자 인증
  - OAuth2 + JWT 기반 인증 레이어 추가

---

**문서 버전**: 0.1.0
**최종 수정**: 2025-11-17
**다음 액션**: `/alfred:2-run SPEC-SECURITY-004` (TDD 구현 시작)
