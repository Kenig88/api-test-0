import allure
import requests
from services.posts.post_endpoints import PostEndpoints
from services.posts.post_payloads import PostPayloads
from services.posts.post_model import PostModel
from utils.helper import Helper


class PostsAPI(Helper):
    """
    PostsAPI — клиент-обёртка над HTTP-запросами к /post.

    - RAW методы (*_response): возвращают requests.Response без assert'ов
    - CHECKED методы: проверяют статус, парсят JSON, возвращают PostModel
    """

    def __init__(self, session: requests.Session, endpoints: PostEndpoints, timeout: int = 15):
        super().__init__()
        self.session = session
        self.endpoints = endpoints
        self.timeout = timeout

    # ============================================== RAW (no asserts) ==============================================

    @allure.step("POST /post/create (raw)")
    def create_post_response(self, payload: dict) -> requests.Response:
        resp = self.session.post(
            url=self.endpoints.create_post,
            json=payload,
            timeout=self.timeout,
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("GET /post/{post_id} (raw)")
    def get_post_by_id_response(self, post_id: str) -> requests.Response:
        resp = self.session.get(
            url=self.endpoints.post_by_id(post_id),
            timeout=self.timeout,
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("PUT /post/{post_id} (raw)")
    def update_post_response(self, post_id: str, payload: dict) -> requests.Response:
        resp = self.session.put(
            url=self.endpoints.post_by_id(post_id),
            json=payload,
            timeout=self.timeout,
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("DELETE /post/{post_id} (raw)")
    def delete_post_response(self, post_id: str) -> requests.Response:
        resp = self.session.delete(
            url=self.endpoints.post_by_id(post_id),
            timeout=self.timeout,
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("GET /post (raw)")
    def list_posts_response(self, limit: int = 10, page: int = 0) -> requests.Response:
        resp = self.session.get(
            url=self.endpoints.list_posts,
            params={"limit": limit, "page": page},
            timeout=self.timeout,
        )
        self.attach_response_safe(resp)
        return resp

    @allure.step("GET /user/{user_id}/post (raw)")
    def list_posts_by_user_response(self, user_id: str, limit: int = 10, page: int = 0) -> requests.Response:
        resp = self.session.get(
            url=self.endpoints.posts_by_user(user_id),
            params={"limit": limit, "page": page},
            timeout=self.timeout,
        )
        self.attach_response_safe(resp)
        return resp

    # ============================================== CHECKED ==============================================

    @allure.step("Create post (owner={owner_id})")
    def create_post(self, owner_id: str, payload: dict | None = None) -> tuple[str, PostModel]:
        if payload is None:
            payload = PostPayloads.create_post(owner_id)
        resp = self.create_post_response(payload)
        body = resp.json()

        assert resp.status_code in (200, 201), body

        post_id = body.get("id")
        assert post_id, f"'id' not found in response: {body}"

        return post_id, PostModel.model_validate(body)

    @allure.step("Get post by id: {post_id}")
    def get_post_by_id(self, post_id: str) -> PostModel:
        resp = self.get_post_by_id_response(post_id)
        body = resp.json()
        assert resp.status_code == 200, body
        return PostModel.model_validate(body)

    @allure.step("Update post by id: {post_id}")
    def update_post(self, post_id: str, payload: dict) -> PostModel:
        resp = self.update_post_response(post_id, payload)
        body = resp.json()
        assert resp.status_code == 200, body
        return PostModel.model_validate(body)

    @allure.step("Delete post by id: {post_id}")
    def delete_post(self, post_id: str, allow_not_found: bool = False) -> str | None:
        resp = self.delete_post_response(post_id)
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

    @allure.step("List posts")
    def list_posts(self, limit: int = 10, page: int = 0) -> list[PostModel]:
        resp = self.list_posts_response(limit=limit, page=page)
        body = resp.json()
        assert resp.status_code == 200, body

        return [PostModel.model_validate(item) for item in body.get("data", [])]

    @allure.step("List posts by user: {user_id}")
    def list_posts_by_user(self, user_id: str, limit: int = 10, page: int = 0) -> list[PostModel]:
        resp = self.list_posts_by_user_response(user_id=user_id, limit=limit, page=page)
        body = resp.json()
        assert resp.status_code == 200, body
        return [PostModel.model_validate(item) for item in body.get("data", [])]