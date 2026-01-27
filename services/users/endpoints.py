class Endpoints:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    @property
    def create_user(self) -> str:
        return f"{self.base_url}/user/create"

    def get_user_by_id(self, user_id: str) -> str:
        return f"{self.base_url}/user/{user_id}"

    def delete_user(self, user_id: str) -> str:
        return f"{self.base_url}/user/{user_id}"

    def update_user(self, user_id: str) -> str:
        return f"{self.base_url}/user/{user_id}"
