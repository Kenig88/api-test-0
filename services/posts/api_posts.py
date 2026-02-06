import allure  # Allure — отчёты по тестам: "шаги", вложения, удобный лог запросов/ответов
import requests  # requests.Session и requests.Response (типы и HTTP-клиент)

from services.posts.post_endpoints import PostEndpoints  # объект, который хранит/строит URL'ы для post-эндпоинтов
from services.posts.post_payloads import PostPayloads  # фабрика payload'ов (тела запросов) для постов
from services.posts.post_model import PostModel, PostPreviewModel  # Pydantic-модели ответа (полная/короткая)
from utils.helper import Helper  # общий helper (например attach_response_safe для прикрепления ответа в Allure)


class PostsAPI(Helper):
    """
    PostsAPI — клиент-обёртка над HTTP-запросами к "постам".

    Структура специально разделена на 2 уровня:

    1) RAW методы (*_response)
       - делают запрос и возвращают requests.Response
       - НЕ содержат assert'ов
       - полезны для негативных тестов (ожидаем 400/404 и т.п.)

    2) CHECKED методы (без *_response)
       - используют RAW методы
       - проверяют status_code через assert
       - парсят JSON
       - возвращают типизированные модели (PostModel/PostPreviewModel)
    """

    def __init__(self, session: requests.Session, endpoints: PostEndpoints, timeout: int = 15):
        super().__init__()  # вызываем конструктор Helper (если там есть настройки/методы)
        self.session = session      # requests.Session: уже с заголовками (токен, content-type и т.д.)
        self.endpoints = endpoints  # PostEndpoints: умеет отдавать URL'ы (list, create, by_id, by_user...)
        self.timeout = timeout      # таймаут для каждого запроса (сек), чтобы тесты не "висели"

    # ==============================================RAW=(no=asserts)====================================================
    # ==================================================================================================================
    # ==============================================RAW=(no=asserts)====================================================

    # RAW методы: "низкий уровень" — просто запрос + return Response.
    # Здесь мы также прикладываем ответ в Allure, чтобы при падении теста видеть детали.

    @allure.step("POST /post/create (raw)")
    def create_post_response(self, payload: dict) -> requests.Response:
        """
        RAW: создать пост.

        payload — dict, который будет отправлен как JSON.
        """
        resp = self.session.post(
            self.endpoints.create_post,  # URL для создания (например /post/create)
            json=payload,                # тело запроса в JSON
            timeout=self.timeout
        )
        self.attach_response_safe(resp)  # прикрепляем ответ в Allure (статус/тело), удобно для дебага
        return resp

    @allure.step("GET /post/{post_id} (raw)")
    def get_post_by_id_response(self, post_id: str) -> requests.Response:
        """
        RAW: получить пост по id.
        """
        resp = self.session.get(
            self.endpoints.post_by_id(post_id),  # URL формируется с post_id (например /post/<id>)
            timeout=self.timeout
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("PUT /post/{post_id} (raw)")
    def update_post_response(self, post_id: str, payload: dict) -> requests.Response:
        """
        RAW: обновить пост по id (PUT).

        payload — dict с полями, которые хотим обновить (text/image/tags...).
        """
        resp = self.session.put(
            self.endpoints.post_by_id(post_id),  # тот же /post/<id>
            json=payload,
            timeout=self.timeout
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("DELETE /post/{post_id} (raw)")
    def delete_post_response(self, post_id: str) -> requests.Response:
        """
        RAW: удалить пост по id.
        """
        resp = self.session.delete(
            self.endpoints.post_by_id(post_id),
            timeout=self.timeout
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("GET /post (raw)")
    def list_posts_response(self, limit: int = 10, page: int = 0) -> requests.Response:
        """
        RAW: получить список постов.

        limit/page — параметры пагинации, уходят как query params:
        /post?limit=10&page=0
        """
        resp = self.session.get(
            self.endpoints.list_posts,                 # URL списка постов (например /post)
            params={"limit": limit, "page": page},     # query params
            timeout=self.timeout
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("GET /user/{user_id}/post (raw)")
    def list_posts_by_user_response(self, user_id: str, limit: int = 10, page: int = 0) -> requests.Response:
        """
        RAW: получить список постов конкретного пользователя.
        """
        resp = self.session.get(
            self.endpoints.posts_by_user(user_id),     # URL формируется с user_id (например /user/<id>/post)
            params={"limit": limit, "page": page},
            timeout=self.timeout
        )
        self.attach_response_safe(resp)
        return resp

    # ================================================CHECKED===========================================================
    # ==================================================================================================================
    # ================================================CHECKED===========================================================

    # CHECKED методы: "высокий уровень" — добавляют проверки статуса и возвращают модели.

    @allure.step("Create post (owner={owner_id})")
    def create_post(self, owner_id: str, payload: dict | None = None) -> tuple[str, PostModel]:
        """
        Создаёт пост и возвращает:
        - id поста
        - PostModel (полная модель поста)

        Если payload не передали — создадим дефолтный через PostPayloads.
        """
        if payload is None:
            payload = PostPayloads.create_post(owner_id)  # дефолтный валидный payload

        resp = self.create_post_response(payload)  # делаем запрос через RAW метод
        body = resp.json()                         # парсим JSON-ответ

        # При создании API обычно возвращает 201 Created или иногда 200 OK
        assert resp.status_code in (200, 201), body

        # Достаём id поста из ответа
        post_id = body.get("id")
        assert post_id, f"'id' not found in response: {body}"

        # Возвращаем id и валидируем структуру ответа через Pydantic
        return post_id, PostModel(**body)

    @allure.step("Get post by id: {post_id}")
    def get_post_by_id(self, post_id: str) -> PostModel:
        """
        Получает пост по id и возвращает PostModel.
        """
        resp = self.get_post_by_id_response(post_id)
        body = resp.json()
        assert resp.status_code == 200, body
        return PostModel(**body)

    @allure.step("Update post by id: {post_id}")
    def update_post(self, post_id: str, payload: dict) -> PostModel:
        """
        Обновляет пост и возвращает обновлённый PostModel.
        """
        resp = self.update_post_response(post_id, payload)
        body = resp.json()
        assert resp.status_code == 200, body
        return PostModel(**body)

    @allure.step("Delete post by id: {post_id}")
    def delete_post(self, post_id: str, allow_not_found: bool = False) -> str | None:
        """
        Удаляет пост.

        allow_not_found=True удобно для cleanup после тестов:
        - если API вернул 404 (уже удалён) — считаем это нормальным и возвращаем None
        """
        resp = self.delete_post_response(post_id)

        # Если это cleanup и пост уже удалён — просто выходим
        if allow_not_found and resp.status_code == 404:
            return None  # некоторые API на delete возвращают id строкой

        # Нормальными считаем 200 OK или 204 No Content
        assert resp.status_code in (200, 204), resp.text

        # Некоторые API возвращают JSON, некоторые — пустое тело или строку
        try:
            body = resp.json()
        except Exception:
            body = resp.text.strip()

        # Нормализуем ответ к строке (id), чтобы тестам было удобно
        if isinstance(body, str):
            return body.strip('"')  # если пришло "id" в кавычках — убираем кавычки
        if isinstance(body, dict):
            return body.get("id") or body.get("data") or str(body)
        return str(body)

    @allure.step("List posts")
    def list_posts(self, limit: int = 10, page: int = 0) -> list[PostPreviewModel]:
        """
        Возвращает список постов в формате превью (обычно API отдаёт их в body["data"]).
        """
        resp = self.list_posts_response(limit=limit, page=page)
        body = resp.json()
        assert resp.status_code == 200, body

        # Достаём список элементов из поля "data"
        data = body.get("data", [])

        # Превращаем каждый dict в PostPreviewModel (валидация + удобный доступ к полям)
        return [PostPreviewModel(**item) for item in data]

    @allure.step("List posts by user: {user_id}")
    def list_posts_by_user(self, user_id: str, limit: int = 10, page: int = 0) -> list[PostPreviewModel]:
        """
        Возвращает список постов конкретного пользователя (preview-модели).
        """
        resp = self.list_posts_by_user_response(
            user_id=user_id,
            limit=limit,
            page=page
        )
        body = resp.json()
        assert resp.status_code == 200, body

        data = body.get("data", [])
        return [PostPreviewModel(**item) for item in data]