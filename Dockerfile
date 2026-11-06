
# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости проекта
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы проекта в контейнер
COPY . .

# Открываем порт приложения
EXPOSE 8080

# Запускаем сервер Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
