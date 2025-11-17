# SPEC-SECURITY-004 인수 기준 (Acceptance Criteria)

## TAG BLOCK

```yaml
spec_id: SPEC-SECURITY-004
title: 보안 스캔 결과 시각화 웹 대시보드 인수 기준
domain: SECURITY
status: draft
version: 0.1.0
created: 2025-11-17
author: @user
```

---

## 1. 개요 (Overview)

### 1.1 목적
SPEC-SECURITY-004의 구현이 요구사항을 충족하는지 검증하기 위한 명확하고 측정 가능한 인수 기준을 정의한다.

### 1.2 인수 테스트 형식
모든 인수 기준은 **Given-When-Then (GWT)** 형식으로 작성되어, 비즈니스 요구사항과 기술 구현 간의 명확한 매핑을 제공한다.

---

## 2. Core Features (핵심 기능)

### AC-001: Streamlit 웹 대시보드 실행
**TAG**: TAG-REQ-DASH-001

**Given**: Streamlit이 로컬 환경에 설치되어 있고
**When**: `streamlit run src/pysec/dashboard/app.py` 명령어를 실행하면
**Then**:
- [ ] 브라우저가 자동으로 http://localhost:8501 로 열림
- [ ] 대시보드 타이틀 "🛡️ Security Dashboard" 표시
- [ ] 사이드바에 "Upload JSON Report" 파일 업로더 표시
- [ ] 에러 없이 앱이 정상 실행됨

**검증 방법**:
```bash
streamlit run src/pysec/dashboard/app.py
# 브라우저 확인: http://localhost:8501
# 타이틀 및 파일 업로더 UI 존재 확인
```

---

### AC-002: SAST JSON 리포트 업로드 및 파싱
**TAG**: TAG-REQ-DASH-002

**Given**: SPEC-001에서 생성된 유효한 SAST JSON 리포트 (예: `sast_report.json`)가 있고
**When**: 사용자가 파일 업로더를 통해 JSON 파일을 업로드하면
**Then**:
- [ ] "✅ 파일 검증 완료" 성공 메시지 표시
- [ ] JSON 데이터가 ScanReport Pydantic 모델로 파싱됨
- [ ] 대시보드에 차트 및 테이블이 자동 렌더링됨
- [ ] 에러 메시지 없음

**검증 방법**:
```python
# tests/test_integration.py
def test_upload_sast_report():
    valid_file = create_mock_sast_json()
    data = validate_upload(valid_file)
    assert data['scan_id'] == 'scan-001'
    assert len(data['issues']) > 0
```

**Given**: 잘못된 형식의 JSON 파일 (예: `invalid.json`)을 업로드하면
**When**: 파일 검증 단계에서
**Then**:
- [ ] "❌ 유효하지 않은 JSON 형식입니다" 에러 메시지 표시
- [ ] 재업로드 안내 표시
- [ ] 대시보드 렌더링 중단

**검증 방법**:
```python
def test_upload_invalid_json():
    invalid_file = create_invalid_json()
    with pytest.raises(ValueError, match="유효하지 않은 JSON"):
        validate_upload(invalid_file)
```

---

### AC-003: 심각도 분포 Pie 차트 표시
**TAG**: TAG-REQ-DASH-003

**Given**: 유효한 SAST 리포트가 업로드되어 있고 (HIGH: 2, MEDIUM: 3, LOW: 1)
**When**: Overview 페이지를 열면
**Then**:
- [ ] Plotly Donut Pie 차트가 렌더링됨
- [ ] 차트 타이틀 "Severity Distribution" 표시
- [ ] HIGH (🔴 RED), MEDIUM (🟡 ORANGE), LOW (🔵 BLUE) 색상 구분
- [ ] 각 섹션에 개수 및 비율 표시 (예: "HIGH: 2 (33%)")
- [ ] 호버 시 "Count: 2, Percent: 33%" 툴팁 표시

**검증 방법**:
```python
# tests/test_charts.py
def test_severity_pie_chart_rendering():
    df = pd.DataFrame({'severity': ['HIGH', 'HIGH', 'MEDIUM', 'MEDIUM', 'MEDIUM', 'LOW']})
    fig = create_severity_pie_chart(df)

    assert fig.data[0].type == 'pie'
    assert fig.data[0].hole == 0.4  # Donut chart
    assert fig.layout.title.text == 'Severity Distribution'

    # 색상 검증
    color_map = fig.data[0].marker.colors
    assert '#FF4B4B' in str(color_map)  # RED for HIGH
```

**Given**: 필터에서 "HIGH"만 선택하면
**When**: 차트가 업데이트될 때
**Then**:
- [ ] Pie 차트에 HIGH만 표시됨
- [ ] 비율이 100%로 표시됨

---

### AC-004: 취약점 상세 테이블 표시 및 필터링
**TAG**: TAG-REQ-DASH-004, TAG-REQ-DASH-008

**Given**: SAST 리포트에 10개의 이슈가 있고
**When**: Overview 페이지에서 테이블을 확인하면
**Then**:
- [ ] 테이블 제목 "Detailed Issues" 표시
- [ ] 컬럼: Severity, Type, File, Line, Description, OWASP Category
- [ ] 10개 행 모두 표시됨
- [ ] 인터랙티브 정렬 기능 동작 (컬럼 헤더 클릭)

**검증 방법**:
```python
# tests/test_tables.py
def test_render_issues_table():
    df = create_mock_issues_df(count=10)
    rendered_table = render_issues_table(df)

    assert len(rendered_table) == 10
    assert 'severity' in rendered_table.columns
    assert 'description' in rendered_table.columns
```

**Given**: 사이드바에서 심각도 필터를 "HIGH"로 설정하면
**When**: 테이블이 업데이트될 때
**Then**:
- [ ] HIGH 심각도 이슈만 테이블에 표시됨
- [ ] 필터링된 항목 개수 표시 (예: "Showing 2 of 10 issues")

**검증 방법**:
```python
def test_filter_by_severity():
    df = create_mock_issues_df(count=10)
    filtered = df[df['severity'] == 'HIGH']

    assert len(filtered) == 2
    assert all(filtered['severity'] == 'HIGH')
```

---

### AC-005: 파일 업로드 보안 검증 (3단계)
**TAG**: TAG-REQ-DASH-005

#### 5-1. 파일 크기 제한

**Given**: 15MB 크기의 JSON 파일을 업로드하면
**When**: 파일 검증 단계에서
**Then**:
- [ ] "❌ 파일 크기는 10MB 이하여야 합니다" 에러 메시지 표시
- [ ] 업로드 중단

**검증 방법**:
```python
def test_file_size_limit():
    large_file = create_mock_file(size=15*1024*1024)
    with pytest.raises(ValueError, match="10MB 이하"):
        validate_upload(large_file)
```

#### 5-2. 확장자 검증

**Given**: `.txt` 확장자 파일을 업로드하면
**When**: 파일 검증 단계에서
**Then**:
- [ ] "❌ JSON 파일만 업로드 가능합니다" 에러 메시지 표시
- [ ] 업로드 중단

**검증 방법**:
```python
def test_invalid_extension():
    txt_file = create_mock_file(name="report.txt")
    with pytest.raises(ValueError, match="JSON 파일만"):
        validate_upload(txt_file)
```

#### 5-3. 스키마 검증

**Given**: ScanReport 스키마와 일치하지 않는 JSON 파일을 업로드하면
**When**: Pydantic 검증 단계에서
**Then**:
- [ ] "❌ 스캔 리포트 형식이 올바르지 않습니다" 에러 메시지 표시
- [ ] 필수 필드 목록 표시 (예: "scan_id, timestamp, issues")
- [ ] 업로드 중단

**검증 방법**:
```python
def test_schema_validation():
    invalid_json = {"invalid_field": "data"}
    with pytest.raises(ValueError, match="형식이 올바르지 않습니다"):
        ScanReport(**invalid_json)
```

---

### AC-006: 민감 정보 자동 마스킹
**TAG**: TAG-REQ-DASH-006

#### 6-1. 파일 경로 사용자명 마스킹

**Given**: 파일 경로가 `/home/alice/project/app.py`인 이슈가 있고
**When**: 민감 정보 마스킹이 활성화되어 있으면
**Then**:
- [ ] 테이블에 `/home/***/project/app.py`로 표시됨
- [ ] 원본 경로는 노출되지 않음

**검증 방법**:
```python
# tests/test_security.py
def test_mask_user_paths():
    text = "/home/alice/project/app.py"
    masked = mask_sensitive_data(text)

    assert masked == "/home/***/project/app.py"
    assert "alice" not in masked
```

**Given**: Windows 경로 `C:\Users\Bob\code\main.py`가 있으면
**When**: 마스킹 함수를 적용하면
**Then**:
- [ ] `C:\Users\***\code\main.py`로 변환됨

**검증 방법**:
```python
def test_mask_windows_paths():
    text = r"C:\Users\Bob\code\main.py"
    masked = mask_sensitive_data(text)

    assert masked == r"C:\Users\***\code\main.py"
    assert "Bob" not in masked
```

#### 6-2. API 키/토큰 마스킹

**Given**: 코드 스니펫에 `api_key = 'abcdef123456789'`가 포함되어 있으면
**When**: 민감 정보 마스킹을 적용하면
**Then**:
- [ ] `api_key = ***REDACTED***`로 변환됨
- [ ] 원본 API 키는 노출되지 않음

**검증 방법**:
```python
def test_mask_api_keys():
    text = "api_key = 'abcdef123456789'"
    masked = mask_sensitive_data(text)

    assert "***REDACTED***" in masked
    assert "abcdef123456789" not in masked
```

#### 6-3. 비밀번호 마스킹

**Given**: 코드에 `password = "secret123"`이 있으면
**When**: 마스킹 함수를 적용하면
**Then**:
- [ ] `password = ***REDACTED***`로 변환됨

**검증 방법**:
```python
def test_mask_passwords():
    text = 'password = "secret123"'
    masked = mask_sensitive_data(text)

    assert "***REDACTED***" in masked
    assert "secret123" not in masked
```

---

## 3. Advanced Features (부가 기능)

### AC-007: DAST JSON 리포트 업로드 및 OWASP 차트
**TAG**: TAG-REQ-DASH-014

**Given**: SPEC-002에서 생성된 DAST JSON 리포트가 있고
**When**: 파일을 업로드하고 DAST 페이지를 열면
**Then**:
- [ ] OWASP Top 10 카테고리별 Bar 차트 렌더링
- [ ] 차트 타이틀 "OWASP Top 10 Distribution" 표시
- [ ] X축: 이슈 개수, Y축: OWASP 카테고리 (A01~A10)
- [ ] 호버 시 카테고리 및 개수 표시

**검증 방법**:
```python
# tests/test_charts.py
def test_owasp_bar_chart():
    df = pd.DataFrame({
        'owasp_category': ['A01:2021', 'A03:2021', 'A01:2021', 'A07:2021']
    })
    chart = create_owasp_bar_chart(df)

    assert chart.mark == 'bar'
    assert 'A01:2021' in chart.data['category'].values
```

---

### AC-008: 대용량 데이터 페이지네이션
**TAG**: TAG-REQ-DASH-011

**Given**: 1500개의 이슈를 포함한 JSON 리포트가 업로드되었고
**When**: 테이블을 확인하면
**Then**:
- [ ] 처음 100개 이슈만 테이블에 표시됨
- [ ] "Showing first 100 of 1500 issues" 메시지 표시
- [ ] "More" 버튼 또는 페이지 번호 선택 UI 제공
- [ ] 페이지 변경 시 다음 100개 로드됨

**검증 방법**:
```python
# tests/test_tables.py
def test_pagination_large_dataset():
    df = create_mock_issues_df(count=1500)
    paginated = render_paginated_table(df, page_size=100)

    assert len(paginated) == 100
    # 페이지 2 선택
    paginated_page2 = render_paginated_table(df, page=2, page_size=100)
    assert len(paginated_page2) == 100
```

---

### AC-009: 과거 스캔 트렌드 분석 (선택)
**TAG**: TAG-REQ-DASH-015

**Given**: 3개의 스캔 리포트 (2025-11-15, 2025-11-16, 2025-11-17)가 업로드되었고
**When**: Overview 페이지에서 트렌드 차트를 확인하면
**Then**:
- [ ] Plotly Line 차트 렌더링
- [ ] X축: 날짜 (2025-11-15 ~ 2025-11-17)
- [ ] Y축: 이슈 개수
- [ ] 3개 라인: HIGH, MEDIUM, LOW
- [ ] 호버 시 날짜 및 개수 표시

**검증 방법**:
```python
# tests/test_charts.py
def test_trend_chart():
    reports = [
        {'timestamp': '2025-11-15T10:00:00Z', 'summary': {'high': 5, 'medium': 10, 'low': 3}},
        {'timestamp': '2025-11-16T10:00:00Z', 'summary': {'high': 3, 'medium': 8, 'low': 2}},
        {'timestamp': '2025-11-17T10:00:00Z', 'summary': {'high': 2, 'medium': 5, 'low': 1}}
    ]
    fig = create_trend_chart(reports)

    assert fig.data[0].type == 'scatter'  # Line chart
    assert len(fig.data) == 3  # HIGH, MEDIUM, LOW
```

---

### AC-010: 자동 새로고침 (선택)
**TAG**: TAG-REQ-DASH-013

**Given**: 사이드바에서 "Enable Auto-Refresh" 체크박스를 활성화하고
**When**: 30초가 경과하면
**Then**:
- [ ] 대시보드가 자동으로 새로고침됨
- [ ] JSON 파일이 재로드됨 (파일 경로 지정 시)
- [ ] 새로운 이슈가 자동으로 감지됨
- [ ] "Last updated: 2025-11-17 14:30:22" 타임스탬프 표시

**검증 방법**:
```python
# tests/test_autorefresh.py
def test_autorefresh_enabled():
    # 자동 새로고침 활성화
    enable_autorefresh = True
    assert st_autorefresh(interval=30000) is not None
```

---

## 4. Error Handling (에러 처리)

### AC-011: 잘못된 파일 형식 에러 처리
**TAG**: TAG-REQ-DASH-009

**Given**: 유효하지 않은 JSON 파일을 업로드하면
**When**: 파싱 단계에서 에러가 발생하면
**Then**:
- [ ] "❌ 유효하지 않은 JSON 형식입니다" 에러 메시지 표시
- [ ] "다시 업로드하기" 버튼 제공
- [ ] 샘플 JSON 형식 예제 표시
- [ ] 대시보드는 이전 상태 유지 (에러로 중단되지 않음)

**검증 방법**:
```python
def test_invalid_json_error_handling():
    invalid_json = "not a json"

    try:
        data = json.loads(invalid_json)
    except json.JSONDecodeError as e:
        error_message = f"유효하지 않은 JSON 형식입니다: {e}"
        assert "유효하지 않은 JSON" in error_message
```

---

### AC-012: 스키마 불일치 에러 처리
**TAG**: TAG-REQ-DASH-010

**Given**: ScanReport 스키마와 일치하지 않는 JSON을 업로드하면
**When**: Pydantic 검증 실패 시
**Then**:
- [ ] "❌ 스캔 리포트 형식이 올바르지 않습니다" 에러 메시지 표시
- [ ] 필수 필드 목록 표시:
  - `scan_id` (required)
  - `timestamp` (required)
  - `issues` (required, list)
- [ ] SPEC-001/002 문서 링크 제공

**검증 방법**:
```python
def test_schema_mismatch_error():
    invalid_data = {"wrong_field": "value"}

    try:
        ScanReport(**invalid_data)
    except ValidationError as e:
        assert "scan_id" in str(e)
        assert "timestamp" in str(e)
```

---

## 5. Performance & Security (성능 및 보안)

### AC-013: 차트 렌더링 성능
**TAG**: TAG-REQ-DASH-003

**Given**: 100개의 이슈를 포함한 리포트가 업로드되었고
**When**: Plotly Pie 차트를 렌더링하면
**Then**:
- [ ] 렌더링 시간 < 1초
- [ ] 브라우저 메모리 사용량 < 200MB
- [ ] 호버 인터랙션 응답 시간 < 100ms

**검증 방법**:
```bash
# Streamlit profiler 사용
streamlit run src/pysec/dashboard/app.py --profiler
# 브라우저 DevTools → Performance 탭 확인
```

---

### AC-014: 파일 업로드 보안 (OWASP 준수)
**TAG**: TAG-REQ-DASH-005

**Given**: 악성 JSON 페이로드를 업로드하려고 시도하면
**When**: 파일 검증 단계에서
**Then**:
- [ ] 파일 크기 제한으로 대용량 페이로드 차단
- [ ] JSON 파싱 중 주입 공격 방지 (json.load() 사용)
- [ ] Pydantic 스키마 검증으로 예상치 못한 필드 차단
- [ ] 에러 메시지에 민감 정보 노출 없음

**검증 방법**:
```python
def test_malicious_payload_blocked():
    malicious_json = {
        "scan_id": "<script>alert('XSS')</script>",
        "timestamp": "2025-11-17T10:00:00Z",
        "issues": []
    }

    # Pydantic 검증으로 스크립트 태그는 문자열로 처리됨
    report = ScanReport(**malicious_json)

    # Streamlit은 기본적으로 HTML 이스케이프
    assert "<script>" not in st.markdown(report.scan_id)
```

---

## 6. Usability (사용성)

### AC-015: 직관적인 필터 UI
**TAG**: TAG-REQ-DASH-008

**Given**: 사용자가 대시보드를 처음 사용할 때
**When**: 사이드바를 확인하면
**Then**:
- [ ] 필터 섹션이 명확히 구분됨
- [ ] "Severity Filter" 레이블과 함께 멀티셀렉트 UI 표시
- [ ] 기본값으로 HIGH, MEDIUM, LOW 선택됨
- [ ] 필터 변경 시 즉시 차트 업데이트 (< 200ms)

**검증 방법**:
```python
# tests/test_filters.py
def test_filter_ui_defaults():
    severity_filter = render_severity_filter()

    assert "HIGH" in severity_filter
    assert "MEDIUM" in severity_filter
    assert "LOW" in severity_filter
    assert "INFO" not in severity_filter  # 기본값 제외
```

---

### AC-016: 다크 모드 지원 (선택)
**TAG**: TAG-REQ-DASH-016

**Given**: 사용자가 다크 모드를 선택하면
**When**: Streamlit 설정에서 테마를 변경하면
**Then**:
- [ ] 배경색: #0E1117 (다크)
- [ ] 텍스트 색상: #FAFAFA (밝은 회색)
- [ ] 차트 색상: 다크 모드 호환 색상 적용
- [ ] 에러 메시지 색상: 가독성 유지

**검증 방법**:
```toml
# .streamlit/config.toml 확인
[theme]
base = "dark"
backgroundColor = "#0E1117"
textColor = "#FAFAFA"
```

---

## 7. Integration Testing (통합 테스트)

### AC-017: SAST + DAST 통합 스캔 리포트
**TAG**: TAG-REQ-DASH-002

**Given**: SAST 및 DAST 결과가 포함된 통합 리포트를 업로드하면
**When**: Overview 페이지를 확인하면
**Then**:
- [ ] SAST 이슈와 DAST 이슈가 모두 테이블에 표시됨
- [ ] 심각도 차트에 통합 통계 표시
- [ ] OWASP 차트에 DAST 데이터만 표시 (SAST는 제외)

**검증 방법**:
```python
# tests/test_integration.py
def test_unified_report_rendering():
    unified_report = create_mock_unified_report(
        sast_issues=5,
        dast_alerts=3
    )

    data = validate_upload(unified_report)
    assert len(data['all_issues']) == 8  # 5 + 3
```

---

## 8. Definition of Done (완료 기준)

### 8.1 기능 완성도

- [ ] 모든 Primary Goal 인수 기준 통과 (AC-001 ~ AC-006)
- [ ] 모든 Secondary Goal 인수 기준 통과 (AC-007 ~ AC-008)
- [ ] 선택 기능 50% 이상 구현 (AC-009 ~ AC-010)

### 8.2 품질 기준

- [ ] 단위 테스트 커버리지 ≥ 85%
- [ ] 통합 테스트 통과율 100%
- [ ] Mypy 타입 체크 100% 통과
- [ ] Ruff 린팅 오류 0건
- [ ] 보안 검증 테스트 100% 통과

### 8.3 사용자 경험

- [ ] 파일 업로드 성공률 ≥ 95% (수동 테스트)
- [ ] 차트 렌더링 시간 < 1초 (100 이슈 기준)
- [ ] 필터 응답 시간 < 200ms
- [ ] 에러 메시지 명확성 검증 (5명 이상 사용자 테스트)

### 8.4 문서화

- [ ] README.md에 대시보드 사용법 추가
- [ ] 모든 함수에 Docstring 작성 (Google 스타일)
- [ ] 샘플 JSON 파일 제공 (SAST, DAST, 통합)
- [ ] 트러블슈팅 가이드 작성

### 8.5 배포 준비

- [ ] 로컬 배포 성공 (localhost:8501)
- [ ] Docker 이미지 빌드 성공 (선택)
- [ ] Streamlit Cloud 배포 가이드 작성 (선택)
- [ ] 보안 설정 검증 (.streamlit/config.toml)

---

## 9. Acceptance Test Execution Plan (인수 테스트 실행 계획)

### 9.1 테스트 환경

| 항목 | 값 |
|------|-----|
| **Python 버전** | 3.11.5 |
| **Streamlit 버전** | 1.41.0 |
| **브라우저** | Chrome 120+ |
| **OS** | Ubuntu 22.04 / Windows 11 / macOS 14+ |

### 9.2 테스트 데이터

**준비 파일**:
1. `sast_report_small.json` (10 이슈)
2. `sast_report_large.json` (1500 이슈)
3. `dast_report.json` (20 alerts)
4. `unified_report.json` (SAST + DAST)
5. `invalid_format.json` (스키마 불일치)
6. `malformed.json` (잘못된 JSON)

### 9.3 실행 순서

**Phase 1: 기본 기능 검증** (AC-001 ~ AC-006)
1. Streamlit 앱 실행
2. SAST 리포트 업로드
3. 차트 및 테이블 렌더링 확인
4. 보안 검증 테스트

**Phase 2: 고급 기능 검증** (AC-007 ~ AC-010)
1. DAST 리포트 업로드
2. OWASP 차트 확인
3. 대용량 데이터 페이지네이션
4. 트렌드 차트 및 자동 새로고침

**Phase 3: 에러 처리 검증** (AC-011 ~ AC-012)
1. 잘못된 파일 업로드
2. 에러 메시지 명확성 확인

**Phase 4: 성능 및 보안 검증** (AC-013 ~ AC-014)
1. 성능 벤치마크
2. 보안 테스트 (OWASP ZAP)

---

## 10. Sign-off Checklist (최종 승인 체크리스트)

### 10.1 기술 검토

- [ ] **Tech Lead**: 코드 리뷰 완료 및 승인
- [ ] **QA**: 모든 인수 기준 테스트 통과 확인
- [ ] **Security**: 보안 검증 테스트 통과 확인

### 10.2 문서 검토

- [ ] **Tech Writer**: 사용자 가이드 검토 완료
- [ ] **Product Owner**: SPEC-004 요구사항 충족 확인

### 10.3 배포 승인

- [ ] **DevOps**: 로컬 배포 환경 검증 완료
- [ ] **Product Owner**: 최종 배포 승인

---

**문서 버전**: 0.1.0
**최종 수정**: 2025-11-17
**다음 액션**: `/alfred:2-run SPEC-SECURITY-004` (TDD 구현 시작)
