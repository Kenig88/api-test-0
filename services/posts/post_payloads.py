from uuid import uuid4  # uuid4() — быстрый способ сделать уникальный суффикс для текста поста


class PostPayloads:
    """
    Фабрика payload'ов для Posts API.
    """

    @staticmethod
    def create_post(
            owner_id: str,                 # обязательный: id владельца поста (user id)
            text: str | None = None,       # текст поста (если None — сгенерим дефолтный)
            image: str | None = None,      # ссылка на картинку (если None — поставим дефолт)
            likes: int = 0,                # лайки по умолчанию 0
    ) -> dict:
        """
        Генерирует payload для создания поста.

        Здесь мы делаем "умные дефолты", чтобы в тестах было проще:
        - передал только owner_id — и уже можно создавать пост
        """

        # Валидация обязательного поля: если owner_id пустой, это ошибка использования метода
        if not owner_id:
            raise ValueError("owner_id is required")

        # Если текст не передали — делаем автотекст.
        # Часто в API есть ограничения по длине (например 6-50 символов),
        # поэтому делаем короткий, но валидный текст.
        if text is None:
            text = f"Auto post {uuid4().hex[:8]}"  # [:8] — короткий уникальный кусочек

        # Если image не передали — ставим стабильную ссылку.
        # (В идеале можно держать свою "тестовую" ссылку, чтобы она не умирала.)
        if image is None:
            image = "https://images.unsplash.com/photo-1542291026-7eec264c27ff"

        # Собираем финальный dict, который отправится как JSON
        return {
            "text": text,          # обязательное/важное поле (часто требуется API)
            "image": image,        # ссылка на картинку
            "likes": likes,        # количество лайков
            "owner": owner_id,     # owner обязателен по API: кому принадлежит пост
        }

    @staticmethod
    def update_post(
            text: str | None = None,
            image: str | None = None,
            likes: int | None = None,
            link: str | None = None,
    ) -> dict:
        """
        Генерирует payload для обновления поста.

        Тут принцип другой:
        - мы добавляем в payload только те поля, которые реально передали (не None)
        - это удобно для PATCH/PUT сценариев: меняем только нужные поля
        """

        payload: dict = {}  # начнём с пустого payload

        # Каждое поле добавляем только если оно передано (не None)
        if text is not None:
            payload["text"] = text
        if image is not None:
            payload["image"] = image
        if likes is not None:
            payload["likes"] = likes
        if link is not None:
            payload["link"] = link

        return payload  # вернём только то, что нужно обновить
