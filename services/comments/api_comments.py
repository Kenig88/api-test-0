import allure
import requests
from services.comments.comment_endpoints import CommentEndpoints
from services.comments.comment_payloads import CommentPayloads
from services.comments.comments_model import CommentModel
from utils.helper import Helper


class CommentsAPI(Helper):
    """
    API-клиент для работы с комментариями.

    - *_response (RAW): запросы без assert'ов, возвращают requests.Response
    - методы без *_response (CHECKED): assert статуса + парсинг JSON в Pydantic-модели
    """

    def __init__(self, session: requests.Session, endpoints: CommentEndpoints, timeout: int = 15):
        super().__init__()
        self.session = session
        self.endpoints = endpoints
        self.timeout = timeout

# ================================================RAW=(no=asserts)======================================================
# ======================================================================================================================
# ================================================RAW=(no=asserts)======================================================

    @allure.step("GET /comment (raw)")
    def list_comments_response(self, limit: int = 10, page: int = 0) -> requests.Response:
        resp = self.session.get(
            url=self.endpoints.list_comments,
            params={"limit": limit, "page": page},
            timeout=self.timeout,
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("GET /post/{post_id}/comment (raw)")
    def list_comments_by_post_response(self, post_id: str, limit: int = 10, page: int = 0) -> requests.Response:
        resp = self.session.get(
            url=self.endpoints.comments_by_post(post_id),
            params={"limit": limit, "page": page},
            timeout=self.timeout,
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("GET /user/{user_id}/comment (raw)")
    def list_comments_by_user_response(self, user_id: str, limit: int = 10, page: int = 0) -> requests.Response:
        resp = self.session.get(
            url=self.endpoints.comments_by_user(user_id),
            params={"limit": limit, "page": page},
            timeout=self.timeout,
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("POST /comment/create (raw)")
    def create_comment_response(self, payload: dict) -> requests.Response:
        resp = self.session.post(
            url=self.endpoints.create_comment,
            json=payload,
            timeout=self.timeout,
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("DELETE /comment/{comment_id} (raw)")
    def delete_comment_response(self, comment_id: str) -> requests.Response:
        resp = self.session.delete(
            url=self.endpoints.delete_comment(comment_id),
            timeout=self.timeout,
        )
        self.attach_response_safe(resp)
        return resp


# ==================================================CHECKED=============================================================
# ======================================================================================================================
# ==================================================CHECKED=============================================================

    @allure.step("Create comment (owner={owner_id}, post={post_id})")
    def create_comment(self, owner_id: str, post_id: str, payload: dict | None = None) -> tuple[str, CommentModel]:
        if payload is None:
            payload = CommentPayloads.create_comment(owner_id=owner_id, post_id=post_id)

        resp = self.create_comment_response(payload)
        body = resp.json()

        assert resp.status_code in (200, 201), body

        comment_id = body.get("id")
        assert comment_id, f"'id' not found in response: {body}"

        return comment_id, CommentModel.model_validate(body)

    @allure.step("Delete comment by id: {comment_id}")
    def delete_comment(self, comment_id: str, allow_not_found: bool = False) -> str | None:
        resp = self.delete_comment_response(comment_id)

        if allow_not_found and resp.status_code == 404:
            return None

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
    def list_comments(self, limit: int = 10, page: int = 0) -> list[CommentModel]:
        resp = self.list_comments_response(limit=limit, page=page)
        body = resp.json()
        assert resp.status_code == 200, body
        return [CommentModel.model_validate(item) for item in body.get("data", [])]

    @allure.step("List comments by post: {post_id}")
    def list_comments_by_post(self, post_id: str, limit: int = 10, page: int = 0) -> list[CommentModel]:
        resp = self.list_comments_by_post_response(post_id=post_id, limit=limit, page=page)
        body = resp.json()
        assert resp.status_code == 200, body
        return [CommentModel.model_validate(item) for item in body.get("data", [])]

    @allure.step("List comments by user: {user_id}")
    def list_comments_by_user(self, user_id: str, limit: int = 10, page: int = 0) -> list[CommentModel]:
        resp = self.list_comments_by_user_response(user_id=user_id, limit=limit, page=page)
        body = resp.json()
        assert resp.status_code == 200, body
        return [CommentModel.model_validate(item) for item in body.get("data", [])]