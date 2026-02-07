import allure
import pytest
from config.base_test import BaseTest
from utils.assertions import assert_dummyapi_error
from services.comments.comment_payloads import CommentPayloads


@allure.epic("Administration")
@allure.feature("Comments")
@pytest.mark.negative
class TestCommentsNegative(BaseTest):

    # ---------------- APP_ID errors ----------------

    @allure.title("POST /comment/create without app-id -> 403 APP_ID_MISSING")
    def test_create_comment_without_app_id(self, raw_comments, created_user, post_factory, base_url: str):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)

        payload = CommentPayloads.create_comment(owner_id=user_id, post_id=post_id)

        resp = raw_comments.post(
            f"{base_url}/comment/create",
            json_body=payload,  # app-id НЕ передаём
        )
        assert_dummyapi_error(resp, 403, "APP_ID_MISSING")

    @allure.title("POST /comment/create with invalid app-id -> 403 APP_ID_NOT_EXIST")
    def test_create_comment_with_invalid_app_id(self, raw_comments, created_user, post_factory, base_url: str):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)

        payload = CommentPayloads.create_comment(owner_id=user_id, post_id=post_id)

        resp = raw_comments.post(
            f"{base_url}/comment/create",
            headers={"app-id": "invalid-app-id"},
            json_body=payload,
        )
        assert_dummyapi_error(resp, 403, "APP_ID_NOT_EXIST")

    # ---------------- BODY_NOT_VALID ----------------

    @allure.title("POST /comment/create missing owner -> 400 BODY_NOT_VALID")
    def test_create_comment_missing_owner(self, created_user, post_factory):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)

        payload = CommentPayloads.create_comment(owner_id=user_id, post_id=post_id)  # валидная база
        payload.pop("owner")  # ломаем ровно 1 поле

        resp = self.api_comments.create_comment_response(payload=payload)
        assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")

    @allure.title("POST /comment/create missing post -> 400 BODY_NOT_VALID")
    def test_create_comment_missing_post(self, created_user, post_factory):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)

        payload = CommentPayloads.create_comment(owner_id=user_id, post_id=post_id)  # валидная база
        payload.pop("post")  # ломаем ровно 1 поле

        resp = self.api_comments.create_comment_response(payload=payload)
        assert_dummyapi_error(resp, 400, "BODY_NOT_VALID")

    # ---------------- PARAMS_NOT_VALID ----------------

    @allure.title("GET /post/{bad_id}/comment -> 400 PARAMS_NOT_VALID")
    def test_list_comments_by_post_malformed_post_id(self, raw_comments, api_token: str, base_url: str):
        bad_post_id = "123"

        resp = raw_comments.get(
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
    def test_path_not_found(self, raw_comments, api_token: str, base_url: str):
        resp = raw_comments.get(
            f"{base_url}/commentzzz",
            headers={"app-id": api_token},
        )
        assert_dummyapi_error(resp, 404, "PATH_NOT_FOUND")
