# Базовый образ: Python 3.11 на Alpine Linux (легковесный)
FROM python:3.11-alpine

# Полезные переменные окружения:
# - PYTHONDONTWRITEBYTECODE=1: не создаём .pyc файлы
# - PYTHONUNBUFFERED=1: логи без буферизации
# - PIP_DISABLE_PIP_VERSION_CHECK=1: меньше шума от pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Системные пакеты, которые реально полезны для тестов/HTTPS/таймзоны
# Java/Allure CLI/curl/tar/wget больше не нужны, т.к. HTML отчёт строится в workflow
RUN apk add --no-cache \
      tzdata \
      ca-certificates \
      bash \
  && update-ca-certificates

# Рабочая директория контейнера
WORKDIR /usr/workspace

# Копируем requirements.txt отдельно для кеша
COPY requirements.txt /usr/workspace/requirements.txt

# Ставим зависимости
RUN python -m pip install --no-cache-dir --upgrade pip \
 && python -m pip install --no-cache-dir -r /usr/workspace/requirements.txt

# Копируем проект (в compose всё равно будет volume, но пусть будет)
COPY . /usr/workspace

# По умолчанию запускаем pytest (в compose вы переопределяете command)
CMD ["pytest"]
