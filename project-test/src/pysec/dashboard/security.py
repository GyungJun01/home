"""
Security validation and data masking for dashboard (TAG-REQ-DASH-005, TAG-REQ-DASH-006)

Implements 3-tier file validation (extension → size → JSON schema) and
sensitive data masking for secure dashboard operation.
"""

import json
import re
from typing import Any

from pydantic import ValidationError

from pysec.scanner.models import ScanReport

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = [".json"]


def validate_upload(file: Any) -> dict[str, Any]:
    """
    Validate uploaded JSON file with 3-tier security checks.

    Tier 1: File size validation (max 10MB)
    Tier 2: File extension validation (.json only)
    Tier 3: JSON schema validation (Pydantic ScanReport)

    Args:
        file: Uploaded file object with name, size, and read() method

    Returns:
        Parsed JSON data as dictionary

    Raises:
        ValueError: If validation fails at any tier

    TAG-REQ-DASH-005: File upload validation with clear error messages
    """
    # Tier 1: File size check
    # Get file size by seeking to end
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"파일 크기가 10MB 제한을 초과합니다. 현재: {file_size / 1024 / 1024:.1f}MB"
        )

    # Tier 2: File extension check
    file_name: str = file.name
    if not any(file_name.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise ValueError(f"JSON 파일만 허용됩니다. 현재: {file_name}")

    # Tier 3: JSON parsing
    file.seek(0)
    try:
        data: dict[str, Any] = json.load(file)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 형식이 올바르지 않습니다: {e}") from e

    # Tier 4: Schema validation (Pydantic)
    try:
        ScanReport(**data)
    except ValidationError as e:
        raise ValueError(f"스키마가 일치하지 않습니다: {e}") from e

    return data


def mask_sensitive_data(text: str) -> str:
    r"""
    Mask sensitive information in text using regex patterns.

    Masks:
    - Unix home directory paths (/home/username)
    - Windows user paths (C:\Users\username\)
    - API keys, tokens, secrets
    - Passwords

    Args:
        text: Text to mask

    Returns:
        Text with sensitive data masked

    TAG-REQ-DASH-006: Automatic masking of sensitive data in UI display
    """
    masked = text

    # Unix home directory pattern
    masked = re.sub(r"/home/[^/]+/", "/home/***/", masked)

    # Windows user path pattern - avoid escapes in replacement
    masked = re.sub(
        r"C:\\Users\\[^\\]+\\", "C:\\\\Users\\\\***\\\\", masked
    )

    # API key pattern (case-insensitive)
    masked = re.sub(
        r"(api[_-]?key)\s*=\s*\w+",
        r"\1=***",
        masked,
        flags=re.IGNORECASE,
    )

    # Token pattern
    masked = re.sub(
        r"(token)\s*=\s*[\w.-]+",
        r"\1=***",
        masked,
        flags=re.IGNORECASE,
    )

    # Password pattern with quotes
    masked = re.sub(
        r"(password|passwd|pwd)\s*=\s*\"[^\"]+\"",
        r'\1="***"',
        masked,
        flags=re.IGNORECASE,
    )

    # Password pattern without quotes
    masked = re.sub(
        r"(password|passwd|pwd)\s*=\s*\w+",
        r"\1=***",
        masked,
        flags=re.IGNORECASE,
    )

    return masked
