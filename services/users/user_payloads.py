import uuid  # генерация уникальных значений (uuid4) — полезно, чтобы email не повторялся
from faker import Faker  # генератор “фейковых” данных: имена, телефоны, даты и т.д.

fake = Faker()  # создаём экземпляр Faker один раз, чтобы использовать в методах


class UserPayloads:
    """
    Класс-фабрика payload'ов для запросов к Users API.

    Payload = dict, который мы отправляем в json=... при POST/PUT запросах.
    """

    @staticmethod
    def create_user() -> dict:
        """
        Генерирует тело запроса для создания пользователя.

        Почему делаем уникальный email:
        - многие API не разрешают создавать несколько пользователей с одинаковым email
        - в тестах важно избегать конфликтов/флаков из-за дублей
        """
        # uuid.uuid4().hex — это уникальная строка без дефисов
        unique_email = f"autotest_{uuid.uuid4().hex}@example.com"

        return {
            "email": unique_email,                          # уникальный email для создания пользователя
            "firstName": fake.first_name(),                 # случайное имя
            "lastName": fake.last_name(),                   # случайная фамилия
            "dateOfBirth": fake.date_of_birth().isoformat(),# дата рождения -> строка 'YYYY-MM-DD'
            "phone": fake.msisdn()[:14],                    # “номер телефона” как строка цифр (обрезаем до 14)
        }

    @staticmethod
    def update_user() -> dict:
        """
        Генерирует тело запроса для обновления пользователя.

        Обычно при update не обязательно передавать все поля —
        можно менять только часть (firstName, lastName, phone).
        """
        return {
            "firstName": fake.first_name(),  # новое имя
            "lastName": fake.last_name(),    # новая фамилия
            "phone": fake.msisdn()[:14],     # новый номер
        }
