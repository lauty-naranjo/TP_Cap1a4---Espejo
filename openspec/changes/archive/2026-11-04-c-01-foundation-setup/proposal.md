# Proposal — c-01-foundation-setup

> Nota de naming: el CLI de openspec exige kebab-case en minúsculas; `C-01-foundation-setup`
> (CHANGES.md) se registra acá como `c-01-foundation-setup`. Es el mismo change del roadmap.

## Why

El roadmap de la API Veterinaria (TP Programación III, Cap. 1 a 4) necesita un primer change que
deje el esqueleto del repositorio con la estructura **exacta** que dicta la consigna. Sin ese
andamiaje los changes de dominio (C-02 en adelante) no tienen dónde vivir: ni `app/core/config.py`
para leer `DATABASE_URL` (US-103 CA-1), ni la convención de módulos
`app/modules/<módulo>/{models,schemas,service,router}.py`, ni el `requirements.txt` con el stack
pinneado que se corrige como criterio de evaluación.

## What Changes

- Estructura de directorios exacta de la consigna:
  - `app/main.py` — app FastAPI mínima con hook `lifespan` vacío, listo para que C-02 cree motor
    y sessionmaker. Sin routers registrados.
  - `app/core/config.py` — lee `DATABASE_URL` desde `.env` vía python-dotenv (US-103 CA-1);
    **falla en el arranque si falta**.
  - `app/modules/<módulo>/` — carpetas placeholder para los 6 módulos mínimos
    (`health`, `duenios`, `mascotas`, `practicas`, `turnos`, `laboratorio`) con sus archivos
    vacíos (`models.py`, `schemas.py`, `service.py`, `router.py`) y `__init__.py`, para que la
    estructura quede fijada desde el día 1 (FichaDuenio vivirá en `duenios`, TurnoPractica en
    `turnos`; `laboratorio` sin `models.py` — IN-02).
  - `test/` — carpeta vacía con `.gitkeep` (los casos `.http`/`.sql` son de C-10).
  - `reiniciar.py` — placeholder que explota con `NotImplementedError` (el borrado/`create_all`/seed
    real es de C-04).
- `requirements.txt` con el stack dictado (DD-01): Python 3.12 + `fastapi[standard]>=0.111`
  (incluye uvicorn) + `sqlmodel>=0.0.24` + `sqlalchemy[asyncio]>=2.0` + `asyncpg>=0.30` +
  `python-dotenv>=1.0` (SU-07: un único `requirements.txt`, sin lockfile).
- `env.example` con la forma `postgresql+asyncpg://usuario:password@localhost:5432/veterinaria`
  **sin ningún secreto** (US-103 CA-2).
- `.gitignore` que excluye `.env` (+ artefactos Python estándar): `.env` nunca se versiona y
  **cero credenciales reales** en el repo.
- Todo importable: `python -c "import app.main"` sin errores y `uvicorn app.main:app` arranca
  (evidencia necesaria para la condición de corrección de la cátedra).

**Fuera de alcance (deliberado, corresponde a changes siguientes):**
- `app/core/database.py`, `lifespan` con motor/sessionmaker, `get_session` → **C-02**.
- Routers y endpoints de health (`/health/live`, `/health/ready`) → **C-02**.
- Modelos, restricciones y relaciones → **C-03**. Seed de `reiniciar.py` → **C-04**.
- Lógica de servicios, routers de dominio y casos `.http`/`.sql` → **C-05..C-10**.
- README de entrega → **C-11**.

## Capabilities

### New Capabilities
- `project-configuration`: configuración por entorno del servicio — lectura de `DATABASE_URL`
  desde `.env` vía python-dotenv, falla en el arranque si falta, `env.example` sin secretos y
  `.env` excluido del versionado (US-103).

### Modified Capabilities
<!-- Vacío: primer change del proyecto, no hay capabilities existentes. -->

## Impact

- **Código**: crean los archivos raíz del proyecto (`app/`, `app/core/config.py`, `app/main.py`,
  módulos placeholder, `reiniciar.py`, `requirements.txt`, `env.example`, `.gitignore`).
- **Sin endpoints públicos todavía**: la app no expone rutas (las health checks llegan en C-02).
- **Sin base de datos**: C-01 no toca PostgreSQL ni conecta al motor — solo lee la variable.
- **Dependencias**: define el pinning de todo el stack del TP; versiones mínimas con `>=`
  (riesgo de infra, `08_arquitectura_propuesta.md` §Riesgos).
- **Gobernanza/reglas duras que muerden primero**: estructura de consigna intocable,
  `.env` no versionado, `env.example` sin secretos, cero credenciales en el repo.
