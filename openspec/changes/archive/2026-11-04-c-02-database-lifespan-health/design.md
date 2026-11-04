# Design — c-02-database-lifespan-health

## Context

El change C-01 dejó la aplicación FastAPI con `app/core/config.py` (fail-fast de `DATABASE_URL`,
DD-02/D2), `app/main.py` (lifespan vacío, D4) y módulos placeholder. Falta el wiring del ciclo de
vida de la base y los health checks que la consigna exige en el Ejercicio 1 (US-101, US-102).

Los flujos de `knowledge-base/07_flujos_principales.md` definen el comportamiento objetivo:

- **Flujo 1 (arranque/apagado)**: el lifespan crea el motor asincrónico (`create_async_engine` con
  `DATABASE_URL`) y la fábrica de sesiones (`async_sessionmaker`), los guarda en `app.state`; registra
  los routers y, al apagar, cierra el motor (`engine.dispose()`).
- **Flujo 2 (sesión por petición)**: cualquier request resuelve `Depends(get_session)` → una sesión
  nueva por petición (creada con `expire_on_commit=False`); el handler delega en el service pasándole
  la sesión.
- **Flujo 13 (health)**: `GET /health/live` no toca la base → `{"estado": "vivo"}` 200 (RN-HL-01);
  `GET /health/ready` ejecuta `SELECT 1` → 200 si la base contesta, 503 si no (RN-HL-02).

Stack y reglas duras aplicables: todo handler `async def` (RN-AS-01), cero lazy loading
(`MissingGreenlet`), `IntegrityError` → 409, dinero en `Decimal`/`NUMERIC`, sin auth/RBAC, sin
Alembic (DD-03).

## Goals / Non-Goals

**Goals:**
- Crear el motor async + sessionmaker en el lifespan y guardarlos en `app.state`; dispose al apagar.
- Proveer `get_session` (una sesión nueva por petición, `expire_on_commit=False`).
- Exponer `/health/live` y `/health/ready` con los códigos de respuesta de la consigna.

**Non-Goals:**
- Endpoints de dominio (C-05+); modelos/relaciones (C-03); seed/reiniciar (C-04); tests de casos
  `.http` (C-10); README de entrega (C-11).
- Auth/RBAC, Alembic/repositorios/UoW, lazy loading, float money, precio/total del cliente, validación
  previa de unicidad — todas fuera de alcance por reglas duras.

## Decisions

### D1 — `app/core/database.py` expone las piezas de infraestructura
- `create_async_engine(DATABASE_URL, ...)` — sin `echo` en el engine de producción (la evidencia
  `echo=True` es para los tests de C-08).
- `async_sessionmaker(engine, expire_on_commit=False)`.
- `get_session`: dependencia async con `yield` que abre la sesión del sessionmaker y la cierra al
  finalizar la petición.

### D2 — El lifespan crea el motor y la sessionmaker y los guarda en `app.state`
- `app.state.engine` y `app.state.sessionmaker` (nombres fijados por el Flujo 1 de la consigna).
- En shutdown: `await engine.dispose()` (libera el pool).

### D3 — Registro de routers dentro del lifespan vía `app.include_router`
- Solo el router de `health` existe en este change; los routers de dominio se registran en sus
  changes correspondientes (C-05+). Se agregan con `include_router` dentro del lifespan, siguiendo el
  Flujo 1 de la consigna.

### D4 — Health checks con códigos exactos de la consigna
- `GET /health/live`: 200 con `{"estado": "vivo"}`, sin tocar la base (RN-HL-01).
- `GET /health/ready`: ejecuta `SELECT 1`; 200 con `{"estado": "listo"}` si contesta, 503 con
  `{"estado": "no_disponible"}` si no (RN-HL-02). El detalle del error queda en el log, no en la respuesta.

### D5 — Sin configuración adicional
- Solo `DATABASE_URL` (variable única exigida, KB `08_arquitectura_propuesta.md` §Variables de
  entorno). Tamaño de pool u otros settings se documentan para futuras implementaciones, no entran al TP.

## Risks / Trade-offs

- [El engine async no conecta de forma eager] → una URL malformada puede no fallar hasta la primera
  query → el fail-fast de ausencia ya cubierto por `config.py`; la validación de formato queda como
  riesgo conocido (fuera del alcance de este change).
- [Health check con base caída] → el `SELECT 1` puede tardar → sin timeout explícito (consigna no lo
  pide); se acepta el coste para el TP.

## Migration Plan

- Sin cambios de esquema (DD-03: `create_all` en C-04, sin Alembic).
- Secuencia de implementación: `app/core/database.py` → lifespan en `app/main.py` → health router →
  tests → smoke con uvicorn. Sin pasos de migración de datos; rollback = revertir código (no hay estado
  de BD afectado).

## Open Questions

- Ninguna que bloquee el alcance. QA-03 (mecanismo del offload del laboratorio) queda abierta para C-09
  y no bloquea a C-02.
