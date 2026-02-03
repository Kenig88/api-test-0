import allure
import pytest
from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Comments")
@pytest.mark.regression
class TestComments(BaseTest):

    @pytest.mark.regression
    @allure.title("Create Comment -> POST /comment/create")
    def test_create_comment(self, created_user, post_factory, comment_factory):
        user_id, _ = created_user

        with allure.step("PRECONDITION: create post"):
            post_id, _ = post_factory(owner_id=user_id)
            assert post_id

        with allure.step("CREATE: create comment for post"):
            comment_id, comment = comment_factory(owner_id=user_id, post_id=post_id)
            assert comment_id
            assert comment.id == comment_id
            assert comment.message  # message обязателен в create
            assert comment.owner is not None
            assert comment.owner.id == user_id
            assert comment.post == post_id

    @pytest.mark.regression
    @allure.title("Get Comments List -> GET /comment")
    def test_get_comments_list(self):
        with allure.step("READ: list comments"):
            comments = self.api_comments.list_comments(limit=10, page=0)
            assert isinstance(comments, list)
            assert len(comments) > 0
            # минимальные sanity-checks по модели превью
            assert all(c.id for c in comments)

    @pytest.mark.regression
    @allure.title("Get Comments By Post -> GET /post/{post_id}/comment")
    def test_get_list_comments_by_post(self, created_user, post_factory, comment_factory):
        user_id, _ = created_user

        with allure.step("PRECONDITION: create post"):
            post_id, _ = post_factory(owner_id=user_id)
            assert post_id

        with allure.step("CREATE: create comment for post"):
            comment_id, _ = comment_factory(owner_id=user_id, post_id=post_id)
            assert comment_id

        with allure.step("READ: list comments by post and verify created id is present"):
            comments = self.api_comments.list_comments_by_post(post_id=post_id, limit=50, page=0)
            assert comment_id in [c.id for c in comments]

    @pytest.mark.regression
    @allure.title("Get Comments By User -> GET /user/{user_id}/comment")
    def test_get_list_comments_by_user(self, created_user, post_factory, comment_factory):
        user_id, _ = created_user

        with allure.step("PRECONDITION: create post"):
            post_id, _ = post_factory(owner_id=user_id)
            assert post_id

        with allure.step("CREATE: create comment for user"):
            comment_id, _ = comment_factory(owner_id=user_id, post_id=post_id)
            assert comment_id

        with allure.step("READ: list comments by user and verify created id is present"):
            comments = self.api_comments.list_comments_by_user(user_id=user_id, limit=50, page=0)
            assert comment_id in [c.id for c in comments]

    @pytest.mark.regression
    @allure.title("Delete Comment -> DELETE /comment/{id} (verify deleted)")
    def test_delete_comment(self, created_user, post_factory, comment_factory):
        user_id, _ = created_user

        with allure.step("PRECONDITION: create post"):
            post_id, _ = post_factory(owner_id=user_id)
            assert post_id

        with allure.step("CREATE: create comment"):
            comment_id, _ = comment_factory(owner_id=user_id, post_id=post_id)
            assert comment_id

        with allure.step("DELETE: delete comment by id"):
            deleted_id = self.api_comments.delete_comment(comment_id)
            # delete в доке возвращает строку id — у тебя это уже обработано в API
            assert deleted_id is not None

        with allure.step("VERIFY DELETE: повторный DELETE -> 404"):
            resp = self.api_comments.delete_comment_response(comment_id)
            assert resp.status_code == 404, resp.text
