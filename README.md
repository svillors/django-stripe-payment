# Django Stripe Payment

Django-приложение для оплаты товаров и заказов через Stripe.

Django-приложение с оплатой через Stripe (PaymentIntent). Поддерживает оплату товаров и заказов с учётом скидок и налогов. Данные хранятся в PostgreSQL.

## Демо проекта

Демо проекта можно посмотреть по этой [ссылке](https://svillors.com/).

## Стек

- Python 3.12
- Django 6
- PostgreSQL
- Stripe
- Gunicorn
- WhiteNoise
- Docker Compose

## Переменные окружения

Создайте `.env` на основе примера:

```bash
cp .env.example .env
```

Минимальный набор:

```env
DJANGO_SECRET_KEY=change-me
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

STRIPE_SECRET_KEY=sk_test_change_me
STRIPE_PUBLISHABLE_KEY=pk_test_change_me

POSTGRES_PASSWORD=change-me
```

Для сервера замените:

- `DJANGO_SECRET_KEY` на случайную длинную строку;
- `DJANGO_ALLOWED_HOSTS` на домен или IP сервера;
- Stripe-ключи на реальные тестовые или live-ключи;
- `POSTGRES_PASSWORD` на нормальный пароль.

## Запуск через Docker

Собрать и запустить проект:

```bash
docker compose up -d --build
```

После старта приложение будет доступно на `http://127.0.0.1:8000`.


## Локальный запуск без Docker

Установить зависимости:

```bash
uv sync
```

Или через `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Для локального запуска нужен PostgreSQL. По умолчанию приложение ожидает:

```env
POSTGRES_DB=django_stripe_payment
POSTGRES_USER=django_stripe_payment
POSTGRES_PASSWORD=change-me
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Если нужно, эти переменные можно добавить в `.env`.

Применить миграции:

```bash
python manage.py migrate
```

Запустить dev-сервер:

```bash
python manage.py runserver
```

## Stripe

Для тестовой оплаты используйте тестовые ключи Stripe.

Тестовая карта:

```text
4242 4242 4242 4242
```

Любая будущая дата, любой CVC и любой ZIP.

## Статика

В Docker статика собирается автоматически через `collectstatic` и отдаётся через WhiteNoise.

Если запускаете проект вручную с `DJANGO_DEBUG=False`, выполните:

```bash
python manage.py collectstatic --noinput
```
