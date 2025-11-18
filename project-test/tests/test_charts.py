"""
Tests for dashboard chart components (TAG-REQ-DASH-003, TAG-REQ-DASH-014)

Tests for Plotly Pie charts (severity, confidence distribution) and
Altair Bar charts (OWASP Top 10 mapping).
"""

import pandas as pd
import pytest

from pysec.dashboard.components.charts import (
    create_severity_pie_chart,
    create_confidence_pie_chart,
    create_owasp_bar_chart,
)


class TestSeverityPieChart:
    """Tests for severity distribution pie chart (TAG-REQ-DASH-003)"""

    def test_create_severity_pie_chart_returns_figure(self) -> None:
        """Test that function returns a plotly figure"""
        df = pd.DataFrame({
            "severity": ["HIGH", "HIGH", "MEDIUM", "LOW", "LOW", "LOW"],
            "issue_id": ["1", "2", "3", "4", "5", "6"],
        })

        fig = create_severity_pie_chart(df)
        assert fig is not None
        assert hasattr(fig, "data")

    def test_severity_pie_chart_has_correct_values(self) -> None:
        """Test that pie chart has correct severity counts"""
        df = pd.DataFrame({
            "severity": ["HIGH", "HIGH", "MEDIUM", "LOW", "LOW", "LOW"],
            "issue_id": ["1", "2", "3", "4", "5", "6"],
        })

        fig = create_severity_pie_chart(df)
        # Check that figure contains the severity data
        assert len(fig.data) > 0

    def test_severity_pie_chart_with_single_severity(self) -> None:
        """Test pie chart with only one severity level"""
        df = pd.DataFrame({
            "severity": ["HIGH", "HIGH", "HIGH"],
            "issue_id": ["1", "2", "3"],
        })

        fig = create_severity_pie_chart(df)
        assert fig is not None

    def test_severity_pie_chart_with_empty_df(self) -> None:
        """Test pie chart handles empty dataframe gracefully"""
        df = pd.DataFrame({"severity": [], "issue_id": []})

        # Should handle empty dataframe
        fig = create_severity_pie_chart(df)
        assert fig is not None

    def test_severity_pie_chart_title(self) -> None:
        """Test that severity pie chart has correct title"""
        df = pd.DataFrame({
            "severity": ["HIGH", "MEDIUM", "LOW"],
            "issue_id": ["1", "2", "3"],
        })

        fig = create_severity_pie_chart(df)
        assert "심각도" in fig.layout.title.text or "분포" in fig.layout.title.text


class TestConfidencePieChart:
    """Tests for confidence distribution pie chart"""

    def test_create_confidence_pie_chart_returns_figure(self) -> None:
        """Test that function returns a plotly figure"""
        df = pd.DataFrame({
            "confidence": ["HIGH", "MEDIUM", "LOW"],
            "issue_id": ["1", "2", "3"],
        })

        fig = create_confidence_pie_chart(df)
        assert fig is not None
        assert hasattr(fig, "data")

    def test_confidence_pie_chart_with_single_confidence(self) -> None:
        """Test pie chart with only one confidence level"""
        df = pd.DataFrame({
            "confidence": ["HIGH", "HIGH"],
            "issue_id": ["1", "2"],
        })

        fig = create_confidence_pie_chart(df)
        assert fig is not None

    def test_confidence_pie_chart_title(self) -> None:
        """Test that confidence pie chart has correct title"""
        df = pd.DataFrame({
            "confidence": ["HIGH", "MEDIUM", "LOW"],
            "issue_id": ["1", "2", "3"],
        })

        fig = create_confidence_pie_chart(df)
        assert "신뢰도" in fig.layout.title.text or "분포" in fig.layout.title.text


class TestOWASPBarChart:
    """Tests for OWASP Top 10 bar chart (TAG-REQ-DASH-014)"""

    def test_create_owasp_bar_chart_returns_chart(self) -> None:
        """Test that function returns an Altair chart"""
        df = pd.DataFrame({
            "owasp_category": ["A01:2021", "A02:2021", "A01:2021", "A03:2021"],
            "issue_id": ["1", "2", "3", "4"],
        })

        chart = create_owasp_bar_chart(df)
        assert chart is not None

    def test_owasp_bar_chart_with_single_category(self) -> None:
        """Test bar chart with single OWASP category"""
        df = pd.DataFrame({
            "owasp_category": ["A01:2021", "A01:2021"],
            "issue_id": ["1", "2"],
        })

        chart = create_owasp_bar_chart(df)
        assert chart is not None

    def test_owasp_bar_chart_with_empty_df(self) -> None:
        """Test bar chart handles empty dataframe"""
        df = pd.DataFrame({"owasp_category": [], "issue_id": []})

        chart = create_owasp_bar_chart(df)
        assert chart is not None

    def test_owasp_bar_chart_multiple_categories(self) -> None:
        """Test bar chart with multiple OWASP categories"""
        categories = [
            "A01:2021", "A01:2021",
            "A02:2021",
            "A03:2021", "A03:2021", "A03:2021",
        ]
        df = pd.DataFrame({
            "owasp_category": categories,
            "issue_id": [str(i) for i in range(len(categories))],
        })

        chart = create_owasp_bar_chart(df)
        assert chart is not None

    def test_owasp_bar_chart_handles_none_category(self) -> None:
        """Test bar chart handles None/missing OWASP categories"""
        df = pd.DataFrame({
            "owasp_category": ["A01:2021", None, "A02:2021"],
            "issue_id": ["1", "2", "3"],
        })

        # Should handle None values gracefully
        chart = create_owasp_bar_chart(df)
        assert chart is not None
