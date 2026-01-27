from config.base_test import BaseTest
import pytest
import allure


@allure.epic("Administration")
@allure.feature("Users")
class TestUsers(BaseTest):

    @pytest.mark.regression
    @allure.title("Create new user")
    def test_create_user(self, created_user):
        user_id, user = created_user
        assert user_id
        # если хочешь печать:
        print(user.model_dump_json() if hasattr(user, "model_dump_json") else user.json())

    @pytest.mark.regression
    @allure.title("Get user by id")
    def test_get_user_by_id(self, created_user):
        user_id, created = created_user
        fetched = self.api_users.get_user_by_id(user_id)

        assert fetched.id == user_id
        # более сильная проверка, если поле есть:
        if created.email and fetched.email:
            assert fetched.email == created.email

    @pytest.mark.regression
    @allure.title("Update user by id (PUT)")
    def test_update_user_by_id(self, created_user):
        user_id, _ = created_user

        update_payload = {
            "firstName": "UpdatedName",
            "lastName": "UpdatedLast"
        }

        updated = self.api_users.update_user(user_id, update_payload)
        assert updated.id == user_id

        fetched = self.api_users.get_user_by_id(user_id)
        assert fetched.firstName == "UpdatedName"
        assert fetched.lastName == "UpdatedLast"

    @pytest.mark.regression
    @allure.title("Delete user by id")
    def test_delete_user_by_id(self, created_user):
        user_id, _ = created_user
        self.api_users.delete_user(user_id)
        # проверяем, что юзер реально удалён
        resp = self.api_users.get_user_by_id_response(user_id)
        assert resp.status_code == 404, resp.text
