import allure
import pytest
from config.base_test import BaseTest
from services.posts.post_payloads import PostPayloads


@allure.epic("Administration")
@allure.feature("Posts")
class TestPosts(BaseTest):

    @pytest.mark.regression
    @allure.title("Create new post")
    def test_create_post(self, created_user):
        user_id, _ = created_user
        post_id, post = self.api_posts.create_post(owner_id=user_id)

        assert post_id
        assert post.id == post_id
        assert post.owner is not None
        assert post.owner.id == user_id

    @pytest.mark.regression
    @allure.title("Get post by id")
    def test_get_post_by_id(self, created_user):
        user_id, _ = created_user
        post_id, created = self.api_posts.create_post(owner_id=user_id)

        fetched = self.api_posts.get_post_by_id(post_id)
        assert fetched.id == post_id
        assert fetched.text == created.text

    @pytest.mark.regression
    @allure.title("Update post by id (PUT)")
    def test_update_post_by_id(self, created_user):
        user_id, _ = created_user
        post_id, created = self.api_posts.create_post(owner_id=user_id)

        update_payload = PostPayloads.update_post(
            text="Updated post text",
            likes=123,
            tags=["updated", "qa"]
        )
        updated = self.api_posts.update_post(post_id, update_payload)
        assert updated.id == post_id

        fetched = self.api_posts.get_post_by_id(post_id)
        assert fetched.text == "Updated post text"
        assert fetched.likes == 123
        assert fetched.tags == ["updated", "qa"]

        # owner нельзя обновлять, но он должен остаться прежним
        assert fetched.owner is not None
        assert fetched.owner.id == user_id

    @pytest.mark.regression
    @allure.title("Delete post by id")
    def test_delete_post_by_id(self, created_user):
        user_id, _ = created_user
        post_id, _ = self.api_posts.create_post(owner_id=user_id)

        self.api_posts.delete_post(post_id)

        resp = self.api_posts.get_post_by_id_response(post_id)
        assert resp.status_code == 404, resp.text

    @pytest.mark.regression
    @allure.title("List posts by user contains created posts")
    def test_list_posts_by_user_contains_created(self, created_user, post_factory):
        user_id, _ = created_user

        p1_id, _ = post_factory(owner_id=user_id)
        p2_id, _ = post_factory(owner_id=user_id)

        posts = self.api_posts.list_posts_by_user(user_id=user_id, limit=50, page=0)
        ids = [p.id for p in posts]

        assert p1_id in ids
        assert p2_id in ids
