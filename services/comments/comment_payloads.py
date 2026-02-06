from uuid import uuid4  # нужен для генерации уникального сообщения комментария


class CommentPayloads:
    """
    Фабрика payload'ов для Comments API.
    """

    @staticmethod
    def create_comment(
            owner_id: str,                 # обязательный: кто оставил комментарий
            post_id: str,                  # обязательный: к какому посту комментарий
            message: str | None = None     # текст комментария (если None — сгенерим)
    ) -> dict:
        """
        Генерирует payload для создания комментария.

        Требования обычно такие:
        - owner обязателен
        - post обязателен
        - message должна быть не пустой и, например, >= 2 символов
        """

        # Проверяем обязательные параметры "на входе" —
        # лучше упасть здесь понятной ошибкой, чем получить 400 от API и долго разбираться.
        if not owner_id:
            raise ValueError("owner_id is required")
        if not post_id:
            raise ValueError("post_id is required")

        # Если message не передали — делаем автосообщение.
        if message is None:
            message = f"Auto comment {uuid4().hex[:8]}"  # коротко и уникально (и >= 2 символов)

        return {
            "message": message,   # текст комментария
            "owner": owner_id,    # required: автор комментария
            "post": post_id,      # required: пост, к которому комментарий
        }
