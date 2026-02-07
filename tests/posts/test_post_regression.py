import allure
import pytest
from config.base_test import BaseTest
from services.posts.post_payloads import PostPayloads


@allure.epic("Administration")
@allure.feature("Posts")
@pytest.mark.regression
class TestPosts(BaseTest):

    @allure.title("Create Post -> POST /post/create")
    def test_create_post(self, created_user, post_factory):
        user_id, _ = created_user

        with allure.step("CREATE: create post"):
            post_id, post = post_factory(owner_id=user_id)

            assert post_id
            assert post.id == post_id
            assert post.owner is not None
            assert post.owner.id == user_id

    @allure.title("Get Post by id -> GET /post/{id}")
    def test_get_post_by_id(self, created_user, post_factory):
        user_id, _ = created_user

        with allure.step("PRECONDITION: create post"):
            post_id, created = post_factory(owner_id=user_id)
            assert post_id

        with allure.step("READ: get post by id"):
            fetched = self.api_posts.get_post_by_id(post_id)

            assert fetched.id == post_id
            if created.text and fetched.text:
                assert fetched.text == created.text
            assert fetched.owner is not None
            assert fetched.owner.id == user_id

    @allure.title("Update Post -> PUT /post/{id}")
    def test_update_post(self, created_user, post_factory):
        user_id, _ = created_user

        with allure.step("PRECONDITION: create post"):
            post_id, _ = post_factory(owner_id=user_id)
            assert post_id

        with allure.step("UPDATE: update post fields (text/likes)"):
            update_payload = PostPayloads.update_post(
                text="Updated post text",
                likes=123,
            )
            updated = self.api_posts.update_post(post_id, update_payload)
            assert updated.id == post_id

        with allure.step("READ: get post by id and verify updated fields"):
            fetched = self.api_posts.get_post_by_id(post_id)

            assert fetched.id == post_id
            assert fetched.text == "Updated post text"
            assert fetched.likes == 123
            assert fetched.owner is not None
            assert fetched.owner.id == user_id  # owner нельзя обновлять

    @allure.title("Delete Post -> DELETE /post/{id} (verify GET 404)")
    def test_delete_post(self, created_user, post_factory):
        user_id, _ = created_user

        with allure.step("PRECONDITION: create post"):
            post_id, _ = post_factory(owner_id=user_id)
            assert post_id

        with allure.step("DELETE: delete post by id"):
            deleted_id = self.api_posts.delete_post(post_id)
            assert deleted_id is not None

        with allure.step("VERIFY DELETE: GET /post/{id} after delete -> 404"):
            resp = self.api_posts.get_post_by_id_response(post_id)
            assert resp.status_code == 404, resp.text

    @allure.title("Get Posts List -> GET /post")
    def test_get_list(self):
        with allure.step("READ: list posts"):
            posts = self.api_posts.list_posts(limit=10, page=0)

            assert isinstance(posts, list)
            assert len(posts) > 0
            assert all(p.id for p in posts)

    @allure.title("Get List By User -> GET /user/{user_id}/post (contains created post)")
    def test_get_list_by_user(self, created_user, post_factory):
        user_id, _ = created_user

        with allure.step("PRECONDITION: create post for user"):
            post_id, _ = post_factory(owner_id=user_id)
            assert post_id

        with allure.step("READ: list posts by user and verify id is present"):
            posts = self.api_posts.list_posts_by_user(
                user_id=user_id,
                limit=50,
                page=0
            )
            ids = [p.id for p in posts]
            assert post_id in ids