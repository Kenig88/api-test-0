import allure
import pytest
import requests
from utils.assertions import assert_dummyapi_error
from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Posts")
@pytest.mark.negative
@pytest.mark.regression
class TestPostsNegative(BaseTest):

    @allure.title("POST /post/create without app-id -> 403 APP_ID_MISSING")
    def test_create_post_without_app_id(self, base_url: str):
        with allure.step("Send POST /post/create without app-id header"):
            resp = requests.post(
                url=f"{base_url}/post/create",
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                json={"text": "Hello world", "image": "https://example.com/1.jpg", "likes": 0, "tags": ["qa"], "owner": "000000000000000000000000"},
                timeout=15,
            )

        with allure.step("Assert 403 + APP_ID_MISSING"):
            assert_dummyapi_error(resp, 403, "APP_ID_MISSING")

    @allure.title("POST /post/create with invalid app-id -> 403 APP_ID_NOT_EXIST")
    def test_create_post_with_invalid_app_id(self, base_url: str):
        with allure.step("Send POST /post/create with invalid app-id"):
            resp = requests.post(
                url=f"{base_url}/post/create",
                headers={
                    "app-id": "invalid-app-id",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json={"text": "Hello world", "image": "https://example.com/1.jpg", "likes": 0, "tags": ["qa"], "owner": "000000000000000000000000"},
                timeout=15,
            )

        with allure.step("Assert 403 + APP_ID_NOT_EXIST"):
            assert_dummyapi_error(resp, 403, "APP_ID_NOT_EXIST")

    @allure.title("POST /post/create without owner -> 400 BODY_NOT_VALID")
    def test_create_post_missing_owner(self):
        with allure.step("Send POST /post/create missing owner"):
            resp = self.api_posts.create_post_response(
                payload={"text": "Hello world", "image": "https://example.com/1.jpg", "likes": 0, "tags": ["qa"]}
            )

        with allure.step("Assert 400 + BODY_NOT_VALID"):
            assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")

    @allure.title("GET /post/{bad_id} -> 400 PARAMS_NOT_VALID")
    def test_get_post_with_malformed_id(self):
        bad_id = "123"
        with allure.step(f"Send GET /post/{bad_id}"):
            resp = self.api_posts.get_post_by_id_response(bad_id)

        with allure.step("Assert 400 + PARAMS_NOT_VALID"):
            assert_dummyapi_error(resp, 400, "PARAMS_NOT_VALID")

    @allure.title("DELETE /post/{id} for non-existent id -> 404 RESOURCE_NOT_FOUND")
    def test_delete_post_not_found(self):
        non_exist_id = "000000000000000000000000"
        with allure.step(f"Send DELETE /post/{non_exist_id}"):
            resp = self.api_posts.delete_post_response(non_exist_id)

        with allure.step("Assert 404 + RESOURCE_NOT_FOUND"):
            assert_dummyapi_error(resp, 404, "RESOURCE_NOT_FOUND")

    @allure.title("PUT /post/{id}: attempt to update owner -> should be 400 or ignored")
    def test_update_post_owner_forbidden_or_ignored(self, created_user, post_factory):
        user_id, _ = created_user
        post_id, created = post_factory(owner_id=user_id)
        old_owner_id = created.owner.id if created.owner else user_id

        with allure.step("Try to update forbidden field: owner"):
            resp = self.api_posts.update_post_response(
                post_id=post_id,
                payload={"owner": "000000000000000000000000"}
            )

        with allure.step("If API rejects -> expect 400 BODY_NOT_VALID"):
            if resp.status_code == 400:
                assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")
                return

        with allure.step("If API returns 200 -> verify owner did NOT change"):
            assert resp.status_code == 200, resp.text
            fetched = self.api_posts.get_post_by_id(post_id)

            assert fetched.owner is not None
            assert fetched.owner.id == old_owner_id
