# SciCalc Pro — Backend

## Setup rápido

```bash
# 1. Instalar dependencias (requiere Python 3.11+)
pip install -e ".[dev]"

# 2. Levantar PostgreSQL
docker-compose up -d postgres

# 3. Ejecutar migraciones
alembic upgrade head

# 4. Correr el servidor
uvicorn src.main:app --reload --port 8000
```

## Ejecutar pruebas unitarias

```bash
cd backend
pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml
```

## Pruebas incluidas (mínimo 7)

| # | Archivo | Prueba |
|---|---------|--------|
| 1 | test_arithmetic.py | Aritmética básica + división por cero |
| 2 | test_trig_deg.py | Trigonometría modo DEG |
| 3 | test_trig_rad.py | Trigonometría modo RAD con mpmath |
| 4 | test_regex_validators.py | Validación Regex (email, password, expresión, UUID) |
| 5 | test_history_crud.py | CRUD historial + FIFO 50 registros |
| 6 | test_jwt_auth.py | JWT generación/validación/expiración + bcrypt |
| 7 | test_sync_lww.py | Resolución de conflictos LWW |

## Arquitectura

```
src/
├── domain/          ← Núcleo puro (sin dependencias externas)
│   ├── engine/      ← Lexer → Parser → Evaluator
│   ├── entities/    ← Calculation, User, Profile
│   ├── value_objects/
│   ├── ports/       ← Interfaces abstractas (ABC)
│   └── exceptions/
├── application/     ← Casos de uso + DTOs + Validators
└── infrastructure/  ← FastAPI, SQLAlchemy, JWT, bcrypt
```

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| DATABASE_URL | postgresql+asyncpg://scicalc:secret@localhost:5432/scicalc | URL de PostgreSQL |
| SECRET_KEY | dev-secret-key-... | Clave JWT (cambiar en producción) |
| ACCESS_TOKEN_EXPIRE_MINUTES | 15 | TTL del access token |
| REFRESH_TOKEN_EXPIRE_DAYS | 7 | TTL del refresh token |

## Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /api/v1/auth/register | Registrar usuario |
| POST | /api/v1/auth/login | Login → tokens JWT |
| POST | /api/v1/calculate | Evaluar expresión matemática |
| GET | /api/v1/history | Historial del usuario |
| DELETE | /api/v1/history/{id} | Borrado lógico de historial |
| GET | /health | Health check |
