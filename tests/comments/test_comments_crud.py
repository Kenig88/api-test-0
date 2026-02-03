import allure
import pytest
from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Comments")
@pytest.mark.smoke
class TestComments(BaseTest):

    @allure.title("Comment flow (CREATE -> LIST by post -> LIST by user -> DELETE -> verify deleted)")
    def test_comment_crud(self, created_user, post_factory, comment_factory):
        user_id, _ = created_user

        with allure.step("PRECONDITION: create post for comment"):
            post_id, _ = post_factory(owner_id=user_id)
            assert post_id

        with allure.step("CREATE: POST /comment/create"):
            comment_id, created = comment_factory(owner_id=user_id, post_id=post_id)
            assert comment_id
            assert created.id == comment_id
            assert created.owner is not None
            assert created.owner.id == user_id
            assert created.post == post_id

        with allure.step("READ: GET /post/{post_id}/comment (comment id is in list)"):
            comments_by_post = self.api_comments.list_comments_by_post(
                post_id=post_id,
                limit=50,
                page=0
            )
            assert comment_id in [c.id for c in comments_by_post]

        with allure.step("READ: GET /user/{user_id}/comment (comment id is in list)"):
            comments_by_user = self.api_comments.list_comments_by_user(
                user_id=user_id,
                limit=50,
                page=0
            )
            assert comment_id in [c.id for c in comments_by_user]

        with allure.step("DELETE: DELETE /comment/{id}"):
            self.api_comments.delete_comment(comment_id)

        with allure.step("VERIFY DELETE: повторный DELETE -> 404 RESOURCE_NOT_FOUND"):
            resp = self.api_comments.delete_comment_response(comment_id)
            assert resp.status_code == 404, resp.text
