# SciCalc Pro — Guía de Ejecución

> **Sistema operativo**: Windows 11 con Git Bash
> **Python**: 3.12 en `C:\Users\Angel Puentes\AppData\Local\Programs\Python\Python312`
> **Prerequisitos**: Docker Desktop corriendo, Python 3.12 en PATH, Chrome instalado

---

## Índice

1. [Estructura del proyecto](#1-estructura-del-proyecto)
2. [Prerequisitos y configuración inicial](#2-prerequisitos-y-configuración-inicial)
3. [Levantar la base de datos](#3-levantar-la-base-de-datos)
4. [Backend — FastAPI](#4-backend--fastapi)
5. [Pruebas unitarias](#5-pruebas-unitarias)
6. [Pruebas de integración](#6-pruebas-de-integración)
7. [Pruebas E2E con Selenium](#7-pruebas-e2e-con-selenium)
8. [Cobertura combinada (meta >90%)](#8-cobertura-combinada-meta-90)
9. [SonarQube](#9-sonarqube)
10. [Pipeline CI/CD](#10-pipeline-cicd)
11. [Referencia de endpoints](#11-referencia-de-endpoints)
12. [Variables de entorno](#12-variables-de-entorno)
13. [Solución de problemas comunes](#13-solución-de-problemas-comunes)

---

## 1. Estructura del proyecto

```
SciCalcPro/                          ← RAÍZ del proyecto
│
├── .github/
│   └── workflows/
│       └── ci.yml                   ← Pipeline CI/CD (lint → unit → integration → E2E → Sonar)
├── docker-compose.yml               ← Define PostgreSQL + backend en Docker
├── sonar-project.properties         ← Configuración de SonarQube
├── PRD.md                           ← Documento de requerimientos (v5.0)
├── GUIA.md                          ← Este archivo
│
├── backend/                         ← Código Python / FastAPI
│   ├── pyproject.toml               ← Dependencias y configuración pytest
│   ├── alembic.ini                  ← Configuración de migraciones
│   ├── run.py                       ← Arranque del servidor (fix Windows asyncio)
│   ├── Dockerfile                   ← Imagen Docker del backend
│   ├── coverage.xml                 ← Reporte de cobertura (generado por pytest --cov)
│   │
│   ├── src/
│   │   ├── main.py                  ← FastAPI app + lifespan + CORS + /health
│   │   ├── domain/                  ← Lógica de negocio pura (sin dependencias externas)
│   │   │   ├── engine/              ← Lexer → Parser → Evaluador matemático (mpmath)
│   │   │   ├── entities/            ← Calculation, User, Profile
│   │   │   ├── value_objects/       ← AngleMode, Precision, Expression
│   │   │   ├── ports/               ← Interfaces abstractas (ABC) — input/output
│   │   │   └── exceptions/          ← DivisionByZeroError, UndefinedResultError, ValidationError
│   │   ├── application/             ← Casos de uso + DTOs + Validadores
│   │   │   ├── use_cases/           ← EvaluateExpression, ManageHistory, ManageUser
│   │   │   ├── dtos/                ← CalculationRequest (Pydantic+Regex), CalculationResponse
│   │   │   └── validators/          ← regex_validators.py (email, password, expresión, uuid)
│   │   └── infrastructure/          ← Implementaciones concretas
│   │       ├── adapters/
│   │       │   ├── input/
│   │       │   │   ├── fastapi_router.py   ← Endpoints REST /api/v1/*
│   │       │   │   ├── web_router.py       ← Páginas HTML /web/* (para Selenium)
│   │       │   │   ├── auth_middleware.py  ← JWT dependency get_current_user
│   │       │   │   ├── math_engine_adapter.py
│   │       │   │   └── templates/          ← login.html, register.html, calculator.html
│   │       │   └── output/
│   │       │       ├── postgres_history_repo.py
│   │       │       ├── postgres_user_repo.py
│   │       │       └── postgres_sync_repo.py
│   │       ├── persistence/
│   │       │   ├── database.py      ← Engine async SQLAlchemy + get_db()
│   │       │   ├── models/          ← 7 modelos ORM (users, profiles, calculation_history, ...)
│   │       │   └── migrations/      ← Scripts Alembic
│   │       └── security/
│   │           ├── jwt_handler.py   ← create_access_token, create_refresh_token, decode_token
│   │           └── password_hasher.py ← bcrypt hash + verify
│   │
│   └── tests/
│       ├── conftest.py              ← Fixtures en memoria (InMemoryHistoryRepo, InMemoryUserRepo)
│       ├── unit/                    ← 7 archivos, 80+ casos — NO requieren PostgreSQL
│       │   ├── test_arithmetic.py       ← RF-001
│       │   ├── test_trig_deg.py         ← RF-002 (DEG)
│       │   ├── test_trig_rad.py         ← RF-002 (RAD)
│       │   ├── test_regex_validators.py ← RNF-006
│       │   ├── test_history_crud.py     ← RF-003
│       │   ├── test_jwt_auth.py         ← RNF-006 (JWT)
│       │   └── test_sync_lww.py         ← Sincronización LWW
│       ├── integration/             ← Pruebas HTTP contra la app real + PostgreSQL
│       │   ├── conftest.py          ← AsyncClient (ASGITransport), test_user, auth_headers
│       │   ├── test_health_web.py   ← /health + páginas /web/*
│       │   ├── test_auth_api.py     ← register, login, /users/me, delete user
│       │   ├── test_calculate_api.py← POST /calculate (todas las variantes)
│       │   └── test_history_api.py  ← GET/DELETE /history
│       └── e2e/                     ← Selenium WebDriver (requieren Chrome + servidor live)
│           ├── conftest.py          ← live_server (uvicorn thread), Chrome driver, e2e_user
│           ├── test_web_pages.py    ← GET /web/* → HTTP 200 + DOM correcto
│           ├── test_auth_e2e.py     ← Registro / login vía formulario HTML
│           ├── test_calculator_e2e.py ← Cálculos, historial vía browser
│           └── selenium_main.py     ← Demo interactivo con Chrome visible (RF-001 a RF-008)
│
└── frontend/                        ← App web (prototipo)
    └── src/
        ├── components/
        ├── screens/
        ├── services/
        ├── store/
        ├── hooks/
        └── database/
```

---

## 2. Prerequisitos y configuración inicial

### 2.1 Python en PATH de Git Bash

Python 3.12 está instalado pero **no está en el PATH de Git Bash por defecto**. Agrégalo una sola vez:

```bash
# Ejecutar desde cualquier directorio
echo 'export PATH="/c/Users/Angel Puentes/AppData/Local/Programs/Python/Python312:/c/Users/Angel Puentes/AppData/Local/Programs/Python/Python312/Scripts:$PATH"' >> ~/.bashrc
echo 'export DATABASE_URL="postgresql+asyncpg://scicalc:secret@localhost:5434/scicalc"' >> ~/.bashrc
source ~/.bashrc
```

Verifica:

```bash
python --version    # Python 3.12.x
pip --version
alembic --version
pytest --version
```

### 2.2 Instalar dependencias del backend

```bash
# Directorio: SciCalcPro/backend/
cd backend
pip install -e ".[dev]"
```

Esto instala **todas** las dependencias: FastAPI, SQLAlchemy, pytest, selenium, webdriver-manager, etc.

---

## 3. Levantar la base de datos

```bash
# Directorio: SciCalcPro/   (raíz del proyecto, donde está docker-compose.yml)
docker-compose up -d postgres
```

| Detalle | Valor |
|---------|-------|
| Contenedor | `scicalc_postgres` |
| Base de datos | `scicalc` |
| Usuario | `scicalc` |
| Contraseña | `secret` |
| Puerto local | **5434** (no 5432, evita conflicto con PostgreSQL nativo de Windows) |

Verificar que está corriendo:

```bash
docker ps
# Debe aparecer: scicalc_postgres   Up   0.0.0.0:5434->5432/tcp
```

### 3.1 Aplicar migraciones (primera vez o después de cambios de schema)

```bash
# Directorio: SciCalcPro/backend/
alembic upgrade head
```

> **Nota**: Si no tienes `DATABASE_URL` en el `.bashrc`, usa:
> ```bash
> DATABASE_URL=postgresql+asyncpg://scicalc:secret@localhost:5434/scicalc alembic upgrade head
> ```

---

## 4. Backend — FastAPI

### 4.1 Modo desarrollo (recomendado en Windows)

```bash
# Directorio: SciCalcPro/backend/
python run.py
```

`run.py` configura `WindowsSelectorEventLoopPolicy` **antes** de arrancar uvicorn, lo que es obligatorio para que asyncpg funcione correctamente en Windows.

| Recurso | URL |
|---------|-----|
| API REST | http://localhost:8001/api/v1 |
| Documentación interactiva (Swagger) | http://localhost:8001/docs |
| Documentación alternativa (ReDoc) | http://localhost:8001/redoc |
| Health check | http://localhost:8001/health |
| Web login (Selenium) | http://localhost:8001/web/login |
| Web registro (Selenium) | http://localhost:8001/web/register |
| Web calculadora (Selenium) | http://localhost:8001/web/calculator |

### 4.2 Modo Docker completo (PostgreSQL + Backend juntos)

```bash
# Directorio: SciCalcPro/   (raíz)
docker-compose up --build
```

> En Docker, el backend corre en el mismo puerto 8000 pero con `--reload` habilitado.
> **No usar este modo en Windows para desarrollo** — el reload de uvicorn dentro del contenedor no tiene el problema del event loop, pero puede haber latencia extra.

### 4.3 Detener el servidor

```bash
# Ctrl+C en la terminal donde corre el servidor
# Para Docker:
docker-compose down
```

---

## 5. Pruebas unitarias

### 5.1 Ejecutar todas las pruebas unitarias

```bash
# Directorio: SciCalcPro/backend/
pytest tests/unit/ -v
```

### 5.2 Con reporte de cobertura (solo unit)

```bash
# Directorio: SciCalcPro/backend/
pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml
```

> **Cobertura esperada solo con unit/: ~42%** — para alcanzar el >90% correr unit + integration juntos (ver sección 8).

### 5.3 Un solo archivo

```bash
pytest tests/unit/test_arithmetic.py -v
pytest tests/unit/test_trig_deg.py -v
pytest tests/unit/test_jwt_auth.py -v
```

### 5.4 Qué prueba cada archivo

| Archivo | Qué verifica | Requiere PostgreSQL |
|---------|-------------|-------------------|
| `test_arithmetic.py` | `+`, `-`, `*`, `/`, `^`, precedencia, `DivisionByZeroError` | No |
| `test_trig_deg.py` | sin/cos/tan en grados, tolerancia 1e-10, tan(90°) = Indefinido | No |
| `test_trig_rad.py` | sin/cos/tan en radianes con mpmath | No |
| `test_regex_validators.py` | email, password, expresiones, UUID v4 | No |
| `test_history_crud.py` | CRUD historial, borrado lógico, FIFO 50 registros | No |
| `test_jwt_auth.py` | JWT generación/decodificación/expiración (freezegun), bcrypt | No |
| `test_sync_lww.py` | Resolución de conflictos Last Write Wins | No |

---

## 6. Pruebas de integración

Las pruebas de integración usan `httpx.AsyncClient` con `ASGITransport` — **no levantan un servidor real**, pero sí requieren PostgreSQL para persistencia.

### Prerequisitos

1. PostgreSQL corriendo (`docker-compose up -d postgres`)
2. Migraciones aplicadas (`alembic upgrade head`)
3. `DATABASE_URL` en el entorno

### 6.1 Ejecutar todas las pruebas de integración

```bash
# Directorio: SciCalcPro/backend/
pytest tests/integration/ -v
```

### 6.2 Con cobertura

```bash
pytest tests/integration/ -v --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml
```

### 6.3 Qué prueba cada archivo

| Archivo | Flujo cubierto | Módulos ejercidos |
|---------|--------------|-----------------|
| `test_health_web.py` | GET /health, GET /web/login, /register, /calculator | `main.py`, `web_router.py` |
| `test_auth_api.py` | Registro, login, /users/me, DELETE /users/{id}, errores | `fastapi_router.py`, `auth_middleware.py`, `postgres_user_repo.py` |
| `test_calculate_api.py` | POST /calculate: aritmética, trig, notación científica, errores, 422 | `fastapi_router.py`, `evaluate_expression.py`, `postgres_history_repo.py` |
| `test_history_api.py` | GET /history, DELETE /history/{id}, múltiples cálculos | `fastapi_router.py`, `postgres_history_repo.py`, `manage_history.py` |

### 6.4 Cómo funciona internamente

```
pytest inicia
  │
  ├─ client fixture → AsyncClient(ASGITransport(app))
  │    └─ lifespan del app se ejecuta → create_all en PostgreSQL
  │
  ├─ test_user fixture → POST /register + POST /login → token JWT
  │
  ├─ TEST: cliente envía petición HTTP directamente al app ASGI
  │    └─ sin servidor real, sin sockets — todo en memoria
  │
  └─ teardown: DELETE /users/{id} (borrado lógico)
```

---

## 7. Pruebas E2E con Selenium

Las pruebas E2E abren Chrome en modo headless y simulan un usuario real interactuando con las páginas web.

### Prerequisitos

1. **PostgreSQL corriendo** con migraciones aplicadas (sección 3)
2. **Backend corriendo** en `http://localhost:8000` — abrir en **otra terminal**: `python run.py`
3. **Chrome** instalado en el sistema
4. `webdriver-manager` descarga el ChromeDriver automáticamente

### 7.1 Ejecutar todos los tests E2E

```bash
# Directorio: SciCalcPro/backend/
pytest tests/e2e/ -v -m e2e
```

### 7.2 Por archivo

```bash
pytest tests/e2e/test_web_pages.py -v       # Páginas HTML → HTTP 200
pytest tests/e2e/test_auth_e2e.py -v        # Registro y login vía browser
pytest tests/e2e/test_calculator_e2e.py -v  # Cálculos e historial vía browser
```

### 7.3 Demo interactivo con Chrome visible

```bash
# Directorio: SciCalcPro/backend/
python tests/e2e/selenium_main.py
```

Abre Chrome en modo visual. Cubre RF-001 al RF-008 y RNF-006 paso a paso.

### 7.4 Qué prueba cada archivo E2E

| Archivo | Flujo probado |
|---------|--------------|
| `test_web_pages.py` | GET /web/login, /web/register, /web/calculator → HTTP 200 + DOM correcto |
| `test_auth_e2e.py` | Registro exitoso, email duplicado, login válido, contraseña incorrecta |
| `test_calculator_e2e.py` | `2+3*4=14`, `sin(90)=1`, expresión inválida, historial, borrar entrada |
| `selenium_main.py` | Demo completo RF-001 → RF-008 + RNF-006 con Chrome visible |

---

## 8. Cobertura combinada (meta >90%)

Para alcanzar la meta de cobertura del PRD, correr **unit + integration juntos**:

```bash
# Directorio: SciCalcPro/backend/
# Prerequisito: PostgreSQL corriendo + alembic upgrade head

pytest tests/unit/ tests/integration/ -v \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml
```

El archivo `coverage.xml` resultante es el que consume SonarQube.

> **No incluir `tests/e2e/`** en la medición de cobertura — los E2E requieren servidor live y se ejecutan por separado.

---

## 9. SonarQube

SonarQube analiza la calidad del código: bugs, vulnerabilidades, code smells, duplicaciones y cobertura.

### 9.1 Levantar el servidor SonarQube

```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:community
# Esperar ~2 minutos → http://localhost:9000  (admin / admin)
```

### 9.2 Generar cobertura combinada (paso previo obligatorio)

```bash
# Directorio: SciCalcPro/backend/
pytest tests/unit/ tests/integration/ \
  --cov=src \
  --cov-report=xml:coverage.xml
```

### 9.3 Ejecutar el análisis

**Opción A — sonar-scanner instalado:**
```bash
# Directorio: SciCalcPro/   (raíz)
sonar-scanner
```

**Opción B — Docker (sin instalar sonar-scanner):**
```bash
# Directorio: SciCalcPro/   (raíz)
docker run --rm \
  -e SONAR_HOST_URL="http://host.docker.internal:9000" \
  -e SONAR_LOGIN="<tu-token>" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli
```

### 9.4 Ver resultados

Abre: http://localhost:9000/dashboard?id=scicalc-pro

Métricas objetivo: Reliability **A** · Security **A** · Maintainability **A** · Coverage **>90%**

---

## 10. Pipeline CI/CD

El pipeline `.github/workflows/ci.yml` se ejecuta automáticamente en cada push a `main` o `develop`.

### Etapas

| # | Job | Qué hace | Bloqueante |
|---|-----|---------|-----------|
| 1 | `lint` | Análisis estático con ruff | Sí |
| 2 | `unit-tests` | pytest tests/unit/ con cobertura | Sí (necesita lint) |
| 3 | `integration-tests` | pytest unit+integration con PostgreSQL, falla si cobertura <90% | Sí (necesita lint) |
| 4 | `e2e-tests` | Selenium headless con Chrome | Necesita integration |
| 5 | `sonarqube` | Scan de calidad (requiere secrets SONAR_TOKEN y var SONAR_HOST_URL) | Necesita integration |

### Configurar secrets en GitHub

```
Repositorio → Settings → Secrets and variables → Actions
  SONAR_TOKEN     = <token generado en SonarQube: My Account → Security>

Repositorio → Settings → Secrets and variables → Variables
  SONAR_HOST_URL  = http://tu-servidor-sonar:9000
```

---

## 11. Referencia de endpoints

### Autenticación

| Método | Endpoint | Parámetros | Descripción |
|--------|----------|-----------|-------------|
| POST | `/api/v1/auth/register` | `email`, `password`, `display_name` (query params) | Registro → 201 |
| POST | `/api/v1/auth/login` | `username`, `password` (form data) | Login → JWT tokens |

### Cálculo (requiere JWT)

| Método | Endpoint | Body JSON | Descripción |
|--------|----------|----------|-------------|
| POST | `/api/v1/calculate` | `expression`, `angle_mode`, `precision_digits` | Evaluar expresión → `CalculationResponse` |

### Historial (requiere JWT)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/history` | Últimos 50 cálculos del usuario |
| DELETE | `/api/v1/history/{id}` | Borrado lógico |

### Usuario (requiere JWT)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Datos del usuario autenticado |
| DELETE | `/api/v1/users/{id}` | Borrado lógico |

### Web y sistema

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/web/login` | Página HTML de login |
| GET | `/web/register` | Página HTML de registro |
| GET | `/web/calculator` | Página HTML de calculadora |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI interactivo |
| GET | `/redoc` | ReDoc interactivo |

---

## 12. Variables de entorno

| Variable | Valor por defecto | Descripción |
|----------|------------------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://scicalc:secret@localhost:5434/scicalc` | URL de conexión a PostgreSQL |
| `SECRET_KEY` | `dev-secret-key-change-in-production-min-32-chars` | Clave para firmar JWT |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Duración del access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Duración del refresh token |

Configurarlas permanentemente en Git Bash (`~/.bashrc`):

```bash
echo 'export DATABASE_URL="postgresql+asyncpg://scicalc:secret@localhost:5434/scicalc"' >> ~/.bashrc
source ~/.bashrc
```

---

## 13. Solución de problemas comunes

### `asyncpg.exceptions.ConnectionDoesNotExistError` (WinError 64 / WinError 10054)

**Causa**: asyncpg en Windows usa `ProactorEventLoop` por defecto, incompatible con SCRAM-SHA-256.

**Solución A** — Usar `run.py` en lugar de `uvicorn` directo:
```bash
# Directorio: SciCalcPro/backend/
python run.py   # ← Configura WindowsSelectorEventLoopPolicy antes de uvicorn
```

**Solución B** — Para alembic, asegúrate de usar el puerto 5434 con `DATABASE_URL`:
```bash
DATABASE_URL=postgresql+asyncpg://scicalc:secret@localhost:5434/scicalc alembic upgrade head
```

---

### `pip: command not found` / `pytest: command not found` / `alembic: command not found`

**Causa**: Python no está en el PATH de Git Bash.

**Solución**:
```bash
echo 'export PATH="/c/Users/Angel Puentes/AppData/Local/Programs/Python/Python312:/c/Users/Angel Puentes/AppData/Local/Programs/Python/Python312/Scripts:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

### Puerto 5432 en uso (conflicto con PostgreSQL nativo de Windows)

**Causa**: Windows tiene PostgreSQL 17 nativo escuchando en 5432.

**Solución**: El `docker-compose.yml` ya usa el puerto **5434**. Siempre usar `localhost:5434` en `DATABASE_URL`.

Verificar qué proceso usa el puerto:
```bash
# En PowerShell (no Git Bash):
Get-NetTCPConnection -LocalPort 5432 | Select-Object OwningProcess
```

---

### Tests E2E fallan con `ConnectionRefusedError`

**Causa**: El backend no está corriendo antes de ejecutar los tests E2E.

**Solución**: Levanta el servidor primero en otra terminal:
```bash
# Terminal 1:
cd backend && python run.py

# Terminal 2:
cd backend && pytest tests/e2e/ -v -m e2e
```

---

### `DevToolsActivePort file doesn't exist` (Selenium/Chrome)

**Causa**: Chrome no puede arrancar en modo headless.

**Solución**: Verifica que Chrome está instalado:
```bash
# En Git Bash:
"/c/Program Files/Google/Chrome/Application/chrome.exe" --version
```

Si no está instalado, descárgalo desde https://www.google.com/chrome/

---

### `version is obsolete` en docker-compose

**Causa**: La propiedad `version` en `docker-compose.yml` es obsoleta en versiones recientes de Docker.

**Impacto**: Solo es un warning, no afecta el funcionamiento. Puedes ignorarlo o eliminar la línea `version: "3.9"` del archivo.

---

## Flujo completo de inicio rápido

```bash
# ── PRIMERA VEZ ──────────────────────────────────────────────────────────────

# 1. Configurar PATH y variables de entorno
echo 'export PATH="/c/Users/Angel Puentes/AppData/Local/Programs/Python/Python312:/c/Users/Angel Puentes/AppData/Local/Programs/Python/Python312/Scripts:$PATH"' >> ~/.bashrc
echo 'export DATABASE_URL="postgresql+asyncpg://scicalc:secret@localhost:5434/scicalc"' >> ~/.bashrc
source ~/.bashrc

# 2. Instalar dependencias
cd ~/Downloads/Universidad\ 2026/Métricas\ de\ Calidad\ de\ Software/SciCalcPro/backend
pip install -e ".[dev]"

# ── CADA VEZ QUE TRABAJAS ────────────────────────────────────────────────────

# 3. Levantar PostgreSQL
cd ~/Downloads/Universidad\ 2026/Métricas\ de\ Calidad\ de\ Software/SciCalcPro
docker-compose up -d postgres

# 4. Aplicar migraciones (solo si hay cambios en models/)
cd backend
alembic upgrade head

# 5. [TERMINAL 1] Arrancar el servidor
python run.py
# → http://localhost:8000/docs  (Swagger)
# → http://localhost:8000/web/calculator  (interfaz web)

# ── PRUEBAS ──────────────────────────────────────────────────────────────────

# 6. [TERMINAL 2] Pruebas unitarias (no requieren servidor)
cd ~/Downloads/Universidad\ 2026/Métricas\ de\ Calidad\ de\ Software/SciCalcPro/backend
pytest tests/unit/ -v

# 7. [TERMINAL 2] Pruebas de integración (requieren PostgreSQL, NO el servidor)
pytest tests/integration/ -v

# 8. [TERMINAL 2] Cobertura combinada unit + integration (genera coverage.xml)
pytest tests/unit/ tests/integration/ -v \
  --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml

# 9. [TERMINAL 2] Pruebas E2E Selenium (requieren servidor corriendo en TERMINAL 1)
pytest tests/e2e/ -v -m e2e

# 10. [TERMINAL 2] Demo Selenium con Chrome visible
python tests/e2e/selenium_main.py

# ── SONARQUBE ─────────────────────────────────────────────────────────────────

# 11. Levantar SonarQube (primera vez o si no está corriendo)
docker run -d --name sonarqube -p 9000:9000 sonarqube:community
# Esperar ~2 min → http://localhost:9000 (admin/admin)

# 12. Escanear (desde la raíz del proyecto, después del paso 8)
cd ~/Downloads/Universidad\ 2026/Métricas\ de\ Calidad\ de\ Software/SciCalcPro
sonar-scanner
# o con Docker:
# docker run --rm -e SONAR_HOST_URL="http://host.docker.internal:9000" \
#   -e SONAR_LOGIN="<token>" -v "$(pwd):/usr/src" sonarsource/sonar-scanner-cli
```
