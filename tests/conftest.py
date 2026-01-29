import os
import pytest
import requests
from pathlib import Path
from dotenv import load_dotenv

from services.users.api_users import UsersAPI
from services.users.endpoints import Endpoints

from services.posts.api_posts import PostsAPI
from services.posts.endpoints import PostEndpoints

from services.comments.api_comments import CommentsAPI
from services.comments.endpoints import CommentEndpoints

DEFAULT_TIMEOUT = 15

dotenv_path = Path(__file__).resolve().parents[1] / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)


# Берёт HOST из .env, гарантирует что он не пустой.
@pytest.fixture(scope="session")
def base_url() -> str:
    host = os.getenv("HOST", "").strip().rstrip("/")
    assert host, f"HOST is not set. Set env var HOST or create {dotenv_path} (see .env)"
    return host


# Берёт API_TOKEN из .env, это app-id для DummyAPI.
@pytest.fixture(scope="session")
def api_token() -> str:
    token = os.getenv("API_TOKEN", "").strip()
    assert token, f"API_TOKEN is not set. Set env var API_TOKEN or create {dotenv_path} (see .env)"
    return token


"""Создаёт requests.Session() и один раз выставляет заголовки. Почему Session — хорошо: 
* соединения переиспользуются (быстрее)
* заголовки не нужно повторять в каждом запросе
*удобно централизованно менять поведение."""
@pytest.fixture(scope="session")
def http(api_token: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "app-id": api_token,
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
    yield session
    session.close()


@pytest.fixture(autouse=True, scope="session")
def env_check(http: requests.Session, base_url: str):
    response = http.get(f"{base_url}/user?limit=1", timeout=DEFAULT_TIMEOUT)
    assert response.status_code == 200, f"Env check failed: {response.status_code} {response.text}"


# ---------- Test data fixtures: create user(s) + auto cleanup ----------

# =======================================================USERS===========================================================
# =======================================================================================================================
# =======================================================USERS===========================================================


@pytest.fixture(scope="session")
def endpoints(base_url: str) -> Endpoints:
    return Endpoints(base_url)


@pytest.fixture(scope="session")
def users_api(http: requests.Session, endpoints: Endpoints) -> UsersAPI:
    return UsersAPI(session=http, endpoints=endpoints, timeout=DEFAULT_TIMEOUT)


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


# =======================================================POSTS===========================================================
# =======================================================================================================================
# =======================================================POSTS===========================================================


@pytest.fixture(scope="session")
def post_endpoints(base_url: str) -> PostEndpoints:
    return PostEndpoints(base_url)


@pytest.fixture(scope="session")
def posts_api(http: requests.Session, post_endpoints: PostEndpoints) -> PostsAPI:
    return PostsAPI(session=http, endpoints=post_endpoints, timeout=DEFAULT_TIMEOUT)


@pytest.fixture
def post_factory(posts_api: PostsAPI, user_factory):
    """
    Фабрика постов на тест + авто-удаление.
    Если owner_id не передан — сама создаст юзера через user_factory.
    """
    created_post_ids: list[str] = []

    def create(owner_id: str | None = None):
        if owner_id is None:
            owner_id, _ = user_factory()

        post_id, post = posts_api.create_post(owner_id=owner_id)
        created_post_ids.append(post_id)
        return post_id, post

    yield create

    for post_id in created_post_ids:
        posts_api.delete_post(post_id, allow_not_found=True)


@pytest.fixture
def created_post(post_factory):
    return post_factory()


#======================================================COMMENTS=========================================================
#=======================================================================================================================
#======================================================COMMENTS=========================================================


@pytest.fixture(scope="session")
def comment_endpoints(base_url: str) -> CommentEndpoints:
    return CommentEndpoints(base_url)


@pytest.fixture(scope="session")
def comments_api(http: requests.Session, comment_endpoints: CommentEndpoints) -> CommentsAPI:
    return CommentsAPI(session=http, endpoints=comment_endpoints, timeout=DEFAULT_TIMEOUT)


@pytest.fixture
def comment_factory(comments_api: CommentsAPI, post_factory, user_factory):
    """
    Фабрика комментариев на тест + авто-удаление.
    Если не передали owner_id/post_id — сама создаст нужные сущности.
    Важно: teardown идёт в правильном порядке (comments -> posts -> users).
    """
    created_comment_ids: list[str] = []

    def create(owner_id: str | None = None, post_id: str | None = None):
        if owner_id is None:
            owner_id, _ = user_factory()
        if post_id is None:
            # гарантирую post от этого owner (чтобы связи были логичные)
            post_id, _ = post_factory(owner_id=owner_id)

        comment_id, comment = comments_api.create_comment(owner_id=owner_id, post_id=post_id)
        created_comment_ids.append(comment_id)
        return comment_id, comment

    yield create

    for cid in created_comment_ids:
        comments_api.delete_comment(cid, allow_not_found=True)


@pytest.fixture
def created_comment(comment_factory):
    return comment_factory()
