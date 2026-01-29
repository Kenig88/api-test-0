from __future__ import annotations

import json
from typing import Any

import allure
import requests
from allure_commons.types import AttachmentType


class Helper:
    """Common helpers for Allure attachments."""

    def attach_response(self, response: Any) -> None:
        """Attach JSON-serializable data to Allure as pretty-printed JSON."""
        body = json.dumps(response, indent=4, ensure_ascii=False)
        allure.attach(body=body, name="API Response", attachment_type=AttachmentType.JSON)

    def attach_response_safe(self, response: requests.Response) -> None:
        """Attach response JSON if possible, otherwise attach raw text."""
        try:
            self.attach_response(response.json())
        except Exception:
            allure.attach(
                body=response.text,
                name="API Response (text)",
                attachment_type=AttachmentType.TEXT,
            )
