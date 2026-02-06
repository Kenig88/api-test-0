import os  # работа с переменными окружения (ENV), например HOST и API_TOKEN
import pytest  # pytest: фикстуры, тесты, ассерты
import requests  # HTTP-клиент (мы будем делать запросы в API)
from pathlib import Path  # удобная работа с путями к файлам
from dotenv import load_dotenv  # загрузка переменных из .env файла в окружение

# Импортируем API-клиенты и классы эндпоинтов (урлы/роуты)
from services.users.api_users import UsersAPI
from services.users.user_endpoints import UserEndpoints
from services.posts.api_posts import PostsAPI
from services.posts.post_endpoints import PostEndpoints
from services.comments.api_comments import CommentsAPI
from services.comments.comment_endpoints import CommentEndpoints

DEFAULT_TIMEOUT = 15  # таймаут для HTTP-запросов (сек), чтобы тесты не висли бесконечно

# ---------- Загрузка переменных окружения из .env ----------
# Ищем файл .env на уровень выше (parents[1]) относительно текущего файла (обычно conftest.py).
dotenv_path = Path(__file__).resolve().parents[1] / ".env"

# Если .env существует — загружаем из него переменные окружения (HOST, API_TOKEN и т.д.)
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)


# ---------- Базовые фикстуры окружения (HOST / TOKEN / HTTP session) ----------

@pytest.fixture(scope="session")
def base_url() -> str:
    """
    Берём HOST из окружения и приводим к аккуратному виду:
    - strip() убирает пробелы
    - rstrip("/") убирает завершающий слэш, чтобы не получилось // в URL
    scope="session": создаётся один раз на всю тестовую сессию (быстрее).
    """
    host = os.getenv("HOST", "").strip().rstrip("/")
    # assert здесь — быстрый и понятный фейл, если переменная не задана
    assert host, f"HOST is not set. Set env var HOST or create {dotenv_path} (see .env)"
    return host


@pytest.fixture(scope="session")
def api_token() -> str:
    """
    Берём API_TOKEN (у DummyAPI это app-id).
    Если токена нет — падаем сразу, чтобы не бегать тестами впустую.
    """
    token = os.getenv("API_TOKEN", "").strip()
    assert token, f"API_TOKEN is not set. Set env var API_TOKEN or create {dotenv_path} (see .env)"
    return token


# Почему requests.Session — хорошо:
# 1) соединения переиспользуются (быстрее, меньше накладных расходов)
# 2) заголовки задаём один раз, не повторяем в каждом запросе
# 3) можно централизованно менять поведение (ретраи/прокси/адаптеры и т.д.)
@pytest.fixture(scope="session")
def http(api_token: str) -> requests.Session:
    """
    Создаём одну HTTP-сессию на всю тестовую сессию (scope="session").
    В неё сразу добавляем заголовки, которые нужны для каждого запроса.
    """
    session = requests.Session()

    # headers.update добавляет дефолтные заголовки ко всем запросам этой session
    session.headers.update({
        "app-id": api_token,             # авторизация/идентификатор приложения для API
        "Accept": "application/json",    # ожидаем ответ в JSON
        "Content-Type": "application/json",  # обычно нужен для POST/PUT с JSON
    })

    # yield в фикстуре означает:
    # - всё до yield выполняется ДО тестов
    # - всё после yield выполняется ПОСЛЕ тестов (teardown/cleanup)
    yield session

    # закрываем сессию (освобождаем ресурсы, соединения)
    session.close()


@pytest.fixture(autouse=True, scope="session")
def env_check(http: requests.Session, base_url: str):
    """
    Проверка окружения перед запуском всех тестов.

    autouse=True + scope="session":
    - pytest выполнит эту фикстуру автоматически
    - один раз за сессию
    - если окружение/токен/host неверные — тесты не будут зря выполняться
    """
    response = http.get(f"{base_url}/user?limit=1", timeout=DEFAULT_TIMEOUT)
    assert response.status_code == 200, f"Env check failed: {response.status_code} {response.text}"


# =======================================================USERS==========================================================
# ======================================================================================================================
# =======================================================USERS==========================================================


@pytest.fixture(scope="session")
def user_endpoints(base_url: str) -> UserEndpoints:
    """
    Создаём объект, который знает URL'ы юзер-эндпоинтов.
    Обычно внутри: /user, /user/{id}, и т.п.
    """
    return UserEndpoints(base_url)


@pytest.fixture(scope="session")
def users_api(http: requests.Session, user_endpoints: UserEndpoints) -> UsersAPI:
    """
    Создаём API-клиент UsersAPI.
    Он использует:
    - session (requests.Session) для запросов
    - endpoints для формирования урлов
    - timeout для ограничения времени ожидания
    """
    return UsersAPI(
        session=http,
        endpoints=user_endpoints,
        timeout=DEFAULT_TIMEOUT
    )


@pytest.fixture
def user_factory(users_api: UsersAPI):
    """
    Фабрика пользователей на один тест (scope по умолчанию = function).

    Зачем фабрика?
    - в одном тесте можно создать несколько пользователей
    - после теста мы удалим всех созданных (cleanup), даже если тест упал
    """
    created_ids: list[str] = []  # сюда будем складывать id созданных юзеров для последующего удаления

    def create():
        # create_user() возвращает (user_id, user_payload)
        user_id, user = users_api.create_user()
        assert user_id  # сразу убеждаемся, что создание прошло успешно
        created_ids.append(user_id)  # запоминаем id для cleanup
        return user_id, user

    yield create  # отдаём функцию create в тест

    # teardown/cleanup: выполняется после теста
    for user_id in created_ids:
        # allow_not_found=True: если уже удалён — не падаем (часто удобно)
        users_api.delete_user(user_id, allow_not_found=True)


@pytest.fixture
def created_user(user_factory):
    """
    Упрощённая фикстура:
    - создаёт ровно одного пользователя
    - возвращает (user_id, user)
    - удаление обеспечит user_factory
    """
    return user_factory()


# =======================================================POSTS==========================================================
# ======================================================================================================================
# =======================================================POSTS==========================================================


@pytest.fixture(scope="session")
def post_endpoints(base_url: str) -> PostEndpoints:
    """Объект с URL'ами для постов."""
    return PostEndpoints(base_url)


@pytest.fixture(scope="session")
def posts_api(http: requests.Session, post_endpoints: PostEndpoints) -> PostsAPI:
    """API-клиент для постов (создание/удаление/получение)."""
    return PostsAPI(
        session=http,
        endpoints=post_endpoints,
        timeout=DEFAULT_TIMEOUT
    )


@pytest.fixture
def post_factory(posts_api: PostsAPI, user_factory):
    """
    Фабрика постов на тест + авто-удаление.

    Если owner_id не передан — создадим юзера автоматически,
    потому что пост обычно должен принадлежать пользователю (owner).
    """
    created_post_ids: list[str] = []

    def create(owner_id: str | None = None):
        # если владелец не задан — создаём нового пользователя
        if owner_id is None:
            owner_id, _ = user_factory()

        post_id, post = posts_api.create_post(owner_id=owner_id)
        created_post_ids.append(post_id)
        return post_id, post

    yield create

    # cleanup после теста
    for post_id in created_post_ids:
        posts_api.delete_post(post_id, allow_not_found=True)


@pytest.fixture
def created_post(post_factory):
    """Один пост на тест (возвращает (post_id, post))."""
    return post_factory()


# ======================================================COMMENTS=========================================================
# =======================================================================================================================
# ======================================================COMMENTS=========================================================


@pytest.fixture(scope="session")
def comment_endpoints(base_url: str) -> CommentEndpoints:
    """Объект с URL'ами для комментариев."""
    return CommentEndpoints(base_url)


@pytest.fixture(scope="session")
def comments_api(http: requests.Session, comment_endpoints: CommentEndpoints) -> CommentsAPI:
    """API-клиент для комментариев."""
    return CommentsAPI(
        session=http,
        endpoints=comment_endpoints,
        timeout=DEFAULT_TIMEOUT
    )


@pytest.fixture
def comment_factory(comments_api: CommentsAPI, post_factory, user_factory):
    """
    Фабрика комментариев на тест + авто-удаление.

    Если owner_id/post_id не передали — создадим их сами:
    - owner_id (пользователь)
    - post_id (пост этого пользователя)
    """
    created_comment_ids: list[str] = []

    def create(owner_id: str | None = None, post_id: str | None = None):
        # если не передали owner — создаём нового пользователя
        if owner_id is None:
            owner_id, _ = user_factory()

        # если не передали post — создаём пост этого owner
        if post_id is None:
            post_id, _ = post_factory(owner_id=owner_id)

        comment_id, comment = comments_api.create_comment(owner_id=owner_id, post_id=post_id)
        created_comment_ids.append(comment_id)
        return comment_id, comment

    yield create

    # cleanup комментариев после теста
    for cid in created_comment_ids:
        comments_api.delete_comment(cid, allow_not_found=True)


@pytest.fixture
def created_comment(comment_factory):
    """Один комментарий на тест (возвращает (comment_id, comment))."""
    return comment_factory()