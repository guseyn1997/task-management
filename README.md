# Система управления задачами (Task Management API)

API для системы управления задачами, построенный с использованием FastAPI и SQLAlchemy.

## Возможности

- Регистрация и авторизация пользователей с использованием JWT
- CRUD операции для управления проектами и задачами
- Алгоритм оптимального распределения задач между сотрудниками
- Полная документация API через Swagger UI

## Требования

- Python 3.8+
- PostgreSQL (можно заменить на SQLite для локальной разработки)

## Установка и запуск

### С использованием Docker (рекомендуется)

1. Клонируйте репозиторий:
git clone https://github.com/guseyn1997/task-management-api.git
cd task-management-api

2. Запустите с Docker Compose:
docker-compose up -d

3. API будет доступен по адресу: http://localhost:8000
Swagger UI: http://localhost:8000/docs

### Локальная установка

1. Клонируйте репозиторий:
git clone https://github.com/your-username/task-management-api.git
cd task-management-api

2. Создайте и активируйте виртуальное окружение:
python -m venv venv
# На Linus: source venv/bin/activate
# На Windows: venv\Scripts\activate

3. Установите зависимости:
pip install -r requirements.txt

4. Создайте файл .env:
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key

5. Запустите приложение:
uvicorn app.main:app --reload

6. API будет доступен по адресу: http://localhost:8000
Swagger UI: http://localhost:8000/docs

## Запуск тестов
pytest app/tests


## Структура проекта

- `app/` - Основной код приложения
  - `api/` - API роутеры
  - `models/` - SQLAlchemy модели
  - `schemas/` - Pydantic схемы
  - `crud/` - CRUD операции
  - `core/` - Ключевые модули (конфигурация, безопасность)
  - `tests/` - Автоматические тесты

## Алгоритм оптимизации задач

API включает алгоритм оптимального распределения задач между сотрудниками, учитывающий:
- Текущую загруженность сотрудников
- Приоритет задач
- Оптимальные сроки выполнения

Для использования алгоритма выполните POST-запрос на эндпоинт `/optimize-tasks` с указанием ID проекта.
