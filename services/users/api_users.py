import allure  # Allure — отчёты по тестам: шаги (step), вложения (attachments), удобный трейс действий
import requests  # HTTP-клиент: Session/Response типы и выполнение запросов

from services.users.user_endpoints import UserEndpoints  # класс, который хранит/строит URL'ы для user-эндпоинтов
from services.users.user_payloads import UserPayloads  # фабрика payload'ов (тела запросов) для users
from services.users.user_model import UserModel, UserPreviewModel  # Pydantic-модели ответа (полная и "preview")
from utils.helper import Helper  # общий helper (например attach_response_safe для прикрепления ответа в Allure)


class UsersAPI(Helper):
    """
    UsersAPI — обёртка над HTTP-запросами к /user.

    Как пользоваться:
    - методы *_response (RAW) → возвращают requests.Response, без assert'ов (удобно для негативных тестов)
    - методы без *_response (CHECKED) → проверяют статус, парсят JSON и возвращают модели (удобно для обычных тестов)
    """

    def __init__(self, session: requests.Session, endpoints: UserEndpoints, timeout: int = 15):
        super().__init__()  # инициализируем базовый Helper (если там есть общие методы/настройки)
        self.session = session      # requests.Session (обычно уже с заголовками app-id/token и т.д.)
        self.endpoints = endpoints  # объект, который знает URL'ы: create/get/update/delete/list
        self.timeout = timeout      # общий таймаут для запросов (сек), чтобы тесты не зависали

    # ==============================================RAW=(no=asserts)====================================================
    # ==================================================================================================================
    # ==============================================RAW=(no=asserts)====================================================

    # RAW методы: делают запрос и возвращают Response.
    # Здесь нет проверок status_code — это оставляем на уровень CHECKED или на тест.

    @allure.step("POST /user/create (raw)")
    def create_user_response(self, payload: dict | None = None) -> requests.Response:
        """
        RAW: создать пользователя.

        payload — dict (будет отправлен как JSON).
        Если payload не передан, генерируем дефолтный через UserPayloads.create_user().
        """
        if payload is None:
            payload = UserPayloads.create_user()  # генерируем валидные тестовые данные (email, имя, и т.д.)

        response = self.session.post(
            url=self.endpoints.create_user,  # URL эндпоинта создания пользователя (например /user/create)
            json=payload,                    # тело запроса в JSON
            timeout=self.timeout
        )
        self.attach_response_safe(response)  # прикрепляем ответ в Allure, чтобы легко дебажить
        return response

    @allure.step("GET /user/{user_id} (raw)")
    def get_user_by_id_response(self, user_id: str) -> requests.Response:
        """
        RAW: получить пользователя по id.
        """
        response = self.session.get(
            url=self.endpoints.get_user_by_id(user_id),  # URL строится с user_id (например /user/<id>)
            timeout=self.timeout
        )
        self.attach_response_safe(response)
        return response

    @allure.step("GET /user (raw)")
    def list_users_response(self, limit: int = 10, page: int = 0) -> requests.Response:
        """
        RAW: получить список пользователей.

        limit/page — параметры пагинации (query params):
        /user?limit=10&page=0
        """
        resp = self.session.get(
            self.endpoints.get_users_list(),            # URL списка пользователей
            params={"limit": limit, "page": page},      # query params
            timeout=self.timeout
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("PUT /user/{user_id} (raw)")
    def update_user_response(self, user_id: str, payload: dict) -> requests.Response:
        """
        RAW: обновить пользователя по id (PUT).

        payload — dict с полями, которые хотим обновить (например firstName/lastName/phone).
        """
        response = self.session.put(
            url=self.endpoints.update_user(user_id),  # URL строится с user_id
            json=payload,
            timeout=self.timeout
        )
        self.attach_response_safe(response)
        return response

    @allure.step("DELETE /user/{user_id} (raw)")
    def delete_user_response(self, user_id: str) -> requests.Response:
        """
        RAW: удалить пользователя по id.
        """
        response = self.session.delete(
            url=self.endpoints.delete_user(user_id),  # URL строится с user_id
            timeout=self.timeout
        )
        self.attach_response_safe(response)
        return response

    # ================================================CHECKED===========================================================
    # ==================================================================================================================
    # ================================================CHECKED===========================================================

    # CHECKED методы: используют RAW и добавляют проверки.
    # Это удобно, когда ты пишешь “счастливые” сценарии (happy path).

    @allure.step("Create user")
    def create_user(self):
        """
        Создаёт пользователя и возвращает:
        - user_id
        - UserModel (типизированная модель пользователя)

        Здесь уже есть assert на статус-код.
        """
        response = self.create_user_response()  # берём RAW метод
        response_json = response.json()         # ожидаем JSON в ответе

        # при создании часто бывает 201 Created, иногда 200 OK
        assert response.status_code in (200, 201), response_json

        # достаём id из ответа
        user_id = response_json.get("id")
        assert user_id is not None, f"'id' not found in response: {response_json}"

        # превращаем dict ответа в Pydantic-модель (валидация + удобный доступ к полям)
        return user_id, UserModel(**response_json)

    @allure.step("Get user by id: {user_id}")
    def get_user_by_id(self, user_id: str) -> UserModel:
        """
        Получает пользователя по id и возвращает UserModel.
        """
        response = self.get_user_by_id_response(user_id)
        response_json = response.json()
        assert response.status_code == 200, response_json
        return UserModel(**response_json)

    @allure.step("List users")
    def list_users(self, limit: int = 10, page: int = 0) -> list[UserPreviewModel]:
        """
        Возвращает список пользователей.

        Обычно список лежит в поле "data" ответа:
        {"data": [ {...}, {...} ], "total": ..., ...}
        """
        resp = self.list_users_response(limit=limit, page=page)
        body = resp.json()
        assert resp.status_code == 200, body

        # Каждый элемент списка превращаем в UserPreviewModel (короткая модель для списка)
        return [UserPreviewModel(**item) for item in body.get("data", [])]

    @allure.step("Update user by id: {user_id}")
    def update_user(self, user_id: str, payload: dict) -> UserModel:
        """
        Обновляет пользователя и возвращает обновлённый UserModel.
        """
        response = self.update_user_response(user_id, payload)
        response_json = response.json()
        assert response.status_code == 200, response_json
        return UserModel(**response_json)

    @allure.step("Delete user by id: {user_id}")
    def delete_user(self, user_id: str, allow_not_found: bool = False) -> None:
        """
        Удаляет пользователя.

        allow_not_found=True удобно для cleanup после тестов:
        - если пользователь уже удалён и API вернул 404 — не падаем.
        """
        response = self.delete_user_response(user_id)

        # Если это cleanup и пользователь уже отсутствует — считаем нормой
        if allow_not_found and response.status_code == 404:
            return

        # На delete некоторые API возвращают JSON, некоторые — пустое тело/текст.
        # Поэтому делаем try/except, чтобы корректно сформировать сообщение при падении assert.
        try:
            body = response.json()
        except Exception:
            body = {"text": response.text}

        # dummyapi обычно отвечает 200 OK или 204 No Content при успешном удалении
        assert response.status_code in (200, 204), body
