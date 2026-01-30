import allure
import pytest
import requests
from utils.assertions import assert_dummyapi_error
from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Comments")
@pytest.mark.negative
class TestCommentsNegative(BaseTest):

    @allure.title("POST /comment/create without app-id -> 403 APP_ID_MISSING")
    def test_create_comment_without_app_id(self, base_url: str):
        with allure.step("Send POST /comment/create without app-id header"):
            resp = requests.post(
                url=f"{base_url}/comment/create",
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                json={"message": "hello", "owner": "000000000000000000000000", "post": "000000000000000000000000"},
                timeout=15,
            )

        with allure.step("Assert 403 + APP_ID_MISSING"):
            assert_dummyapi_error(resp, 403, "APP_ID_MISSING")

    @allure.title("POST /comment/create with invalid app-id -> 403 APP_ID_NOT_EXIST")
    def test_create_comment_with_invalid_app_id(self, base_url: str):
        with allure.step("Send POST /comment/create with invalid app-id"):
            resp = requests.post(
                url=f"{base_url}/comment/create",
                headers={
                    "app-id": "invalid-app-id",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json={"message": "hello", "owner": "000000000000000000000000", "post": "000000000000000000000000"},
                timeout=15,
            )

        with allure.step("Assert 403 + APP_ID_NOT_EXIST"):
            assert_dummyapi_error(resp, 403, "APP_ID_NOT_EXIST")

    @allure.title("POST /comment/create missing owner -> 400 BODY_NOT_VALID")
    def test_create_comment_missing_owner(self, created_user, post_factory):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)

        with allure.step("Send POST /comment/create missing owner"):
            resp = self.api_comments.create_comment_response(
                payload={"message": "hi", "post": post_id}
            )

        with allure.step("Assert 400 + BODY_NOT_VALID"):
            assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")

    @allure.title("POST /comment/create missing post -> 400 BODY_NOT_VALID")
    def test_create_comment_missing_post(self, created_user):
        user_id, _ = created_user

        with allure.step("Send POST /comment/create missing post"):
            resp = self.api_comments.create_comment_response(
                payload={"message": "hi", "owner": user_id}
            )

        with allure.step("Assert 400 + BODY_NOT_VALID"):
            assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")

    @allure.title("POST /comment/create with non-existent post -> API accepts (200/201) and returns comment")
    def test_create_comment_post_not_found_is_accepted(self, created_user):
        user_id, _ = created_user
        bad_post_id = "000000000000000000000000"

        with allure.step("Send POST /comment/create with non-existent post"):
            resp = self.api_comments.create_comment_response(
                payload={"message": "hi", "owner": user_id, "post": bad_post_id}
            )

        with allure.step("Assert API returns 200/201 (DummyAPI behavior)"):
            assert resp.status_code in (200, 201), resp.text
            body = resp.json()
            assert body.get("id"), body

        # cleanup: удаляем созданный коммент
        comment_id = resp.json().get("id")
        if comment_id:
            self.api_comments.delete_comment(comment_id, allow_not_found=True)

    @allure.title("POST /comment/create with non-existent owner -> 400 BODY_NOT_VALID or 404 RESOURCE_NOT_FOUND")
    def test_create_comment_owner_not_found(self, created_user, post_factory):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)
        bad_user_id = "000000000000000000000000"

        with allure.step("Send POST /comment/create with non-existent owner"):
            resp = self.api_comments.create_comment_response(
                payload={"message": "hi", "owner": bad_user_id, "post": post_id}
            )

        expected_errors = {
            400: "BODY_NOT_VALID",
            404: "RESOURCE_NOT_FOUND",
        }

        err = expected_errors.get(resp.status_code)
        assert err is not None, f"Unexpected status: {resp.status_code} {resp.text}"
        assert_dummyapi_error(resp, resp.status_code, err)

    @allure.title("GET /post/{bad_id}/comment -> 400 PARAMS_NOT_VALID")
    def test_list_comments_by_post_malformed_post_id(self):
        bad_post_id = "123"

        with allure.step(f"Send GET /post/{bad_post_id}/comment"):
            resp = self.api_comments.list_comments_by_post_response(
                post_id=bad_post_id,
                limit=10,
                page=0,
            )

        with allure.step("Assert 400 + PARAMS_NOT_VALID"):
            assert_dummyapi_error(resp, 400, "PARAMS_NOT_VALID")

    @allure.title("DELETE /comment/{id} for non-existent id -> 404 RESOURCE_NOT_FOUND")
    def test_delete_comment_not_found(self):
        non_exist_comment_id = "000000000000000000000000"

        with allure.step(f"Send DELETE /comment/{non_exist_comment_id}"):
            resp = self.api_comments.delete_comment_response(non_exist_comment_id)

        with allure.step("Assert 404 + RESOURCE_NOT_FOUND"):
            assert_dummyapi_error(resp, 404, "RESOURCE_NOT_FOUND")
