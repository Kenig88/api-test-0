class CommentEndpoints:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.list_comments = f"{self.base_url}/comment"
        self.create_comment = f"{self.base_url}/comment/create"

    def delete_comment(self, comment_id: str) -> str:
        return f"{self.base_url}/comment/{comment_id}"

    def comments_by_post(self, post_id: str) -> str:
        return f"{self.base_url}/post/{post_id}/comment"

    def comments_by_user(self, user_id: str) -> str:
        return f"{self.base_url}/user/{user_id}/comment"
