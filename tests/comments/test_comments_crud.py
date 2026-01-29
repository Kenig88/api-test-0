import allure
import pytest

from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Comments")
@pytest.mark.regression
class TestCommentsCRUD(BaseTest):

    @allure.title("POST /comment/create -> Create new comment")
    def test_create_comment(self, created_user, post_factory, comment_factory):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)

        comment_id, comment = comment_factory(owner_id=user_id, post_id=post_id)

        assert comment_id
        assert comment.id == comment_id

        assert comment.owner is not None
        assert comment.owner.id == user_id
        assert comment.post == post_id

    @allure.title("GET /post/{post_id}/comment -> Read: list comments by post contains created comment")
    def test_read_comment_via_list_by_post(self, created_user, post_factory, comment_factory):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)

        comment_id, created = comment_factory(owner_id=user_id, post_id=post_id)

        comments = self.api_comments.list_comments_by_post(post_id=post_id, limit=50, page=0)
        ids = [c.id for c in comments]

        assert comment_id in ids

        # чуть сильнее: найдём этот comment и проверим message
        found = next((c for c in comments if c.id == comment_id), None)
        assert found is not None
        assert found.message == created.message

    @allure.title("GET /user/{user_id}/comment -> List comments by user contains created comment")
    def test_list_comments_by_user_contains_created(self, created_user, post_factory, comment_factory):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)

        comment_id, _ = comment_factory(owner_id=user_id, post_id=post_id)

        comments = self.api_comments.list_comments_by_user(user_id=user_id, limit=50, page=0)
        ids = [c.id for c in comments]

        assert comment_id in ids

    @allure.title("DELETE /comment/{id} -> Delete comment by id")
    def test_delete_comment_by_id(self, created_user, post_factory, comment_factory):
        user_id, _ = created_user
        post_id, _ = post_factory(owner_id=user_id)

        comment_id, _ = comment_factory(owner_id=user_id, post_id=post_id)

        self.api_comments.delete_comment(comment_id)

        # У DummyAPI нет GET /comment/{id}. Проверяем косвенно:
        # повторный DELETE обычно возвращает 404 RESOURCE_NOT_FOUND
        resp = self.api_comments.delete_comment_response(comment_id)
        assert resp.status_code == 404, resp.text
