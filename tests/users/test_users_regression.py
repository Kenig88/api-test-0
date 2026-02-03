from config.base_test import BaseTest
import pytest
import allure


@allure.epic("Administration")
@allure.feature("Users")
@pytest.mark.regression
class TestUsers(BaseTest):

    @allure.title("Create User -> POST /user/create")
    def test_create_user(self, created_user):
        with allure.step("CREATE: create user"):
            user_id, user = created_user
            assert user_id
            assert user.firstName
            assert user.lastName
            assert user.email
            # если хочешь печать:
            print(user.model_dump_json() if hasattr(user, "model_dump_json") else user.json())

    @allure.title("Get User by id -> GET /user/{id}")
    def test_get_user_by_id(self, created_user):
        with allure.step("PRECONDITION: create user"):
            user_id, created = created_user
            assert user_id

        with allure.step("READ: get user by id and verify fields"):
            fetched = self.api_users.get_user_by_id(user_id)

            assert fetched.id == user_id
            if created.email and fetched.email:
                assert fetched.email == created.email

    @allure.title("Get Users List -> GET /user")
    def test_get_users_list(self):
        with allure.step("READ: list users"):
            users = self.api_users.list_users(limit=10, page=0)

            assert isinstance(users, list)
            assert len(users) > 0
            assert all(u.id for u in users)

    @allure.title("Update User by id -> PUT /user/{id}")
    def test_update_user_by_id(self, created_user):
        with allure.step("PRECONDITION: create user"):
            user_id, created = created_user
            assert user_id

        with allure.step("UPDATE: update user fields (firstName/lastName)"):
            update_payload = {
                "firstName": "UpdatedName",
                "lastName": "UpdatedLast",
            }
            updated = self.api_users.update_user(user_id, update_payload)
            assert updated.id == user_id

        with allure.step("READ: get user by id and verify updated fields"):
            fetched = self.api_users.get_user_by_id(user_id)

            assert fetched.firstName == "UpdatedName"
            assert fetched.lastName == "UpdatedLast"

            # email по доке нельзя обновлять — проверим, что остался прежним (если есть)
            if created.email and fetched.email:
                assert fetched.email == created.email

    @allure.title("Delete User -> DELETE /user/{id} (verify deleted)")
    def test_delete_user_by_id(self, created_user):
        with allure.step("PRECONDITION: create user"):
            user_id, _ = created_user
            assert user_id

        with allure.step("DELETE: delete user by id"):
            self.api_users.delete_user(user_id)

        with allure.step("VERIFY DELETE: GET /user/{id} -> 404"):
            resp = self.api_users.get_user_by_id_response(user_id)
            assert resp.status_code == 404, resp.text
