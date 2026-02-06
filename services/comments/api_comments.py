import allure  # библиотека для красивых отчётов (шаги, вложения, скриншоты/логи и т.д.)
import requests  # HTTP-клиент, Response/Session типы
from services.comments.comment_endpoints import CommentEndpoints  # объект, который хранит URL'ы/эндпоинты для comments
from services.comments.comment_payloads import CommentPayloads  # фабрика payload'ов (готовые тела запросов)
from services.comments.comments_model import CommentModel, CommentPreviewModel  # Pydantic/модели ответа
from utils.helper import Helper  # ваш общий хелпер (например, attach_response_safe для Allure)


class CommentsAPI(Helper):
    """
    API-клиент для работы с комментариями.

    Важно:
    - Методы *_response = "RAW" уровень: делают запрос, возвращают requests.Response, без assert'ов.
    - Методы без *_response = "CHECKED" уровень: используют RAW методы, проверяют статус-коды,
      парсят JSON и возвращают типизированные модели.
    """

    def __init__(self, session: requests.Session, endpoints: CommentEndpoints, timeout: int = 15):
        super().__init__()  # инициализация базового Helper (если там есть состояние/настройки)
        self.session = session  # requests.Session, уже с заголовками (app-id, content-type и т.д.)
        self.endpoints = endpoints  # объект, который знает все URL'ы для comments
        self.timeout = timeout  # общий таймаут для всех запросов этого клиента

    # ==============================================RAW=(no=asserts)====================================================
    # ==================================================================================================================
    # ==============================================RAW=(no=asserts)====================================================

    # RAW-методы: "низкоуровневые". Делают запрос и возвращают Response.
    # Плюсы:
    # - удобно писать негативные тесты (например, ожидаем 400/404)
    # - можно проверить заголовки/тело/текст ответа без жёстких проверок статуса

    @allure.step("GET /comment (raw)")
    def list_comments_response(self, limit: int = 10, page: int = 0) -> requests.Response:
        # GET /comment?limit=...&page=...
        resp = self.session.get(
            self.endpoints.list_comments,                 # готовый URL эндпоинта
            params={"limit": limit, "page": page},        # query-параметры пагинации
            timeout=self.timeout                          # чтобы запрос не завис
        )
        self.attach_response_safe(resp)  # прикладываем в отчёт (JSON/text/status) безопасно
        return resp

    @allure.step("GET /post/{post_id}/comment (raw)")
    def list_comments_by_post_response(self, post_id: str, limit: int = 10, page: int = 0) -> requests.Response:
        # эндпоинт строится функцией, потому что нужен post_id
        resp = self.session.get(
            self.endpoints.comments_by_post(post_id),     # например: /post/<id>/comment
            params={"limit": limit, "page": page},
            timeout=self.timeout
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("GET /user/{user_id}/comment (raw)")
    def list_comments_by_user_response(self, user_id: str, limit: int = 10, page: int = 0) -> requests.Response:
        resp = self.session.get(
            self.endpoints.comments_by_user(user_id),     # например: /user/<id>/comment
            params={"limit": limit, "page": page},
            timeout=self.timeout
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("POST /comment/create (raw)")
    def create_comment_response(self, payload: dict) -> requests.Response:
        # POST /comment/create с JSON телом
        resp = self.session.post(
            self.endpoints.create_comment,
            json=payload,                                 # requests сам сделает json.dumps + header
            timeout=self.timeout
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("DELETE /comment/{comment_id} (raw)")
    def delete_comment_response(self, comment_id: str) -> requests.Response:
        # DELETE /comment/<id>
        resp = self.session.delete(
            self.endpoints.delete_comment(comment_id),    # функция, потому что url зависит от id
            timeout=self.timeout
        )
        self.attach_response_safe(resp)
        return resp

    # ================================================CHECKED===========================================================
    # ==================================================================================================================
    # ================================================CHECKED===========================================================

    # CHECKED-методы: "высокоуровневые". Делают assert, парсят ответ, возвращают модели.

    @allure.step("Create comment (owner={owner_id}, post={post_id})")
    def create_comment(self, owner_id: str, post_id: str, payload: dict | None = None) -> tuple[str, CommentModel]:
        # Если payload не передали — собираем дефолтный через фабрику payload'ов
        if payload is None:
            payload = CommentPayloads.create_comment(owner_id=owner_id, post_id=post_id)

        # Делаем запрос через RAW метод
        resp = self.create_comment_response(payload)

        # Парсим JSON-ответ (здесь ожидается JSON)
        body = resp.json()

        # Проверяем статус (API может вернуть 200 или 201 при создании)
        assert resp.status_code in (200, 201), body

        # Достаём id комментария
        comment_id = body.get("id")
        assert comment_id, f"'id' not found in response: {body}"

        # Возвращаем id + типизированную модель (удобно в тестах: автокомплит, проверки схемы)
        return comment_id, CommentModel(**body)

    @allure.step("Delete comment by id: {comment_id}")
    def delete_comment(self, comment_id: str, allow_not_found: bool = False) -> str | None:
        """
        Удаляет комментарий по id.

        allow_not_found=True:
        - если комментарий уже удалён и API вернул 404 — считаем это ок и возвращаем None.
        """
        resp = self.delete_comment_response(comment_id)

        # Полезно для cleanup: не падать, если уже удалено
        if allow_not_found and resp.status_code == 404:
            return None  # docs: delete returns string id

        # В остальных случаях считаем нормой 200 или 204
        assert resp.status_code in (200, 204), resp.text

        # API может вернуть:
        # - JSON (dict)
        # - строку (например "id") или вообще пустое тело при 204
        try:
            body = resp.json()
        except Exception:
            body = resp.text.strip()

        # Нормализуем ответ к строке id (если можем)
        if isinstance(body, str):
            return body.strip('"')  # иногда id приходит в кавычках
        if isinstance(body, dict):
            return body.get("id") or body.get("data") or str(body)
        return str(body)

    @allure.step("List comments")
    def list_comments(self, limit: int = 10, page: int = 0) -> list[CommentPreviewModel]:
        # Получаем Response
        resp = self.list_comments_response(limit=limit, page=page)
        body = resp.json()

        # Ожидаем успешный ответ
        assert resp.status_code == 200, body

        # Обычно список лежит в body["data"]
        return [CommentPreviewModel(**item) for item in body.get("data", [])]

    @allure.step("List comments by post: {post_id}")
    def list_comments_by_post(self, post_id: str, limit: int = 10, page: int = 0) -> list[CommentPreviewModel]:
        resp = self.list_comments_by_post_response(
            post_id=post_id,
            limit=limit,
            page=page
        )
        body = resp.json()
        assert resp.status_code == 200, body
        return [CommentPreviewModel(**item) for item in body.get("data", [])]

    @allure.step("List comments by user: {user_id}")
    def list_comments_by_user(self, user_id: str, limit: int = 10, page: int = 0) -> list[CommentPreviewModel]:
        resp = self.list_comments_by_user_response(
            user_id=user_id,
            limit=limit,
            page=page
        )
        body = resp.json()
        assert resp.status_code == 200, body
        return [CommentPreviewModel(**item) for item in body.get("data", [])]
