import allure
import pytest
from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Comments")
class TestComments(BaseTest):

    @pytest.mark.regression
    @allure.title("Create new comment")
    def test_create_comment(self, created_user):
        user_id, _ = created_user
        post_id, _ = self.api_posts.create_post(owner_id=user_id)

        comment_id, comment = self.api_comments.create_comment(owner_id=user_id, post_id=post_id)
        assert comment_id
        assert comment.id == comment_id

        assert comment.owner is not None
        assert comment.owner.id == user_id
        assert comment.post == post_id

    @pytest.mark.regression
    @allure.title("List comments by post contains created comment")
    def test_list_comments_by_post_contains_created(self, created_user):
        user_id, _ = created_user
        post_id, _ = self.api_posts.create_post(owner_id=user_id)
        comment_id, _ = self.api_comments.create_comment(owner_id=user_id, post_id=post_id)

        comments = self.api_comments.list_comments_by_post(post_id=post_id, limit=50, page=0)
        ids = [c.id for c in comments]
        assert comment_id in ids

    @pytest.mark.regression
    @allure.title("Delete comment by id")
    def test_delete_comment(self, created_user):
        user_id, _ = created_user
        post_id, _ = self.api_posts.create_post(owner_id=user_id)
        comment_id, _ = self.api_comments.create_comment(owner_id=user_id, post_id=post_id)

        self.api_comments.delete_comment(comment_id)

        # У comment controller нет GET /comment/:id, поэтому проверяем косвенно:
        # повторный DELETE должен дать 404 (обычно RESOURCE_NOT_FOUND)
        resp = self.api_comments.delete_comment_response(comment_id)
        assert resp.status_code == 404
