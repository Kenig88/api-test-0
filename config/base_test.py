import pytest
from services.users.api_users import UsersAPI


class BaseTest:
    api_users: UsersAPI

    @pytest.fixture(autouse=True)
    def _init_clients(self, users_api):
        self.api_users = users_api

