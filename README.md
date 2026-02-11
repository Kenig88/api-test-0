# -API Test Framework (pytest + requests + Allure)-


Небольшой тестовый фреймворк для API-тестов на базе:
- **pytest** — раннер и организация тестов
- **requests** — HTTP-клиент
- **pydantic v2** — валидация схем/ответов
- **allure-pytest** — репортинг + attachments (запрос/ответ в отчёте)
- **Docker / Docker Compose** — запуск тестовых наборов в контейнерах
- **GitHub Actions** — запуск в CI + публикация Allure Report в GitHub Pages с историей

Тестируемый API: **DummyAPI** (базовый URL вида `https://dummyapi.io/data/v1`). Авторизация через заголовок `app-id`.

---

## Быстрый старт

### Требования:
- Python **3.11+**
- pip
- Docker + Docker Compose
- Allure CLI для локального просмотра HTML-отчёта

### Установка зависимостей (локально):
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### Настройка окружения (.env):

Создай файл .env на основе .env.example:

.env.example:

HOST=https://dummyapi.io/data/v1 \
API_TOKEN=__YOUR__API__TOKEN__

---

## Запуск тестов локально через Pytest:

Маркеры тестов определены в pytest.ini:
* smoke — быстрые критичные проверки.
* regression — полный регресс.
* negative — негативные сценарии/ошибки.

Запустить все тесты:
- "pytest -sv"

Запуск по маркерам:
- "pytest -sv -m smoke"
- "pytest -sv -m regression"
- "pytest -sv -m negative"

Сгенерировать Allure results:
- pytest -sv --alluredir=allure-results --clean-alluredir

---

## Собрать образ Docker:

1. "docker compose build" \
или
2. "docker compose build --no-cache"    <--- если надо пересобрать “с нуля” без кеша.

## Запуск тестов через Docker Compose:

Запустить всё (all):
* "docker compose run --rm all"

Запустить smoke:
* "docker compose run --rm smoke" 

Запустить regression: 
* "docker compose run --rm regression"

Запустить negative:
* "docker compose run --rm negative"

## Посмотреть историю Allure:
"allure open allure-report"

---

## CI: GitHub Actions + Allure Report в GitHub Pages:

В проекте настроен workflow: .github/workflows/api-tests-docker.yml.

Как включить:

1. GitHub → Settings → Secrets and variables → Actions → Secrets добавь:

2. HOST (например, https://dummyapi.io/data/v1)

3. API_TOKEN (твой app-id)

4. GitHub → Settings → Pages:

5. Source: Deploy from a branch

6. Branch: gh-pages

7. Folder: /(root)

Как запустить:

1. Actions → API tests (Docker + Allure) → Run workflow

2. Выбери suite: all / smoke / regression / negative

Где смотреть отчёт:

1. Workflow публикует отчёт в GitHub Pages:

2. .../latest/ — всегда свежий отчёт (алиас)

3. .../<run_number>/ — отчёт конкретного прогона

---

## Структура проекта:

```text
api-test-0/
  config/
    base_test.py               # базовый класс тестов (доступ к API клиентам)
  services/
    users/                     # endpoints/payloads/models + client UsersAPI
    posts/                     # endpoints/payloads/models + client PostsAPI
    comments/                  # endpoints/payloads/models + client CommentsAPI
  tests/
    conftest.py                # фикстуры, сессия, фабрики (создание/cleanup сущностей)
    users/                     # тесты пользователей
    posts/                     # тесты постов
    comments/                  # тесты комментариев
  utils/
    raw_http.py                # "сырой" HTTP клиент для негативных проверок
    assertions.py              # проверки статусов/JSON
    helper.py                  # вспомогательные функции (Allure attachments и т.п.)
  docker-compose.yml           # сервисы all/smoke/regression/negative
  Dockerfile                   # окружение для запуска тестов
  requirements.txt
  pytest.ini
  .env.example
```

---

## Как устроен подход к API:

В клиентах (services/*/api_*.py) используется подход из двух уровней:

* Raw response методы - возвращают requests.Response. Полезно, когда нужно вручную проверить тело/заголовки/ошибки.

* Checked методы - проверяют статус-код, валидируют JSON, возвращают Pydantic-модель или словарь.

Для негативных сценариев используется utils/raw_http.py — это позволяет делать запросы без app-id или с “ломаными” заголовками и проверять ошибки API.

---

## Диагностика проблем: 

* 403 / Unauthorized / app-id missing:
Проверь: 
1. API_TOKEN корректный.
2. env лежит в корне проекта и содержит актуальные значения.
3. в CI секреты HOST и API_TOKEN добавлены.

* Нет allure-results/: \
Запускай так -> "pytest --alluredir=allure-results --clean-alluredir"

* Docker Compose ругается на переменные: \
Убедись, что переменные определены, в .env (в корне проекта) или экспортированы в окружение (HOST/API_TOKEN).

* Безопасность:
1. Никогда не коммить .env (секреты).
2. Если токен “засветился” — сразу перевыпусти (rotate).
3. Не добавляй в репо .venv/, .git/, .idea/, __pycache__/, .pytest_cache/.