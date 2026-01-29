from __future__ import annotations

from typing import Any

import allure
import requests


def assert_dummyapi_error(resp: requests.Response, expected_status: int, expected_error: str) -> dict[str, Any]:
    """Assert DummyAPI error response format.

    DummyAPI usually returns JSON like: {"error": "...", ...}
    """
    assert resp.status_code == expected_status, f"{resp.status_code} {resp.text}"

    try:
        body: dict[str, Any] = resp.json()
    except Exception as e:
        raise AssertionError(f"Response is not JSON: {resp.text}") from e

    # Attach for easier debugging in Allure
    try:
        allure.attach(
            body=str(body),
            name="DummyAPI error body",
            attachment_type=allure.attachment_type.JSON,
        )
    except Exception:
        pass

    assert body.get("error") == expected_error, body
    return body
