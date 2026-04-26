# Lead Processing Backend

Два незалежні FastAPI-сервіси для прийому, фонової обробки, дедуплікації та аналітики лідів.

Структура проекту:

- `landings` — сервіс прийому лідів з лендингів.
- `core` — основний сервіс для фонової обробки лідів та видачі аналітики.

Сервіси взаємодіють між собою тільки через Redis.

Для спрощення тестового завдання та уникнення зайвої інфраструктурної складності (наприклад, реалізації кешування офферів/аффілейтів у Redis або gRPC/HTTP спілкування між сервісами), мікросервіси фізично використовують одну базу даних PostgreSQL і загальні моделі SQLAlchemy. У реальному production-оточенні для забезпечення повної незалежності сервіс офферів реплікувалися б у Redis, щоб landings міг працювати автономно навіть у разі падіння БД core.

## Технологічний стек

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy 2 async
- asyncpg
- Alembic
- Redis
- JWT
- Docker Compose

## Можливості

- Bearer JWT authentication.
- Перевірка affiliate за `id` з JWT payload.
- Прийом лідів через API.
- Валідація вхідних даних.
- Redis-черга для передачі лідів між сервісами.
- Фоновий worker для обробки лідів.
- Дедуплікація лідів протягом 10 хвилин.
- Збереження лідів у PostgreSQL.
- Аналітика з групуванням за датою або оффером.
- Alembic-міграції.
- Swagger-документація через FastAPI.

## Структура проєкту

```text
lead-processing-backend/
  landings/
    app/
      api/
      core/
      schemas/
      services/
  core/
    app/
      api/
      core/
      db/
      schemas/
      services/
      worker.py
  alembic/
  scripts/
  docker-compose.yml
  requirements.txt
  README.md
```

## Основна логіка

### `landings`

Сервіс `landings` відповідає за прийом лідів з лендингів.

Endpoint:

```http
POST /lead
```

Сервіс:

1. Перевіряє Bearer JWT token.
2. Дістає `affiliate_id` з payload токена.
3. Перевіряє, що такий affiliate існує в БД.
4. Перевіряє, що `affiliate_id` з тіла запиту збігається з `id` з токена.
5. Перевіряє, що `offer_id` існує.
6. Кладе прийнятий лід у Redis-чергу.
7. Повертає відповідь `200 OK`.

### `core`

Сервіс `core` складається з API та фонового worker-а.

Worker:

1. Читає ліди з Redis-черги.
2. Перевіряє дедуплікацію.
3. Якщо лід не є дублікатом — записує його в PostgreSQL.
4. Якщо лід є дублікатом — пропускає його.

API:

```http
GET /leads
```

Повертає аналітику по лідах для affiliate, який визначається з Bearer JWT token.

Підтримується групування:

- `group=date` — за датою додавання ліда.
- `group=offer` — за оффером.

## Модель даних

Обов'язкові таблиці:

### `affiliates`

```text
id
name
```

### `offers`

```text
id
name
```

### `leads`

```text
id
name
phone
country
offer_id
affiliate_id
created_at
```

Поле `created_at` зберігає дату та час додавання ліда в БД.

## Змінні середовища

Створіть файл `.env` у корені проекту:

```env
POSTGRES_DB=leads_db
POSTGRES_USER=leads_user
POSTGRES_PASSWORD=leads_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433

DATABASE_URL=postgresql+asyncpg://leads_user:leads_password@127.0.0.1:5433/leads_db

REDIS_URL=redis://localhost:6379/0
REDIS_LEADS_QUEUE=leads_queue

JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256

LANDINGS_HOST=0.0.0.0
LANDINGS_PORT=8001

CORE_HOST=0.0.0.0
CORE_PORT=8002
```

> PostgreSQL проброшений на host-порт `5433`, щоб уникнути можливого конфлікту з локальним PostgreSQL на Windows.

## Локальний запуск

### 1. Створити та активувати virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Встановити залежності

```powershell
pip install -r requirements.txt
```

### 3. Запустити PostgreSQL та Redis

```powershell
docker compose up -d
```

Перевірити контейнери:

```powershell
docker ps
```

Очікувані контейнери:

```text
leads_postgres
leads_redis
```

### 4. Запустити міграції

```powershell
alembic upgrade head
```

### 5. Додати тестові дані

```powershell
python -m scripts.seed
```

Скрипт створює тестові записи:

```text
Affiliates: 1, 2
Offers: 1, 2
```

### 6. Створити JWT token

```powershell
python -m scripts.create_token --affiliate-id 1
```

Отриманий token потрібно використовувати в заголовку:

```http
Authorization: Bearer <token>
```

## Запуск сервісів

Для локальної розробки потрібно запустити три процеси в окремих терміналах.

### Terminal 1 — Landings service

```powershell
uvicorn landings.app.main:app --reload --port 8001
```

Swagger:

```text
http://127.0.0.1:8001/docs
```

### Terminal 2 — Core API service

```powershell
uvicorn core.app.main:app --reload --port 8002
```

Swagger:

```text
http://127.0.0.1:8002/docs
```

### Terminal 3 — Core worker

```powershell
python -m core.app.worker
```

Worker читає Redis-чергу та записує ліди в PostgreSQL.

## API usage

### Прийом ліда

```http
POST /lead
Authorization: Bearer <token>
Content-Type: application/json
```

Request body:

```json
{
  "name": "Oleksii",
  "phone": "+380982342123",
  "country": "UA",
  "offer_id": 1,
  "affiliate_id": 1
}
```

Response:

```json
{
  "status": "accepted"
}
```

PowerShell example:

```powershell
$token = "PASTE_TOKEN_HERE"

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8001/lead" `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{
    "name": "Oleksii",
    "phone": "+380982342123",
    "country": "UA",
    "offer_id": 1,
    "affiliate_id": 1
  }'
```

## Аналітика лідів

### Групування за датою

```http
GET /leads?date_from=2026-04-24&date_to=2026-04-25&group=date
Authorization: Bearer <token>
```

PowerShell example:

```powershell
$response = Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:8002/leads?date_from=2026-04-24&date_to=2026-04-25&group=date" `
  -Headers @{ Authorization = "Bearer $token" }

$response | ConvertTo-Json -Depth 10
```

Response example:

```json
{
  "group_by": "date",
  "items": [
    {
      "group": "2026-04-24",
      "count": 1,
      "leads": [
        {
          "id": 1,
          "name": "Oleksii",
          "phone": "+380982342123",
          "country": "UA",
          "offer_id": 1,
          "affiliate_id": 1,
          "created_at": "2026-04-24T21:21:17.503491Z"
        }
      ]
    }
  ]
}
```

### Групування за оффером

```http
GET /leads?date_from=2026-04-24&date_to=2026-04-25&group=offer
Authorization: Bearer <token>
```

PowerShell example:

```powershell
$response = Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:8002/leads?date_from=2026-04-24&date_to=2026-04-25&group=offer" `
  -Headers @{ Authorization = "Bearer $token" }

$response | ConvertTo-Json -Depth 10
```

Response example:

```json
{
  "group_by": "offer",
  "items": [
    {
      "group": "1: Test Offer",
      "count": 1,
      "leads": [
        {
          "id": 1,
          "name": "Oleksii",
          "phone": "+380982342123",
          "country": "UA",
          "offer_id": 1,
          "affiliate_id": 1,
          "created_at": "2026-04-24T21:21:17.503491Z"
        }
      ]
    }
  ]
}
```

## Дедуплікація

Дедуплікація виконується у `core worker`.

Лід вважається дублікатом, якщо протягом останніх 10 хвилин уже був оброблений лід з такими самими полями:

```text
name + phone + offer_id + affiliate_id
```

Для цього використовується Redis atomic operation:

```text
SET key value NX EX 600
```

- `NX` — встановити ключ тільки якщо його ще немає.
- `EX 600` — TTL 600 секунд, тобто 10 хвилин.

Якщо ключ уже існує, worker пропускає лід і не записує його в PostgreSQL.

## Перевірка дедуплікації

1. Запустіть `landings`, `core API`, `core worker`.
2. Надішліть два однакових `POST /lead` запити.
3. Обидва запити повернуть:

```json
{
  "status": "accepted"
}
```

4. У логах worker буде:

```text
Lead saved: id=...
Duplicate lead skipped: {...}
```

5. У PostgreSQL буде записаний тільки один лід.

## Перевірка Redis-черги

Перевірити довжину черги:

```powershell
docker exec -it leads_redis redis-cli LLEN leads_queue
```

Подивитися елементи черги:

```powershell
docker exec -it leads_redis redis-cli LRANGE leads_queue 0 -1
```

Очистити чергу:

```powershell
docker exec -it leads_redis redis-cli DEL leads_queue
```

## Тестування

Запуск тестів:

```powershell
pytest