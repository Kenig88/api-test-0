import allure
import pytest
import requests
from config.base_test import BaseTest


def assert_dummyapi_error(resp: requests.Response, expected_status: int, expected_error: str):
    """
    DummyAPI обычно возвращает JSON вида: {"error": "...", ...}
    """
    assert resp.status_code == expected_status, f"{resp.status_code} {resp.text}"

    try:
        body = resp.json()
    except Exception as e:
        raise AssertionError(f"Response is not JSON: {resp.text}") from e

    assert body.get("error") == expected_error, body
    return body


@allure.epic("Administration")
@allure.feature("Users")
@pytest.mark.negative
@pytest.mark.regression
class TestUsersNegative(BaseTest):

    @allure.title("GET without app-id -> 403 APP_ID_MISSING")
    def test_get_without_app_id(self, base_url: str):
        with allure.step("Send GET /user?limit=1 without app-id header"):
            resp = requests.get(
                url=f"{base_url}/user?limit=1",
                headers={"Accept": "application/json"},  # app-id намеренно отсутствует
                timeout=15,
            )

        with allure.step("Assert 403 + APP_ID_MISSING"):
            assert_dummyapi_error(resp, 403, "APP_ID_MISSING")

    @allure.title("GET with invalid app-id -> 403 APP_ID_NOT_EXIST")
    def test_get_with_invalid_app_id(self, base_url: str):
        with allure.step("Send GET /user?limit=1 with invalid app-id"):
            resp = requests.get(
                url=f"{base_url}/user?limit=1",
                headers={
                    "app-id": "invalid-app-id",
                    "Accept": "application/json",
                },
                timeout=15,
            )

        with allure.step("Assert 403 + APP_ID_NOT_EXIST"):
            assert_dummyapi_error(resp, 403, "APP_ID_NOT_EXIST")

    @allure.title("POST /user/create with missing required fields -> 400 BODY_NOT_VALID")
    def test_create_user_missing_required_fields(self, api_token: str, base_url: str):
        with allure.step("Send POST /user/create with invalid body (missing fields)"):
            resp = requests.post(
                url=f"{base_url}/user/create",
                headers={
                    "app-id": api_token,
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json={"firstName": "OnlyFirstName"},  # lastName/email отсутствуют
                timeout=15,
            )

        with allure.step("Assert 400 + BODY_NOT_VALID"):
            assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")

    @allure.title("GET /user/{bad_id} -> 400 PARAMS_NOT_VALID")
    def test_get_user_with_malformed_id(self, api_token: str, base_url: str):
        bad_id = "123"  # слишком короткий / невалидный формат
        with allure.step(f"Send GET /user/{bad_id}"):
            resp = requests.get(
                url=f"{base_url}/user/{bad_id}",
                headers={"app-id": api_token, "Accept": "application/json"},
                timeout=15,
            )

        with allure.step("Assert 400 + PARAMS_NOT_VALID"):
            assert_dummyapi_error(resp, 400, "PARAMS_NOT_VALID")

    @allure.title("PUT /user/{id}: attempt to update email -> should not change email (400 or 200 but unchanged)")
    def test_update_user_email_forbidden_or_ignored(self, user_factory):
        with allure.step("Create user (precondition)"):
            user_id, created = user_factory()
            old_email = created.email

        with allure.step("Try to update forbidden field: email"):
            resp = self.api_users.update_user_response(
                user_id=user_id,
                payload={"email": "new_email@example.com"},
            )

        with allure.step("If API rejects -> expect 400 BODY_NOT_VALID"):
            if resp.status_code == 400:
                assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")
                return

        with allure.step("If API returns 200 -> verify email did NOT change"):
            assert resp.status_code == 200, resp.text
            fetched = self.api_users.get_user_by_id(user_id)
            assert fetched.email == old_email

    @allure.title("DELETE /user/{id} for non-existent id -> 404 RESOURCE_NOT_FOUND")
    def test_delete_user_not_found(self):
        non_exist_id = "000000000000000000000000"

        with allure.step(f"Send DELETE /user/{non_exist_id}"):
            resp = self.api_users.delete_user_response(non_exist_id)

        with allure.step("Assert 404 + RESOURCE_NOT_FOUND"):
            assert_dummyapi_error(resp, 404, "RESOURCE_NOT_FOUND")
