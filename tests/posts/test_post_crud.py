import allure
import pytest

from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Posts")
@pytest.mark.smoke
class TestPostsCRUD(BaseTest):

    @allure.title("POST /post/create -> Create new post")
    def test_create_post(self, created_user, post_factory):
        user_id, _ = created_user

        post_id, post = post_factory(owner_id=user_id)

        assert post_id
        assert post.id == post_id
        assert post.owner is not None
        assert post.owner.id == user_id

    @allure.title("GET /post/{id} -> Get post by id")
    def test_get_post_by_id(self, created_user, post_factory):
        user_id, _ = created_user
        post_id, created = post_factory(owner_id=user_id)

        fetched = self.api_posts.get_post_by_id(post_id)

        assert fetched.id == post_id
        assert fetched.text == created.text
        assert fetched.owner is not None
        assert fetched.owner.id == user_id

    @allure.title("PUT /post/{id} -> Update post by id")
    def test_update_post_by_id(self, created_user, post_factory):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)

        update_payload = {
            "text": "Updated post text",
            "likes": 123,
            "tags": ["updated", "qa"]
        }

        updated = self.api_posts.update_post(post_id, update_payload)
        assert updated.id == post_id

        fetched = self.api_posts.get_post_by_id(post_id)
        assert fetched.text == "Updated post text"
        assert fetched.likes == 123
        assert fetched.tags == ["updated", "qa"]
        assert fetched.owner is not None
        assert fetched.owner.id == user_id

    @allure.title("DELETE /post/{id} -> Delete post by id")
    def test_delete_post_by_id(self, created_user, post_factory):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)

        self.api_posts.delete_post(post_id)

        # Проверка удаления: GET должен стать 404
        resp = self.api_posts.get_post_by_id_response(post_id)
        assert resp.status_code == 404, resp.text

    @allure.title("GET /user/{user_id}/post -> List posts by user contains created posts")
    def test_list_posts_by_user_contains_created(self, created_user, post_factory):
        user_id, _ = created_user

        p1_id, _ = post_factory(owner_id=user_id)
        p2_id, _ = post_factory(owner_id=user_id)

        posts = self.api_posts.list_posts_by_user(user_id=user_id, limit=50, page=0)
        ids = [p.id for p in posts]

        assert p1_id in ids
        assert p2_id in ids
