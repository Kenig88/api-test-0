import pytest  # подключаем библиотеку pytest (фреймворк для запуска тестов и фикстур)

# Импортируем классы-клиенты для работы с разными частями API
# (обычно это обёртки над HTTP-запросами: get/post/put/delete)
from services.posts.api_posts import PostsAPI
from services.users.api_users import UsersAPI
from services.comments.api_comments import CommentsAPI


class BaseTest:
    """
    Базовый класс для тестов.

    Идея: все тестовые классы могут наследоваться от BaseTest и получать
    готовые API-клиенты (users/posts/comments) через self.api_users и т.д.
    """

    # Аннотации типов (type hints).
    # Они НЕ создают объекты, а только подсказывают IDE/линтеру:
    # "self.api_users будет объектом UsersAPI"
    api_users: UsersAPI
    api_posts: PostsAPI
    api_comments: CommentsAPI

    @pytest.fixture(autouse=True)
    def _init_clients(self, users_api, posts_api, comments_api):
        """
        Фикстура pytest, которая автоматически запускается перед каждым тестом.

        autouse=True означает:
        - тебе не нужно явно передавать эту фикстуру в тесты
        - она будет применяться ко всем тестам этого класса (и наследников)

        Параметры users_api, posts_api, comments_api — это ДРУГИЕ фикстуры,
        которые pytest должен найти (обычно в conftest.py) и передать сюда.
        """

        # Сохраняем переданные клиенты в поля класса,
        # чтобы в тестах можно было писать self.api_users / self.api_posts / self.api_comments
        self.api_users = users_api
        self.api_posts = posts_api
        self.api_comments = comments_api
