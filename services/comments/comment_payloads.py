from uuid import uuid4


class CommentPayloads:
    @staticmethod
    def create_comment(
            owner_id: str,
            post_id: str,
            message: str | None = None
    ) -> dict:
        if not owner_id:
            raise ValueError("owner_id is required")
        if not post_id:
            raise ValueError("post_id is required")
        if message is None:
            message = f"Auto comment {uuid4().hex[:8]}"  # >=2 символов

        return {
            "message": message,
            "owner": owner_id,  # required
            "post": post_id,  # required
        }
