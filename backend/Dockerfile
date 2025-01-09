# Dockerfile
FROM python:3.12-slim

# Установка зависимостей для системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Установка зависимостей Python
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Команда запуска приложения
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
