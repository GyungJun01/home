"""
Simple Streamlit Dashboard for Security Scan Visualization
TAG-REQ-DASH-001: File upload interface
"""

import streamlit as st


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
        st.success(f"파일 업로드 완료: {uploaded_file.name}")
        st.info("대시보드 구현 예정...")
    else:
        st.info("시작하려면 스캔 보고서를 업로드하세요.")


if __name__ == "__main__":
    main()
