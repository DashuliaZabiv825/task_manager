# Менеджер задач (task_manager)

Django 5.2 + Bootstrap 4 (django-bootstrap4). Регистрация, вход, выход (только POST) и личные задачи:
название, описание, срок, приоритет, состояние. Чужие задачи недоступны (404).

## Порядок списка

1. невыполненные раньше выполненных; 2. приоритет: высокий, обычный, низкий;
3. ближайший срок; 4. задачи без срока в конце.

## Локальный запуск (Python 3.12)

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1      (Linux: source .venv/bin/activate)
    python -m pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Тесты: `python manage.py test`

## Сервер (Docker Compose)

`ssh student@192.168.1.11`, `newproject ФАМИЛИЯ-task-manager`, затем в каталоге проекта:
`git init -q`, `git remote add origin <репозиторий>`, `git pull origin main`.
Допишите в `.env` переменные из `.env.example`, затем `docker compose up -d --build`
и `docker compose exec web python manage.py createsuperuser`. Адрес: `http://192.168.1.11:PORT1/`.

## Переменные окружения

| Переменная | Назначение |
| --- | --- |
| `DJANGO_SECRET_KEY` | секретный ключ |
| `DJANGO_DEBUG` | `False` на сервере |
| `DJANGO_ALLOWED_HOSTS` | допустимые адреса через запятую |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | адрес сайта с портом |
| `DJANGO_USE_HTTPS` | защищённые cookie при HTTPS |
| `SQLITE_PATH` | путь к базе в контейнере |
| `PORT1` | внешний порт (выдаёт `newproject`) |
