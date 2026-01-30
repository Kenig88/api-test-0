FROM python:3.12-slim

# Sensible defaults for containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install deps first (better layer caching)
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . .

# Create directories commonly mounted by docker-compose
RUN mkdir -p /app/allure-results /app/allure-report

# Default command (can be overridden by docker-compose)
CMD ["bash", "-lc", "pytest -m \"${PYTEST_MARKS:-smoke}\" -sv --alluredir=allure-results ${PYTEST_EXTRA_ARGS:-}"]
