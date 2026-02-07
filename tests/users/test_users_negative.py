import allure
import pytest
from config.base_test import BaseTest
from utils.assertions import assert_dummyapi_error
from services.users.user_payloads import UserPayloads


@allure.epic("Administration")
@allure.feature("Users")
@pytest.mark.negative
class TestUsersNegative(BaseTest):

    # ---------------- APP_ID errors ----------------

    @allure.title("GET /user without app-id -> 403 APP_ID_MISSING")
    def test_get_users_without_app_id(self, raw_users, base_url: str):
        resp = raw_users.get(f"{base_url}/user?limit=5")
        assert_dummyapi_error(resp, 403, "APP_ID_MISSING")

    @allure.title("GET /user with invalid app-id -> 403 APP_ID_NOT_EXIST")
    def test_get_users_with_invalid_app_id(self, raw_users, base_url: str):
        resp = raw_users.get(
            f"{base_url}/user?limit=5",
            headers={"app-id": "invalid-app-id"},
        )
        assert_dummyapi_error(resp, 403, "APP_ID_NOT_EXIST")

    @allure.title("POST /user/create without app-id -> 403 APP_ID_MISSING")
    def test_create_user_without_app_id(self, raw_users, base_url: str):
        payload = UserPayloads.create_user()  # валидная база
        resp = raw_users.post(f"{base_url}/user/create", json_body=payload)
        assert_dummyapi_error(resp, 403, "APP_ID_MISSING")

    @allure.title("POST /user/create with invalid app-id -> 403 APP_ID_NOT_EXIST")
    def test_create_user_with_invalid_app_id(self, raw_users, base_url: str):
        payload = UserPayloads.create_user()  # валидная база
        resp = raw_users.post(
            f"{base_url}/user/create",
            headers={"app-id": "invalid-app-id"},
            json_body=payload,
        )
        assert_dummyapi_error(resp, 403, "APP_ID_NOT_EXIST")

    # ---------------- BODY_NOT_VALID ----------------

    @allure.title("POST /user/create missing lastName -> 400 BODY_NOT_VALID")
    def test_create_user_missing_fields(self, raw_users, api_token: str, base_url: str):
        payload = UserPayloads.create_user()  # 100% валидная база
        payload.pop("lastName")               # ломаем ровно 1 поле

        resp = raw_users.post(
            f"{base_url}/user/create",
            headers={"app-id": api_token},
            json_body=payload,
        )
        assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")

    # ---------------- PARAMS_NOT_VALID ----------------

    @allure.title("GET /user/{bad_id} -> 400 PARAMS_NOT_VALID")
    def test_get_user_bad_id(self, raw_users, api_token: str, base_url: str):
        resp = raw_users.get(
            f"{base_url}/user/123",
            headers={"app-id": api_token},
        )
        assert_dummyapi_error(resp, 400, "PARAMS_NOT_VALID")

    # ---------------- RESOURCE_NOT_FOUND ----------------

    @allure.title("GET /user/{id} not found -> 404 RESOURCE_NOT_FOUND")
    def test_get_user_not_found(self, raw_users, api_token: str, base_url: str):
        non_exist_id = "000000000000000000000000"
        resp = raw_users.get(
            f"{base_url}/user/{non_exist_id}",
            headers={"app-id": api_token},
        )
        assert_dummyapi_error(resp, 404, "RESOURCE_NOT_FOUND")

    @allure.title("DELETE /user/{id} not found -> 404 RESOURCE_NOT_FOUND")
    def test_delete_user_not_found(self):
        non_exist_id = "000000000000000000000000"
        resp = self.api_users.delete_user_response(non_exist_id)
        assert_dummyapi_error(resp, 404, "RESOURCE_NOT_FOUND")

    # ---------------- PATH_NOT_FOUND ----------------

    @allure.title("GET wrong path -> 404 PATH_NOT_FOUND")
    def test_path_not_found(self, raw_users, api_token: str, base_url: str):
        resp = raw_users.get(
            f"{base_url}/userzzz",
            headers={"app-id": api_token},
        )
        assert_dummyapi_error(resp, 404, "PATH_NOT_FOUND")
