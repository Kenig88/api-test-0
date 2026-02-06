from __future__ import annotations  # делает аннотации типов "ленивыми" (как строки), иногда помогает с совместимостью
import json  # нужен, чтобы красиво (pretty) распечатать JSON
from typing import Any  # Any = "любой тип" (когда тип данных заранее неизвестен)
import allure  # Allure: прикрепление вложений к отчёту
import requests  # requests.Response тип (HTTP-ответ)
from allure_commons.types import AttachmentType  # типы вложений для Allure (JSON, TEXT и т.д.)


class Helper:
    """
    Общий helper-класс для Allure-вложений.

    Идея: в API-клиентах (UsersAPI/PostsAPI/CommentsAPI) мы хотим
    при каждом запросе прикреплять ответ в отчёт.
    Тогда, если тест упал, мы сразу видим:
    - статус
    - тело ответа (JSON или текст)
    """

    def attach_response(self, response: Any) -> None:
        """
        Прикрепляет данные в Allure как JSON.

        Ожидается, что `response` можно сериализовать в JSON (dict/list и т.п.).
        json.dumps(..., indent=4) делает "красивый" JSON с отступами,
        чтобы его удобно было читать в отчёте.
        ensure_ascii=False позволяет нормально отображать кириллицу и прочие символы.
        """
        body = json.dumps(response, indent=4, ensure_ascii=False)

        # allure.attach добавляет вложение в отчёт
        allure.attach(
            body=body,                       # содержимое вложения (строка)
            name="API Response",             # имя вложения в отчёте
            attachment_type=AttachmentType.JSON  # говорим Allure: это JSON (будет красиво отображаться)
        )

    def attach_response_safe(self, response: requests.Response) -> None:
        """
        Прикрепляет HTTP-ответ в Allure "безопасно".

        Логика:
        1) пробуем прочитать response.json()
           - если тело реально JSON, прикрепим его красиво
        2) если JSON распарсить нельзя (например HTML/текст/пусто),
           прикрепим просто response.text как обычный текст.
        """
        try:
            # response.json() вернёт dict/list, если тело валидный JSON
            self.attach_response(response.json())
        except Exception:
            # Если ответ не JSON — прикрепляем сырой текст, чтобы всё равно видеть тело ответа
            allure.attach(
                body=response.text,
                name="API Response (text)",
                attachment_type=AttachmentType.TEXT,
            )
