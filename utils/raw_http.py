from __future__ import annotations  # позволяет писать аннотации типов без кавычек (удобно и совместимо)

from typing import Callable, Optional
import requests

# Тип "функция-коллбек", которая принимает requests.Response и ничего не возвращает.
# Мы будем передавать сюда, например, attach_response_safe для Allure.
AttachFn = Callable[[requests.Response], None]


class RawHttp:
    """
    "Сырой" HTTP-клиент для негативных сценариев.

    Зачем он нужен:
    - В негативных тестах мы часто хотим отправлять запросы "вручную",
      например БЕЗ app-id или С неправильным app-id.
    - При этом мы хотим сохранять удобство: единые заголовки, единый timeout,
      и обязательно прикреплять ответ в Allure (если передали attach-функцию).

    Важно:
    - Этот клиент НИЧЕГО не ассертит и не валидирует. Он просто делает запрос и возвращает Response.
    - app-id по умолчанию НЕ добавляется — это специально для негативных проверок.
    """

    def __init__(self, timeout: int, attach: Optional[AttachFn] = None):
        """
        timeout: таймаут для всех запросов (секунды)
        attach: функция, которая "прикрепит" ответ в Allure (например, api_users.attach_response_safe)
                Можно не передавать — тогда аттачей не будет.
        """
        self.timeout = timeout
        self.attach = attach

        # Session = "долго живущий" клиент requests.
        # Плюсы Session:
        # - переиспользует соединения (быстрее, чем каждый раз requests.get/post)
        # - можно хранить общие настройки
        self.session = requests.Session()

    def close(self) -> None:
        """Закрываем session (освобождаем ресурсы/соединения). Вызываем в конце фикстуры."""
        self.session.close()

    def _request(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
        json_body: dict | None = None,
    ) -> requests.Response:
        """
        Универсальный метод для любых HTTP-методов.

        method: "GET"/"POST"/"PUT"/...
        url: полный URL (например f"{base_url}/user?limit=5")
        headers: дополнительные заголовки (например {"app-id": api_token})
        json_body: тело запроса для POST/PUT/PATCH (словарь, requests сам превратит в JSON)
        """

        # Базовые заголовки: хотим получать JSON в ответе.
        h = {"Accept": "application/json"}

        # Для запросов с телом обычно нужен Content-Type application/json
        # (GET/DELETE обычно без тела).
        if method.upper() in {"POST", "PUT", "PATCH"}:
            h["Content-Type"] = "application/json"

        # Если тест передал дополнительные заголовки — добавим/перезапишем.
        # Например, тут можно передать "app-id".
        if headers:
            h.update(headers)

        # Делаем запрос через session.request — это универсальная точка входа.
        resp = self.session.request(
            method=method,
            url=url,
            headers=h,
            json=json_body,          # requests сам сериализует dict -> JSON
            timeout=self.timeout,    # если сервер долго не отвечает — упадём по таймауту
        )

        # Если передали attach-функцию — прикрепим ответ в Allure,
        # чтобы при падении теста было видно, что вернул API.
        if self.attach:
            self.attach(resp)

        return resp

    def get(self, url: str, headers: dict | None = None) -> requests.Response:
        """Удобный метод для GET."""
        return self._request("GET", url, headers=headers)

    def post(
        self,
        url: str,
        headers: dict | None = None,
        json_body: dict | None = None,
    ) -> requests.Response:
        """Удобный метод для POST."""
        return self._request("POST", url, headers=headers, json_body=json_body)
