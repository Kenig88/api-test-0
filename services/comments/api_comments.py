import allure
import requests

from services.comments.endpoints import CommentEndpoints
from services.comments.payloads import Payloads
from services.comments.comments_model import CommentModel, CommentPreviewModel
from utils.helper import Helper


class CommentsAPI(Helper):
    def __init__(self, session: requests.Session, endpoints: CommentEndpoints, timeout: int = 15):
        super().__init__()
        self.session = session
        self.endpoints = endpoints
        self.timeout = timeout

    def _attach_response_safe(self, response: requests.Response) -> None:
        try:
            self.attach_response(response.json())
        except Exception:
            allure.attach(
                body=response.text,
                name="API Response (text)",
                attachment_type=allure.attachment_type.TEXT
            )

    # -------- RAW --------

    @allure.step("GET /comment (raw)")
    def list_comments_response(self, limit: int = 10, page: int = 0) -> requests.Response:
        resp = self.session.get(self.endpoints.list_comments, params={"limit": limit, "page": page}, timeout=self.timeout)
        self._attach_response_safe(resp)
        return resp

    @allure.step("GET /post/{post_id}/comment (raw)")
    def list_comments_by_post_response(self, post_id: str, limit: int = 10, page: int = 0) -> requests.Response:
        resp = self.session.get(self.endpoints.comments_by_post(post_id), params={"limit": limit, "page": page}, timeout=self.timeout)
        self._attach_response_safe(resp)
        return resp

    @allure.step("GET /user/{user_id}/comment (raw)")
    def list_comments_by_user_response(self, user_id: str, limit: int = 10, page: int = 0) -> requests.Response:
        resp = self.session.get(self.endpoints.comments_by_user(user_id), params={"limit": limit, "page": page}, timeout=self.timeout)
        self._attach_response_safe(resp)
        return resp

    @allure.step("POST /comment/create (raw)")
    def create_comment_response(self, payload: dict) -> requests.Response:
        resp = self.session.post(self.endpoints.create_comment, json=payload, timeout=self.timeout)
        self._attach_response_safe(resp)
        return resp

    @allure.step("DELETE /comment/{comment_id} (raw)")
    def delete_comment_response(self, comment_id: str) -> requests.Response:
        resp = self.session.delete(self.endpoints.delete_comment(comment_id), timeout=self.timeout)
        self._attach_response_safe(resp)
        return resp

    # -------- CHECKED --------

    @allure.step("Create comment (owner={owner_id}, post={post_id})")
    def create_comment(self, owner_id: str, post_id: str, payload: dict | None = None) -> tuple[str, CommentModel]:
        if payload is None:
            payload = Payloads.create_comment(owner_id=owner_id, post_id=post_id)

        resp = self.create_comment_response(payload)
        body = resp.json()
        assert resp.status_code in (200, 201), body

        comment_id = body.get("id")
        assert comment_id, f"'id' not found in response: {body}"
        return comment_id, CommentModel(**body)

    @allure.step("Delete comment by id: {comment_id}")
    def delete_comment(self, comment_id: str, allow_not_found: bool = False) -> str | None:
        resp = self.delete_comment_response(comment_id)

        if allow_not_found and resp.status_code == 404:
            return None

        # docs: delete returns string id :contentReference[oaicite:5]{index=5}
        assert resp.status_code in (200, 204), resp.text

        try:
            body = resp.json()
        except Exception:
            body = resp.text.strip()

        if isinstance(body, str):
            return body.strip('"')
        if isinstance(body, dict):
            return body.get("id") or body.get("data") or str(body)
        return str(body)

    @allure.step("List comments")
    def list_comments(self, limit: int = 10, page: int = 0) -> list[CommentPreviewModel]:
        resp = self.list_comments_response(limit=limit, page=page)
        body = resp.json()
        assert resp.status_code == 200, body
        return [CommentPreviewModel(**item) for item in body.get("data", [])]

    @allure.step("List comments by post: {post_id}")
    def list_comments_by_post(self, post_id: str, limit: int = 10, page: int = 0) -> list[CommentPreviewModel]:
        resp = self.list_comments_by_post_response(post_id=post_id, limit=limit, page=page)
        body = resp.json()
        assert resp.status_code == 200, body
        return [CommentPreviewModel(**item) for item in body.get("data", [])]

    @allure.step("List comments by user: {user_id}")
    def list_comments_by_user(self, user_id: str, limit: int = 10, page: int = 0) -> list[CommentPreviewModel]:
        resp = self.list_comments_by_user_response(user_id=user_id, limit=limit, page=page)
        body = resp.json()
        assert resp.status_code == 200, body
        return [CommentPreviewModel(**item) for item in body.get("data", [])]
