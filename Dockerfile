# Базовый образ: Python 3.11 на Alpine Linux (легковесный)
FROM python:3.11-alpine

# Полезные переменные окружения:
# - PYTHONDONTWRITEBYTECODE=1: не создаём .pyc файлы (меньше мусора в контейнере)
# - PYTHONUNBUFFERED=1: вывод Python без буферизации (логи сразу видны в CI/терминале)
# - PIP_DISABLE_PIP_VERSION_CHECK=1: отключаем проверку "новая версия pip доступна" (меньше шума в логах)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Устанавливаем системные пакеты, которые нужны контейнеру:
# - tzdata: корректные таймзоны (важно для логов/дат/отчётов)
# - ca-certificates: сертификаты для HTTPS (чтобы curl/pip не падали на TLS)
# - openjdk11-jre: Java Runtime, нужна для Allure Commandline (allure generate)
# - curl: скачиваем Allure (и иногда полезно в отладке)
# - tar: распаковываем .tgz архив
# - wget: запасной скачиватель (может пригодиться)
# - bash: удобная оболочка (у тебя команды в compose написаны через sh, но bash часто нужен для скриптов)
# update-ca-certificates: обновляем/активируем сертификаты в системе
RUN apk add --no-cache \
    tzdata \
    ca-certificates \
    openjdk11-jre \
    curl \
    tar \
    wget \
    bash \
 && update-ca-certificates

# Скачиваем и устанавливаем Allure Commandline:
# - curl -fLsS:
#   -f: упасть с ошибкой, если сервер вернул 4xx/5xx (чтобы билд не "успешно" скачал HTML-страницу ошибки)
#   -L: следовать редиректам
#   -sS: тихий режим, но показывать ошибки
# - сохраняем архив во временную папку /tmp
# - распаковываем в /opt
# - делаем симлинк в /usr/local/bin, чтобы команда `allure` была доступна из PATH
# - удаляем архив после установки, чтобы образ был меньше
RUN curl -fLsS -o /tmp/allure.tgz \
    https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/2.36.0/allure-commandline-2.36.0.tgz \
 && tar -zxf /tmp/allure.tgz -C /opt \
 && ln -sf /opt/allure-2.36.0/bin/allure /usr/local/bin/allure \
 && rm -f /tmp/allure.tgz

# Рабочая директория контейнера: все команды дальше будут выполняться отсюда
WORKDIR /usr/workspace

# Копируем только requirements.txt отдельно:
# это важно для кеша Docker — если код меняется, но зависимости нет,
# Docker переиспользует слой с установленными пакетами и пересборка быстрее
COPY requirements.txt /usr/workspace/requirements.txt

# Устанавливаем Python-зависимости:
# 1) обновляем pip (чтобы меньше было проблем с установкой пакетов)
# 2) ставим зависимости из requirements.txt без кеша (чтобы слой был меньше)
RUN python -m pip install --no-cache-dir --upgrade pip \
 && python -m pip install --no-cache-dir -r /usr/workspace/requirements.txt

# Копируем весь проект внутрь образа
# (в твоём случае в compose ты ещё и монтируешь volume, так что локальные файлы будут перекрывать это копирование)
COPY . /usr/workspace

# Команда по умолчанию (если запустить контейнер без docker-compose command:)
# В compose ты переопределяешь команду, но CMD всё равно полезен как дефолт
CMD ["pytest"]
