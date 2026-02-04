# Берём готовый официальный образ Python 3.11 на Alpine Linux.
# Alpine — очень лёгкий дистрибутив, поэтому итоговый образ меньше.
FROM python:3.11-alpine


# ENV — переменные окружения внутри контейнера.
# Они делают поведение Python/pip удобнее в CI и при отладке.
ENV PYTHONDONTWRITEBYTECODE=1 \        # не создавать .pyc файлы (меньше мусора)
    PYTHONUNBUFFERED=1 \               # вывод в лог сразу, без буферизации (важно в CI)
    PIP_DISABLE_PIP_VERSION_CHECK=1    # pip не будет спамить про "новая версия доступна"


# Устанавливаем системные пакеты ОС (через apk — пакетный менеджер Alpine).
# Здесь только то, что реально нужно тестам:
# - tzdata: чтобы корректно работали таймзоны/даты (часто важно для логов и проверок)
# - ca-certificates: чтобы HTTPS запросы работали (requests/pip/curl и т.д.)
# - bash: иногда полезен для скриптов и команд (хотя у тебя команды в compose через sh)
#
# ВАЖНО: Java и Allure CLI мы больше НЕ ставим,
# потому что HTML отчёт Allure генерируется в GitHub Actions (workflow),
# а контейнер делает только pytest + allure-results.
RUN apk add --no-cache \
      tzdata \
      ca-certificates \
      bash \
  && update-ca-certificates


# WORKDIR задаёт рабочую папку внутри контейнера.
# Все дальнейшие команды (COPY/RUN/CMD) будут выполняться относительно неё.
WORKDIR /usr/workspace


# Копируем requirements.txt отдельно.
# Это сделано специально ради Docker-кеша:
# если код тестов меняется, но зависимости (requirements.txt) нет,
# Docker повторно использует слой с уже установленными библиотеками → сборка быстрее.
COPY requirements.txt /usr/workspace/requirements.txt


# Ставим Python-зависимости проекта.
# --no-cache-dir уменьшает размер образа (pip не хранит кеш пакетов внутри слоя).
# Сначала обновляем pip, потом ставим зависимости.
RUN python -m pip install --no-cache-dir --upgrade pip \
 && python -m pip install --no-cache-dir -r /usr/workspace/requirements.txt


# Копируем весь проект внутрь образа.
# В твоём docker-compose.yml всё равно есть volume ".:/usr/workspace",
# поэтому при запуске через compose файлы с хоста "перекроют" то, что скопировано в образ.
# Но COPY полезен на случай, если кто-то запустит контейнер без volume-монтажа.
COPY . /usr/workspace


# CMD — команда по умолчанию, если контейнер запущен без "command:" в compose.
# У тебя в docker-compose.yml для каждого сервиса есть свой command, поэтому обычно CMD не используется.
CMD ["pytest"]
