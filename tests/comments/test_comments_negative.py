import allure
import pytest
import requests
from config.base_test import BaseTest
from utils.assertions import assert_dummyapi_error


@allure.epic("Administration")
@allure.feature("Comments")
@pytest.mark.negative
class TestCommentsNegative(BaseTest):
    TIMEOUT = 15

    def _get(self, url: str, headers: dict | None = None) -> requests.Response:
        h = {"Accept": "application/json"}
        if headers:
            h.update(headers)
        resp = requests.get(url, headers=h, timeout=self.TIMEOUT)
        self.api_comments.attach_response_safe(resp)
        return resp

    def _post(self, url: str, headers: dict | None = None, json_body: dict | None = None) -> requests.Response:
        h = {"Accept": "application/json", "Content-Type": "application/json"}
        if headers:
            h.update(headers)
        resp = requests.post(url, headers=h, json=json_body, timeout=self.TIMEOUT)
        self.api_comments.attach_response_safe(resp)
        return resp

    # ---------------- APP_ID errors ----------------

    @allure.title("POST /comment/create without app-id -> 403 APP_ID_MISSING")
    def test_create_comment_without_app_id(self, base_url: str):
        resp = self._post(
            f"{base_url}/comment/create",
            json_body={
                "message": "hello",
                "owner": "000000000000000000000000",
                "post": "000000000000000000000000",
            },
        )
        assert_dummyapi_error(resp, 403, "APP_ID_MISSING")

    @allure.title("POST /comment/create with invalid app-id -> 403 APP_ID_NOT_EXIST")
    def test_create_comment_with_invalid_app_id(self, base_url: str):
        resp = self._post(
            f"{base_url}/comment/create",
            headers={"app-id": "invalid-app-id"},
            json_body={
                "message": "hello",
                "owner": "000000000000000000000000",
                "post": "000000000000000000000000",
            },
        )
        assert_dummyapi_error(resp, 403, "APP_ID_NOT_EXIST")

    # ---------------- BODY_NOT_VALID ----------------

    @allure.title("POST /comment/create missing owner -> 400 BODY_NOT_VALID")
    def test_create_comment_missing_owner(self, created_user, post_factory):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)

        resp = self.api_comments.create_comment_response(
            payload={"message": "hi", "post": post_id}  # owner отсутствует
        )
        assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")

    @allure.title("POST /comment/create missing post -> 400 BODY_NOT_VALID")
    def test_create_comment_missing_post(self, created_user):
        user_id, _ = created_user

        resp = self.api_comments.create_comment_response(
            payload={"message": "hi", "owner": user_id}  # post отсутствует
        )
        assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")

    # ---------------- PARAMS_NOT_VALID ----------------

    @allure.title("GET /post/{bad_id}/comment -> 400 PARAMS_NOT_VALID")
    def test_list_comments_by_post_malformed_post_id(self, api_token: str, base_url: str):
        bad_post_id = "123"

        resp = self._get(
            f"{base_url}/post/{bad_post_id}/comment?limit=10&page=0",
            headers={"app-id": api_token},
        )
        assert_dummyapi_error(resp, 400, "PARAMS_NOT_VALID")

    # ---------------- RESOURCE_NOT_FOUND ----------------

    @allure.title("DELETE /comment/{id} for non-existent id -> 404 RESOURCE_NOT_FOUND")
    def test_delete_comment_not_found(self):
        non_exist_comment_id = "000000000000000000000000"
        resp = self.api_comments.delete_comment_response(non_exist_comment_id)
        assert_dummyapi_error(resp, 404, "RESOURCE_NOT_FOUND")

    # ---------------- PATH_NOT_FOUND ----------------

    @allure.title("GET wrong path -> 404 PATH_NOT_FOUND")
    def test_path_not_found(self, api_token: str, base_url: str):
        resp = self._get(
            f"{base_url}/commentzzz",
            headers={"app-id": api_token},
        )
        assert_dummyapi_error(resp, 404, "PATH_NOT_FOUND")
