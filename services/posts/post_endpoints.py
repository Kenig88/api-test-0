class PostEndpoints:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.list_posts = f"{self.base_url}/post"
        self.create_post = f"{self.base_url}/post/create"

    def post_by_id(self, post_id: str) -> str:
        return f"{self.base_url}/post/{post_id}"

    def posts_by_user(self, user_id: str) -> str:
        return f"{self.base_url}/user/{user_id}/post"