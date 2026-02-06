from __future__ import annotations  # делает аннотации "ленивыми" (как строки) — полезно для совместимости/циклов типов
from typing import Any  # Any = "любой тип" (когда структура данных может быть разной)
import allure  # для прикрепления деталей в Allure-отчёт
import requests  # чтобы типизировать resp как requests.Response


def assert_dummyapi_error(
        resp: requests.Response,     # объект ответа от requests (статус, headers, json(), text...)
        expected_status: int,         # какой статус-код мы ожидаем (например 400/404)
        expected_error: str           # какую строку ошибки ожидаем в поле "error"
) -> dict[str, Any]:
    """
    Проверяет, что DummyAPI вернул ошибку в ожидаемом формате.

    Обычно DummyAPI возвращает JSON вида:
      {"error": "some message", ...}

    Эта функция полезна в негативных тестах:
    - мы специально отправляем "плохие" данные
    - и хотим убедиться, что API вернул правильный статус и текст ошибки
    """

    # 1) Проверяем HTTP статус-код.
    # Если статус не совпал — показываем статус и текст ответа (удобно для быстрого дебага).
    assert resp.status_code == expected_status, f"{resp.status_code} {resp.text}"

    # 2) Пытаемся распарсить JSON.
    # Если ответ не JSON (например HTML или пустое тело) — падаем понятной ошибкой.
    try:
        body: dict[str, Any] = resp.json()
    except Exception as e:
        raise AssertionError(f"Response is not JSON: {resp.text}") from e

    # 3) Прикрепляем тело ошибки в Allure.
    # Это нужно, чтобы в отчёте было видно, что реально вернул API (очень помогает при разборе падений).
    # try/except нужен на случай, если Allure не доступен (или attach упадёт) — тесты не должны из-за этого ломаться.
    try:
        allure.attach(
            body=str(body),                            # что прикрепляем (строкой)
            name="DummyAPI error body",                # имя вложения в отчёте
            attachment_type=allure.attachment_type.JSON,  # тип вложения (чтобы Allure подсветил как JSON)
        )
    except Exception:
        pass  # если attach не получилось — просто пропускаем, тест дальше продолжит проверки

    # 4) Проверяем, что поле "error" в JSON совпадает с ожидаемой ошибкой.
    # Если не совпало — выводим весь body, чтобы увидеть, что пришло.
    assert body.get("error") == expected_error, body

    # 5) Возвращаем распарсенный JSON, чтобы тест мог дополнительно проверить другие поля при необходимости.
    return body