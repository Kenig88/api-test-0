import pytest
import allure
from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Users")
@pytest.mark.regression
class TestUsers(BaseTest):

    @allure.title("Create User -> POST /user/create")
    def test_create_user(self, created_user):
        user_id, user = created_user

        with allure.step("ASSERT: verify created user"):
            assert user_id
            assert user.id == user_id
            assert user.firstName
            assert user.lastName
            assert user.email

    @allure.title("Get User by id -> GET /user/{id}")
    def test_get_user_by_id(self, created_user):
        with allure.step("PRECONDITION: create user"):
            user_id, created = created_user
            assert user_id

        with allure.step("READ: get user by id"):
            fetched = self.api_users.get_user_by_id(user_id)

        with allure.step("ASSERT: verify fields"):
            assert fetched.id == user_id
            if created.email and fetched.email:
                assert fetched.email == created.email

    @allure.title("Get Users List -> GET /user")
    def test_get_users_list(self):
        limit = 10
        page = 0

        with allure.step("READ: list users"):
            users = self.api_users.list_users(limit=limit, page=page)

        with allure.step("ASSERT: verify list"):
            assert isinstance(users, list)
            assert len(users) <= limit  # контракт пагинации

            if users:  # если список непустой — проверяем структуру
                assert all(u.id for u in users)

    @allure.title("Update User by id -> PUT /user/{id}")
    def test_update_user_by_id(self, created_user):
        with allure.step("PRECONDITION: create user"):
            user_id, created = created_user
            assert user_id

        with allure.step("UPDATE: update user fields (firstName/lastName)"):
            update_payload = {"firstName": "UpdatedName", "lastName": "UpdatedLast"}
            updated = self.api_users.update_user(user_id, update_payload)

            assert updated.id == user_id
            assert updated.firstName == "UpdatedName"
            assert updated.lastName == "UpdatedLast"

            # email по доке нельзя обновлять — проверим, что остался прежний (если есть)
            if created.email and updated.email:
                assert updated.email == created.email

        with allure.step("READ: get user by id and verify updated fields"):
            fetched = self.api_users.get_user_by_id(user_id)

            assert fetched.firstName == "UpdatedName"
            assert fetched.lastName == "UpdatedLast"
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

            try:
                body = resp.json()
            except Exception:
                body = resp.text

            assert resp.status_code == 404, body