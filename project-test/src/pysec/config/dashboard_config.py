"""
Dashboard configuration module (TAG-REQ-DASH-001)

Configuration settings for Streamlit dashboard.
"""

from dataclasses import dataclass


@dataclass
class DashboardConfig:
    """Configuration for Streamlit dashboard"""

    # Server settings
    port: int = 8501
    address: str = "localhost"
    enable_cors: bool = False
    enable_xsrf_protection: bool = True
    max_upload_size: int = 10  # MB

    # UI settings
    primary_color: str = "#FF4B4B"
    background_color: str = "#FFFFFF"
    secondary_background_color: str = "#F0F2F6"
    text_color: str = "#262730"
    font: str = "sans serif"

    # Feature settings
    enable_dark_mode: bool = False
    enable_autorefresh: bool = False
    autorefresh_interval: int = 30  # seconds

    # Data settings
    default_page_size: int = 100
    max_page_size: int = 500


def get_default_config() -> DashboardConfig:
    """
    Get default dashboard configuration.

    Returns:
        DashboardConfig with default values
    """
    return DashboardConfig()
