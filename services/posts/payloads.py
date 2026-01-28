from uuid import uuid4


class Payloads:
    @staticmethod
    def create_post(owner_id: str,
                    text: str | None = None,
                    image: str | None = None,
                    likes: int = 0,
                    tags: list[str] | None = None) -> dict:
        if not owner_id:
            raise ValueError("owner_id is required")

        if text is None:
            # Post Create: text length 6-50 (preview) :contentReference[oaicite:3]{index=3}
            text = f"Auto post {uuid4().hex[:8]}"

        if image is None:
            image = "https://images.unsplash.com/photo-1542291026-7eec264c27ff"

        if tags is None:
            tags = ["qa", "pytest"]

        return {
            "text": text,
            "image": image,
            "likes": likes,
            "tags": tags,
            "owner": owner_id,  # required :contentReference[oaicite:4]{index=4}
        }

    @staticmethod
    def update_post(text: str | None = None,
                    image: str | None = None,
                    likes: int | None = None,
                    link: str | None = None,
                    tags: list[str] | None = None) -> dict:
        payload: dict = {}
        if text is not None:
            payload["text"] = text
        if image is not None:
            payload["image"] = image
        if likes is not None:
            payload["likes"] = likes
        if link is not None:
            payload["link"] = link
        if tags is not None:
            payload["tags"] = tags
        return payload
