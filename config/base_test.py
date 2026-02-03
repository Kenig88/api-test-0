import pytest
from services.posts.api_posts import PostsAPI
from services.users.api_users import UsersAPI
from services.comments.api_comments import CommentsAPI


class BaseTest:
    api_users: UsersAPI
    api_posts: PostsAPI
    api_comments: CommentsAPI

    @pytest.fixture(autouse=True)
    def _init_clients(self, users_api, posts_api, comments_api):
        self.api_users = users_api
        self.api_posts = posts_api
        self.api_comments = comments_api