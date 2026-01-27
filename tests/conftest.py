import os
from pathlib import Path
import pytest
import requests
from dotenv import load_dotenv
from services.users.api_users import UsersAPI
from services.users.endpoints import Endpoints


DEFAULT_TIMEOUT = 15

dotenv_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=dotenv_path)


@pytest.fixture(scope="session")
def base_url() -> str:
    host = os.getenv("HOST", "").strip().rstrip("/")
    assert host, f"HOST is not set (dotenv: {dotenv_path})"
    return host


@pytest.fixture(scope="session")
def api_token() -> str:
    token = os.getenv("API_TOKEN", "").strip()
    assert token, f"API_TOKEN is not set (dotenv: {dotenv_path})"
    return token


@pytest.fixture(scope="session")
def http(api_token: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "app-id": api_token,
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
    return session


@pytest.fixture(scope="session")
def endpoints(base_url: str) -> Endpoints:
    return Endpoints(base_url)


@pytest.fixture(scope="session")
def users_api(http: requests.Session, endpoints: Endpoints) -> UsersAPI:
    return UsersAPI(session=http, endpoints=endpoints, timeout=DEFAULT_TIMEOUT)


@pytest.fixture(autouse=True, scope="session")
def env_check(http: requests.Session, base_url: str):
    response = http.get(f"{base_url}/user?limit=1", timeout=DEFAULT_TIMEOUT)
    assert response.status_code == 200, f"Env check failed: {response.status_code} {response.text}"


# ---------- Test data fixtures: create user(s) + auto cleanup ----------

@pytest.fixture
def user_factory(users_api: UsersAPI):
    """
    Фабрика пользователей для одного теста.
    Можно создавать 1+ пользователей внутри теста, а после теста все будут удалены.
    """
    created_ids: list[str] = []

    def create():
        user_id, user = users_api.create_user()
        assert user_id
        created_ids.append(user_id)
        return user_id, user

    yield create

    # cleanup после теста (даже если тест упал)
    for user_id in created_ids:
        users_api.delete_user(user_id, allow_not_found=True)


@pytest.fixture
def created_user(user_factory):
    """Один пользователь на тест + авто-удаление после теста."""
    return user_factory()
