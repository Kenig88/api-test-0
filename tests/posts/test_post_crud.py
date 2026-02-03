import allure
import pytest
from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Posts")
@pytest.mark.smoke
class TestPosts(BaseTest):

    @allure.title("Post flow (CREATE -> GET by id -> UPDATE -> GET by id -> DELETE -> GET 404)")
    def test_post_crud(self, created_user, post_factory):
        user_id, _ = created_user

        with allure.step("CREATE: POST /post/create"):
            post_id, created = post_factory(owner_id=user_id)
            assert post_id
            assert created.id == post_id
            assert created.owner is not None
            assert created.owner.id == user_id

        with allure.step("READ: GET /post/{id} (check created post)"):
            fetched = self.api_posts.get_post_by_id(post_id)
            assert fetched.id == post_id
            if created.text and fetched.text:
                assert fetched.text == created.text
            assert fetched.owner is not None
            assert fetched.owner.id == user_id

        with allure.step("UPDATE: PUT /post/{id} (change text/likes/tags)"):
            update_payload = {
                "text": "Updated post text",
                "likes": 123,
                "tags": ["updated", "qa"],
                # owner НЕ передаём — по доке его нельзя обновлять
            }
            updated = self.api_posts.update_post(post_id, update_payload)
            assert updated.id == post_id

        with allure.step("READ: GET /post/{id} (check updated fields)"):
            fetched_after_update = self.api_posts.get_post_by_id(post_id)
            assert fetched_after_update.id == post_id
            assert fetched_after_update.text == "Updated post text"
            assert fetched_after_update.likes == 123
            assert fetched_after_update.tags == ["updated", "qa"]
            assert fetched_after_update.owner is not None
            assert fetched_after_update.owner.id == user_id

        with allure.step("DELETE: DELETE /post/{id}"):
            self.api_posts.delete_post(post_id)

        with allure.step("VERIFY DELETE: GET /post/{id} after delete -> 404"):
            resp = self.api_posts.get_post_by_id_response(post_id)
            assert resp.status_code == 404, resp.text