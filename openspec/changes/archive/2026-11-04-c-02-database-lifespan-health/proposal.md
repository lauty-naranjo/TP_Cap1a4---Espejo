# Proposal — c-02-database-lifespan-health

> Nota de naming: el CLI de openspec exige kebab-case en minúsculas; `C-02-database-lifespan-health`
> (CHANGES.md) se registra acá como `c-02-database-lifespan-health`. Es el mismo change del roadmap.

## Why

El change C-01 dejó la aplicación FastAPI con configuración fail-fast (`app/core/config.py`) y un
lifespan vacío, pero sin motor asíncrono ni fábrica de sesiones, ni endpoints de salud. Sin el wiring
del ciclo de vida de la base (lifespan) y de los health checks, el servicio no puede atender ninguna
consulta de dominio, y la consigna (Ejercicio 1, Flujo 1/2/13) no puede verificarse: los changes de
dominio posteriores (C-03 en adelante) dependen de este andamiaje (camino crítico C-01 → C-02 → C-03).

## What Changes

- `app/core/database.py` (nuevo): fábrica de `create_async_engine` y `async_sessionmaker` con
  `expire_on_commit=False`, más la dependencia `get_session` (una sesión nueva por petición, Flujo 2).
- `app/main.py`: el lifespan crea motor + sessionmaker, los guarda en `app.state`, registra los
  routers de la app y cierra el motor con `engine.dispose()` al apagar (US-101 CA-1, Flujo 1).
- `app/modules/health/router.py`: `GET /health/live` → `{"estado": "vivo"}` 200 sin tocar la base
  (RN-HL-01, US-102); `GET /health/ready` → `SELECT 1`, 200 si la base contesta y **503** si no
  (RN-HL-02, US-102 CA-1/CA-2).

## Capabilities

### New Capabilities
- `database-lifespan`: ciclo de vida del motor asíncrono y de la sesión con la aplicación
  (US-101 CA-1/CA-2).
- `service-health`: health checks de liveness y readiness del servicio (US-102, RN-HL-01/RN-HL-02).

### Modified Capabilities
- Ninguna: el comportamiento de configuración por entorno (`project-configuration`, change C-01) no
  cambia en este change; el motor consume el `DATABASE_URL` ya validado y fail-fast.

## Impact

- **Código**: crean/actualizan `app/core/database.py`, `app/main.py` y `app/modules/health/router.py`.
- **API**: nacen los endpoints `GET /health/live` y `GET /health/ready`.
- **Dependencias**: ninguna nueva (stack ya fijado en C-01, DD-01).
- **Base de datos**: sin cambios de esquema (DD-03: `create_all` en C-04; sin Alembic).
- **Gobernanza**: nivel MEDIO → implementación con checkpoints.
