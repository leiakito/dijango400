# Repository Guidelines

## Project Structure & Module Organization
- `apps/` holds domain apps (users, games, recommendations, content, community, analytics, system); keep logic in `models.py`, `services.py`, `serializers.py`, `views.py`, and `permissions.py`.
- Settings and routing live in `config/` (`config/settings/dev.py` for local, `config/settings/prod.py` for deploy); Celery config is `config/celery.py`.
- Crawlers sit in `crawlers/game_crawler/`; ops scripts in `scripts/` (`db_backup.py`, `crawl_run.py`); container assets in `docker/`; OpenAPI exports in `openapi/`. Runtime artifacts (`logs/`, `media/`, `backups/`) stay out of version control.

## Setup, Build, and Run
- Python 3.10+. Install deps with `pip install -r requirements.txt` (use a venv).
- Secrets/env: `cp .env.example .env` then set DB, Redis, and JWT keys.
- DB ready: `python manage.py makemigrations && python manage.py migrate`.
- Local server: `python manage.py runserver 0.0.0.0:8000 --settings=config.settings.dev`.
- Workers: `celery -A config worker -l info` and `celery -A config beat -l info` (Redis required).
- Containers: from repo root `docker-compose up -d`; inspect with `docker-compose logs -f`.

## Coding Style & Naming
- Follow PEP 8, 4-space indents, and grouped imports; add type hints where helpful.
- DRF naming: `FooSerializer`, `FooViewSet`, `FooFilter`; keep queries/business logic in `services.py` to keep views slim.
- Use snake_case model fields and consistent serializer field names; match nearby docstring language (English/Chinese mix).

## Testing Guidelines
- Runner: `python manage.py test` or `python manage.py test apps.users`. Use `APITestCase`/`APIClient` for endpoints and `TestCase` for models/services.
- Place files as `apps/<app>/tests/test_<feature>.py`; classes `Test<Feature>`. Cover permissions, caching, and Celery side effects when adding features.

## Commit & Pull Request Guidelines
- Conventional-style prefixes (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`); imperative subject; mention touched app when possible.
- PRs include a brief summary, linked issue/task, migration note (yes/no), and local verification steps (tests or key runserver/curl calls). Note API contract changes (paths/fields) and attach screenshots for admin/content flows when useful.

## Security & Configuration Tips
- Keep secrets, dumps, and runtime files (`.env`, `logs/`, `backups/`, `media/`) out of commits.
- For production: set `DJANGO_SETTINGS_MODULE=config.settings.prod`, run `python manage.py collectstatic --noinput`, serve via gunicorn/nginx (see `docker/nginx.conf`), and ensure Redis + Celery are running before enabling recommendation endpoints.
