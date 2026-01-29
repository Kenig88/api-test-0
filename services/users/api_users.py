import allure
import requests
from services.users.endpoints import Endpoints
from services.users.payloads import Payloads
from services.users.user_model import UserModel
from utils.helper import Helper


class UsersAPI(Helper):
    def __init__(self, session: requests.Session, endpoints: Endpoints, timeout: int = 15):
        super().__init__()
        self.session = session
        self.endpoints = endpoints
        self.timeout = timeout

    # -------- helpers --------


    # -------- RAW (no asserts) --------

    @allure.step("POST /user/create (raw)")
    def create_user_response(self, payload: dict | None = None) -> requests.Response:
        if payload is None:
            payload = Payloads.create_user()

        response = self.session.post(
            url=self.endpoints.create_user,
            json=payload,
            timeout=self.timeout
        )
        self.attach_response_safe(response)
        return response

    @allure.step("GET /user/{user_id} (raw)")
    def get_user_by_id_response(self, user_id: str) -> requests.Response:
        response = self.session.get(
            url=self.endpoints.get_user_by_id(user_id),
            timeout=self.timeout
        )
        self.attach_response_safe(response)
        return response

    @allure.step("PUT /user/{user_id} (raw)")
    def update_user_response(self, user_id: str, payload: dict) -> requests.Response:
        response = self.session.put(
            url=self.endpoints.update_user(user_id),
            json=payload,
            timeout=self.timeout
        )
        self.attach_response_safe(response)
        return response

    @allure.step("DELETE /user/{user_id} (raw)")
    def delete_user_response(self, user_id: str) -> requests.Response:
        response = self.session.delete(
            url=self.endpoints.delete_user(user_id),
            timeout=self.timeout
        )
        self.attach_response_safe(response)
        return response

    # -------- CHECKED (Style A: asserts inside) --------

    @allure.step("Create user")
    def create_user(self):
        response = self.create_user_response()
        response_json = response.json()

        assert response.status_code in (200, 201), response_json

        user_id = response_json.get("id")
        assert user_id is not None, f"'id' not found in response: {response_json}"

        return user_id, UserModel(**response_json)

    @allure.step("Get user by id: {user_id}")
    def get_user_by_id(self, user_id: str) -> UserModel:
        response = self.get_user_by_id_response(user_id)
        response_json = response.json()

        assert response.status_code == 200, response_json
        return UserModel(**response_json)

    @allure.step("Update user by id: {user_id}")
    def update_user(self, user_id: str, payload: dict) -> UserModel:
        response = self.update_user_response(user_id, payload)
        response_json = response.json()

        assert response.status_code == 200, response_json
        return UserModel(**response_json)

    @allure.step("Delete user by id: {user_id}")
    def delete_user(self, user_id: str, allow_not_found: bool = False) -> None:
        response = self.delete_user_response(user_id)

        if allow_not_found and response.status_code == 404:
            return

        # dummyapi обычно 200/204
        try:
            body = response.json()
        except Exception:
            body = {"text": response.text}

        assert response.status_code in (200, 204), body
