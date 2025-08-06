FROM python:3.11-slim

# Встановлюємо потрібні пакети (опційно)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Створюємо робочу директорію
WORKDIR /app

# Копіюємо проєкт
COPY . .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt || true

# Залишаємо контейнер "живим" для ручного доступу
CMD ["tail", "-f", "/dev/null"]
