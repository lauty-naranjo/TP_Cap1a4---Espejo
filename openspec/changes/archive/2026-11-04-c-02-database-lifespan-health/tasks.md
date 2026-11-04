# Tasks

> Regla dura afectada por tarea se marca inline con `<!-- rn: … -->`. Verificación esperada por
> tarea en su propio bullet (norma del schema). Nota TDD: el orquestador corre Strict TDD en el apply.

## 1. Ciclo de vida de la base y sesión por petición (US-101)

- [x] 1.1 Escribir test de arranque que ejercite el lifespan: con `DATABASE_URL` presente el motor y
  la sessionmaker se crean y se guardan en `app.state`, y al salir del contexto se cierra el motor
  (US-101 CA-1)
  - Verificación: test rojo falla contra lifespan vacío de C-01; luego implementación lo completa.
- [x] 1.2 Implementar `app/core/database.py`: fábrica de `create_async_engine` y `async_sessionmaker`
  con `expire_on_commit=False`, y dependencia `get_session` que abre/cierra la sesión (US-101 CA-2)
  <!-- rn: solo DATABASE_URL se lee del entorno; nada más de config (sin pydantic-settings) -->
  - Verificación: `python -c "import app.core.database"` corre limpio; la sesión sale con
    `expire_on_commit=False`.
- [x] 1.3 Implementar el lifespan en `app/main.py`: crear motor + sessionmaker en `app.state`,
  registrar routers y cerrar el motor con `engine.dispose()` al apagar (US-101 CA-1)
  <!-- rn: todo handler futuro async def; nada de DB ni lógica fuera del lifespan -->
  - Verificación: `python -c "import app.main"` corre sin errores y `app.main.app` es FastAPI;
    shutdown ejecuta dispose.

## 2. Health checks del servicio (US-102, RN-HL-01/RN-HL-02)

- [x] 2.1 Implementar `GET /health/live`: responde 200 con `{"estado": "vivo"}` sin tocar la base
  (RN-HL-01)
  - Verificación: test que la endpoint responde 200 sin conexión a la base.
- [x] 2.2 Implementar `GET /health/ready`: ejecuta `SELECT 1` y responde 200 si la base contesta,
  503 si no (RN-HL-02, US-102 CA-1/CA-2)
  - Verificación: con base caída responde 503; con base viva responde 200.
- [x] 2.3 Tests del módulo health: live responde aunque la DB esté caída; ready responde 503 con la DB
  caída (caso C-09 reutiliza `/health/live` bajo concurrencia)
  - Verificación: `pytest` verde (DB de prueba real; sin mocks de DB según python-testing-patterns).

## 3. Integración final del change

- [x] 3.1 Smoke end-to-end: `uvicorn app.main:app` con `.env` placeholder → `/health/live` responde
  200; `/health/ready` responde 503 (la base no es alcanzable desde este entorno)
  - Verificación: secuencia de arranque/chequeo manual; sin rutas de dominio registradas aún.

## Workflow follow-up

- `/opsx:verify c-02-database-lifespan-health` y luego `/opsx:archive c-02-database-lifespan-health`.
- Marcar `[x]` en la entrada `[C-02]` de `CHANGES.md`.
- Siguiente change del camino crítico: `/opsx:propose c-03-domain-models` (CLI: nombre en minúsculas:
  `c-03-domain-models`).
