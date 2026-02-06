from config.base_test import BaseTest
import pytest
import allure


@allure.epic("Administration")
@allure.feature("Users")
@pytest.mark.smoke
class TestUsers(BaseTest):

    @allure.title("User flow (CREATE -> GET by id -> UPDATE -> GET by id -> DELETE -> GET 404)")
    def test_user_crud(self, user_factory):

        with allure.step("CREATE: POST /user/create"):
            user_id, created = user_factory()
            assert user_id

        with allure.step("READ: GET /user/{id} (check created user)"):
            fetched = self.api_users.get_user_by_id(user_id)
            assert fetched.id == user_id
            if created.email and fetched.email:
                assert fetched.email == created.email

        with allure.step("UPDATE: PUT /user/{id} (change firstName/lastName)"):
            update_payload = {"firstName": "UpdatedName", "lastName": "UpdatedLast"}
            updated = self.api_users.update_user(user_id, update_payload)
            assert updated.id == user_id

        with allure.step("READ: GET /user/{id} (check updated fields)"):
            fetched_after_update = self.api_users.get_user_by_id(user_id)
            assert fetched_after_update.id == user_id
            assert fetched_after_update.firstName == "UpdatedName"
            assert fetched_after_update.lastName == "UpdatedLast"

        with allure.step("DELETE: DELETE /user/{id}"):
            self.api_users.delete_user(user_id)

        with allure.step("VERIFY DELETE: GET /user/{id} after delete -> 404"):
            resp = self.api_users.get_user_by_id_response(user_id)
            assert resp.status_code == 404, resp.text