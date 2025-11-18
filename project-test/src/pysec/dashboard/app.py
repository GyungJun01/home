"""
Streamlit Dashboard for Security Scan Visualization
TAG-REQ-DASH-001: Complete dashboard implementation
"""

import streamlit as st

from pysec.dashboard.components.charts import (
    create_confidence_pie_chart,
    create_owasp_bar_chart,
    create_severity_pie_chart,
)
from pysec.dashboard.components.filters import (
    filter_empty_message,
    get_severity_options,
)
from pysec.dashboard.components.tables import (
    filter_issues_by_severity,
    get_pagination_info,
    paginate_dataframe,
)
from pysec.dashboard.data_loader import convert_to_dataframe, load_scan_report
from pysec.dashboard.security import validate_upload


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(
        page_title="PySec 보안 스캐너",
        page_icon="🔒",
        layout="wide",
    )

    st.title("🔒 PySec 보안 스캐너 대시보드")
    st.markdown("JSON 스캔 보고서를 업로드하여 보안 이슈를 시각화합니다.")

    # File upload widget
    uploaded_file = st.file_uploader(
        "스캔 보고서 업로드 (JSON)",
        type=["json"],
        help="'pysec scan' 명령어로 생성된 JSON 파일을 업로드하세요",
    )

    if uploaded_file is not None:
        try:
            # Validate and parse uploaded file
            data = validate_upload(uploaded_file)
            st.success(f"✅ 파일 업로드 완료: {uploaded_file.name}")

            # Load scan report
            report = load_scan_report(data)
            df = convert_to_dataframe(report)

            # Display summary metrics
            st.header("📊 요약")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("전체 이슈", report.summary.total_issues)
            with col2:
                st.metric("HIGH", report.summary.high, delta=None, delta_color="inverse")
            with col3:
                st.metric("MEDIUM", report.summary.medium)
            with col4:
                st.metric("LOW", report.summary.low)

            # Sidebar filters
            st.sidebar.header("🔍 필터")
            severity_options = get_severity_options()
            selected_severities = st.sidebar.multiselect(
                "심각도 선택",
                severity_options,
                default=["HIGH", "MEDIUM", "LOW"],
            )

            # Apply filters
            if selected_severities:
                filtered_df = filter_issues_by_severity(df, selected_severities)
            else:
                filtered_df = df

            if len(filtered_df) == 0:
                st.warning(filter_empty_message("severity"))
                return

            # Charts section
            st.header("📈 차트")
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                severity_chart = create_severity_pie_chart(filtered_df)
                st.plotly_chart(severity_chart, use_container_width=True)

            with chart_col2:
                if "confidence" in filtered_df.columns:
                    confidence_chart = create_confidence_pie_chart(filtered_df)
                    st.plotly_chart(confidence_chart, use_container_width=True)

            # OWASP chart
            if "owasp_category" in filtered_df.columns:
                st.subheader("OWASP Top 10 분포")
                owasp_chart = create_owasp_bar_chart(filtered_df)
                st.altair_chart(owasp_chart, use_container_width=True)

            # Issues table with pagination
            st.header("📋 이슈 상세")

            # Pagination controls
            page_size = st.selectbox("페이지당 항목", [10, 25, 50, 100], index=1)
            total_items = len(filtered_df)
            total_pages = max(1, (total_items + page_size - 1) // page_size)

            page = st.number_input(
                "페이지", min_value=1, max_value=total_pages, value=1, step=1
            )

            # Get pagination info
            pag_info = get_pagination_info(total_items, page, page_size)
            st.caption(
                f"전체 {pag_info['total_items']}개 중 {pag_info['start_item']}-{pag_info['end_item']} 표시"
            )

            # Display paginated table
            paginated_df = paginate_dataframe(filtered_df, page, page_size)

            # Select columns to display
            display_columns = ["severity", "type", "category", "file", "line", "description"]
            available_columns = [col for col in display_columns if col in paginated_df.columns]

            st.dataframe(
                paginated_df[available_columns],
                use_container_width=True,
                hide_index=True,
            )

        except ValueError as e:
            st.error(f"❌ 오류: {str(e)}")
            st.info("올바른 JSON 형식의 스캔 보고서를 업로드하세요.")
    else:
        st.info("👆 시작하려면 스캔 보고서를 업로드하세요.")


if __name__ == "__main__":
    main()
