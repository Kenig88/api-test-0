import allure
import pytest
import requests
from config.base_test import BaseTest
from utils.assertions import assert_dummyapi_error


@allure.epic("Administration")
@allure.feature("Users")
@pytest.mark.negative
class TestUsersNegative(BaseTest):
    TIMEOUT = 15

    def _get(self, url: str, headers: dict | None = None) -> requests.Response:
        h = {"Accept": "application/json"}
        if headers:
            h.update(headers)
        resp = requests.get(url, headers=h, timeout=self.TIMEOUT)
        self.api_users.attach_response_safe(resp)
        return resp

    def _post(self, url: str, headers: dict | None = None, json_body: dict | None = None) -> requests.Response:
        h = {"Accept": "application/json", "Content-Type": "application/json"}
        if headers:
            h.update(headers)
        resp = requests.post(url, headers=h, json=json_body, timeout=self.TIMEOUT)
        self.api_users.attach_response_safe(resp)
        return resp


    # ---------------- APP_ID errors ----------------

    @allure.title("GET /user without app-id -> 403 APP_ID_MISSING")
    def test_get_users_without_app_id(self, base_url: str):
        resp = self._get(f"{base_url}/user?limit=5")
        assert_dummyapi_error(resp, 403, "APP_ID_MISSING")

    @allure.title("GET /user with invalid app-id -> 403 APP_ID_NOT_EXIST")
    def test_get_users_with_invalid_app_id(self, base_url: str):
        resp = self._get(
            f"{base_url}/user?limit=5",
            headers={"app-id": "invalid-app-id"},
        )
        assert_dummyapi_error(resp, 403, "APP_ID_NOT_EXIST")


    # ---------------- BODY_NOT_VALID ----------------

    @allure.title("POST /user/create with missing required fields -> 400 BODY_NOT_VALID")
    def test_create_user_missing_fields(self, api_token: str, base_url: str):
        resp = self._post(
            f"{base_url}/user/create",
            headers={"app-id": api_token},
            json_body={"firstName": "OnlyFirstName"},  # нет lastName/email
        )
        assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")


    # ---------------- PARAMS_NOT_VALID ----------------

    @allure.title("GET /user/{bad_id} -> 400 PARAMS_NOT_VALID")
    def test_get_user_bad_id(self, api_token: str, base_url: str):
        bad_id = "123"
        resp = self._get(
            f"{base_url}/user/{bad_id}",
            headers={"app-id": api_token},
        )
        assert_dummyapi_error(resp, 400, "PARAMS_NOT_VALID")


    # ---------------- RESOURCE_NOT_FOUND ----------------

    @allure.title("GET /user/{id} not found -> 404 RESOURCE_NOT_FOUND")
    def test_get_user_not_found(self, api_token: str, base_url: str):
        non_exist_id = "000000000000000000000000"
        resp = self._get(
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
    def test_path_not_found(self, api_token: str, base_url: str):
        resp = self._get(
            f"{base_url}/userzzz",  # путь не существует
            headers={"app-id": api_token},
        )
        assert_dummyapi_error(resp, 404, "PATH_NOT_FOUND")