"""
Chart components for dashboard visualization.

Implements Plotly Pie charts (severity, confidence distribution) and
Altair Bar charts (OWASP Top 10 mapping).

TAG-REQ-DASH-003: Severity distribution pie chart
TAG-REQ-DASH-014: OWASP Top 10 bar chart
"""

from typing import Any

import altair as alt
import pandas as pd
import plotly.graph_objects as go


def create_severity_pie_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a Plotly Pie chart for severity distribution.

    Args:
        df: DataFrame with 'severity' column

    Returns:
        Plotly Figure object with pie chart

    TAG-REQ-DASH-003: Severity distribution visualization
    """
    if len(df) == 0:
        # Handle empty dataframe
        fig = go.Figure()
        fig.add_annotation(text="No data available")
        return fig

    severity_counts = df["severity"].value_counts()

    # Color mapping for severities
    color_map = {
        "HIGH": "#FF4B4B",      # Red
        "MEDIUM": "#FFA500",    # Orange
        "LOW": "#4B9FFF",       # Blue
        "INFO": "#808080"       # Gray
    }

    colors = [color_map.get(severity, "#000000") for severity in severity_counts.index]

    fig = go.Figure(
        data=[go.Pie(
            labels=severity_counts.index,
            values=severity_counts.values,
            marker={"colors": colors},
            hole=0.4,  # Donut chart
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>",
            textinfo="label+percent",
            textposition="inside",
        )]
    )

    fig.update_layout(
        title="Severity Distribution",
        font={"size": 12},
        height=400,
        showlegend=True,
    )

    return fig


def create_confidence_pie_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a Plotly Pie chart for confidence distribution.

    Args:
        df: DataFrame with 'confidence' column

    Returns:
        Plotly Figure object with pie chart
    """
    if len(df) == 0:
        # Handle empty dataframe
        fig = go.Figure()
        fig.add_annotation(text="No data available")
        return fig

    confidence_counts = df["confidence"].value_counts()

    # Color mapping for confidence levels
    color_map = {
        "HIGH": "#2E86AB",      # Dark Blue
        "MEDIUM": "#A23B72",    # Purple
        "LOW": "#F18F01"        # Orange
    }

    colors = [color_map.get(conf, "#000000") for conf in confidence_counts.index]

    fig = go.Figure(
        data=[go.Pie(
            labels=confidence_counts.index,
            values=confidence_counts.values,
            marker={"colors": colors},
            hole=0.4,
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>",
            textinfo="label+percent",
            textposition="inside",
        )]
    )

    fig.update_layout(
        title="Confidence Distribution",
        font={"size": 12},
        height=400,
        showlegend=True,
    )

    return fig


def create_owasp_bar_chart(df: pd.DataFrame) -> Any:
    """
    Create an Altair Bar chart for OWASP Top 10 categories.

    Args:
        df: DataFrame with 'owasp_category' column

    Returns:
        Altair chart object

    TAG-REQ-DASH-014: OWASP Top 10 category distribution
    """
    if len(df) == 0:
        # Return empty chart for empty dataframe
        empty_df = pd.DataFrame({"category": [], "count": []})
        return alt.Chart(empty_df).mark_bar()

    # Filter out None values
    owasp_data = df[df["owasp_category"].notna()]

    if len(owasp_data) == 0:
        empty_df = pd.DataFrame({"category": [], "count": []})
        return alt.Chart(empty_df).mark_bar()

    owasp_counts = owasp_data["owasp_category"].value_counts().reset_index()
    owasp_counts.columns = ["category", "count"]
    owasp_counts = owasp_counts.sort_values("count", ascending=True)

    chart = alt.Chart(owasp_counts).mark_bar().encode(
        x=alt.X("count:Q", title="Number of Issues"),
        y=alt.Y("category:N", title="OWASP Category", sort="-x"),
        color=alt.Color("count:Q", scale=alt.Scale(scheme="reds")),
        tooltip=["category", "count"]
    ).properties(
        title="OWASP Top 10 Distribution",
        width=600,
        height=400,
    ).interactive()

    return chart
