import allure
import pytest
import requests
from config.base_test import BaseTest
from utils.assertions import assert_dummyapi_error


@allure.epic("Administration")
@allure.feature("Posts")
@pytest.mark.negative
class TestPostsNegative(BaseTest):
    TIMEOUT = 15

    def _get(self, url: str, headers: dict | None = None) -> requests.Response:
        h = {"Accept": "application/json"}
        if headers:
            h.update(headers)
        resp = requests.get(url, headers=h, timeout=self.TIMEOUT)
        self.api_posts.attach_response_safe(resp)
        return resp

    def _post(self, url: str, headers: dict | None = None, json_body: dict | None = None) -> requests.Response:
        h = {"Accept": "application/json", "Content-Type": "application/json"}
        if headers:
            h.update(headers)
        resp = requests.post(url, headers=h, json=json_body, timeout=self.TIMEOUT)
        self.api_posts.attach_response_safe(resp)
        return resp


    # ---------------- APP_ID errors ----------------

    @allure.title("POST /post/create without app-id -> 403 APP_ID_MISSING")
    def test_create_post_without_app_id(self, base_url: str):
        resp = self._post(
            f"{base_url}/post/create",
            json_body={
                "text": "Hello world",
                "image": "https://example.com/1.jpg",
                "likes": 0,
                "tags": ["qa"],
                "owner": "000000000000000000000000",
            },
        )
        assert_dummyapi_error(resp, 403, "APP_ID_MISSING")

    @allure.title("POST /post/create with invalid app-id -> 403 APP_ID_NOT_EXIST")
    def test_create_post_with_invalid_app_id(self, base_url: str):
        resp = self._post(
            f"{base_url}/post/create",
            headers={"app-id": "invalid-app-id"},
            json_body={
                "text": "Hello world",
                "image": "https://example.com/1.jpg",
                "likes": 0,
                "tags": ["qa"],
                "owner": "000000000000000000000000",
            },
        )
        assert_dummyapi_error(resp, 403, "APP_ID_NOT_EXIST")


    # ---------------- BODY_NOT_VALID ----------------

    @allure.title("POST /post/create without owner -> 400 BODY_NOT_VALID")
    def test_create_post_missing_owner(self):
        resp = self.api_posts.create_post_response(
            payload={
                "text": "Hello world",
                "image": "https://example.com/1.jpg",
                "likes": 0,
                "tags": ["qa"],
                # owner отсутствует
            }
        )
        assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")

    @allure.title("POST /post/create without text -> 400 BODY_NOT_VALID")
    def test_create_post_missing_text(self):
        resp = self.api_posts.create_post_response(
            payload={
                # text отсутствует
                "image": "https://example.com/1.jpg",
                "likes": 0,
                "tags": ["qa"],
                "owner": "000000000000000000000000",
            }
        )
        assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")


    # ---------------- PARAMS_NOT_VALID ----------------

    @allure.title("GET /post/{bad_id} -> 400 PARAMS_NOT_VALID")
    def test_get_post_with_malformed_id(self):
        bad_id = "123"
        resp = self.api_posts.get_post_by_id_response(bad_id)
        assert_dummyapi_error(resp, 400, "PARAMS_NOT_VALID")


    # ---------------- RESOURCE_NOT_FOUND ----------------

    @allure.title("GET /post/{id} for non-existent id -> 404 RESOURCE_NOT_FOUND")
    def test_get_post_not_found(self):
        non_exist_id = "000000000000000000000000"
        resp = self.api_posts.get_post_by_id_response(non_exist_id)
        assert_dummyapi_error(resp, 404, "RESOURCE_NOT_FOUND")

    @allure.title("DELETE /post/{id} for non-existent id -> 404 RESOURCE_NOT_FOUND")
    def test_delete_post_not_found(self):
        non_exist_id = "000000000000000000000000"
        resp = self.api_posts.delete_post_response(non_exist_id)
        assert_dummyapi_error(resp, 404, "RESOURCE_NOT_FOUND")


    # ---------------- PATH_NOT_FOUND ----------------

    @allure.title("GET wrong path -> 404 PATH_NOT_FOUND")
    def test_path_not_found(self, api_token: str, base_url: str):
        resp = self._get(
            f"{base_url}/postzzz",
            headers={"app-id": api_token},
        )
        assert_dummyapi_error(resp, 404, "PATH_NOT_FOUND")