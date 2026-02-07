from __future__ import annotations

import json
from typing import Any
import allure
import requests
from allure_commons.types import AttachmentType


class Helper:
    """
    Общий helper-класс для Allure-вложений.

    Теперь прикрепляем:
    - Request: method + url + headers + body
    - Response meta: status_code + headers
    - Response body: JSON (pretty) или text
    """

    # какие заголовки "маскируем" в отчёте (чтобы не светить токены)
    _SENSITIVE_HEADERS = {"authorization", "app-id", "x-api-key", "api-key", "token"}

    def _mask_headers(self, headers: dict[str, Any]) -> dict[str, Any]:
        """Скрываем значения чувствительных заголовков."""
        masked = dict(headers)
        for k in list(masked.keys()):
            if k.lower() in self._SENSITIVE_HEADERS:
                masked[k] = "***"
        return masked

    def attach_response(self, response: Any, name: str = "API Response") -> None:
        """Прикрепляет любые данные в Allure как pretty JSON."""
        body = json.dumps(response, indent=4, ensure_ascii=False)
        allure.attach(body=body, name=name, attachment_type=AttachmentType.JSON)

    def attach_text(self, text: str, name: str) -> None:
        """Прикрепляет текст в Allure."""
        allure.attach(body=text, name=name, attachment_type=AttachmentType.TEXT)

    def attach_response_safe(self, response: requests.Response) -> None:
        """
        Прикрепляет request+response в Allure "безопасно".

        1) Request: method/url/headers/body
        2) Response meta: status_code/headers
        3) Response body: json() или text
        """

        # -------------------- REQUEST --------------------
        try:
            req = response.request  # requests.PreparedRequest
            req_headers = self._mask_headers(dict(req.headers) if req.headers else {})

            req_info: dict[str, Any] = {
                "method": req.method,
                "url": req.url,          # url уже включает query params
                "headers": req_headers,
            }

            # body может быть None / bytes / str
            if req.body is None:
                req_info["body"] = None
            else:
                if isinstance(req.body, (bytes, bytearray)):
                    body_text = req.body.decode("utf-8", errors="replace")
                else:
                    body_text = str(req.body)

                # если тело похоже на JSON — попробуем распарсить красиво
                stripped = body_text.strip()
                if stripped.startswith("{") or stripped.startswith("["):
                    try:
                        req_info["body_json"] = json.loads(body_text)
                    except Exception:
                        req_info["body"] = body_text
                else:
                    req_info["body"] = body_text

            self.attach_response(req_info, name="API Request")
        except Exception as e:
            self.attach_text(str(e), name="API Request (attach failed)")

        # -------------------- RESPONSE META --------------------
        try:
            resp_meta = {
                "status_code": response.status_code,
                "headers": dict(response.headers) if response.headers else {},
            }
            self.attach_response(resp_meta, name="API Response Meta")
        except Exception as e:
            self.attach_text(str(e), name="API Response Meta (attach failed)")

        # -------------------- RESPONSE BODY --------------------
        try:
            self.attach_response(response.json(), name="API Response Body")
        except Exception:
            self.attach_text(response.text or "", name="API Response Body (text)")