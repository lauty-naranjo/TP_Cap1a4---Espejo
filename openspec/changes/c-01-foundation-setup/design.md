# Design — c-01-foundation-setup

## Context

Repositorio recién fundado: no existe código fuente todavía (ver estado en `.active-orchestrator-state.json`
— `step: done`, primer change del roadmap de `CHANGES.md`). La estructura del proyecto y el stack son
**dictados** por la consigna (DD-01, `08_arquitectura_propuesta.md` §Estructura de directorios); este
change solo andamia, no conecta base de datos ni registra routers. Skill de referencia resuelta del
registry (`.atl/skill-registry.md`): `fastapi-templates` — su estructura canónica de template se
**adapta al patrón `app/modules/<entidad>/*` que la KB exige**; sus compact rules que aplican:
requirements ya pinneados por el proyecto (no sugerir upgrades), `fastapi[standard]` trae uvicorn
incluido, separación schemas/models futura (C-03+).

## Goals / Non-Goals

**Goals:**
- Árbol de archivos EXACTO de la consigna, presentes desde el primer commit de código.
- Stack completo instalable con `pip install -r requirements.txt` sobre Python 3.12.
- Configuración por entorno funcional y verificable: `DATABASE_URL` se lee de `.env` vía
  python-dotenv; falta variable → arranque aborta con error claro (US-103 CA-1/CA-2).
- `python -c "import app.main"` sin errores; `uvicorn app.main:app` arranca y responde.
- `.env` excluido del versionado; cero credenciales reales en el repo.

**Non-Goals:**
- `app/core/database.py` (motor, sessionmaker, `get_session`) → C-02.
- `lifespan` con lógica (crear/cerrar motor) → C-02; acá el hook queda vacío.
- Endpoints de any kind (health `/health/live`, `/health/ready` → C-02; dominio → C-05+).
- Modelos, schemas de dominio, lógica de services, seed → C-03/C-04.
- README de entrega, casos `.http`/`.sql` → C-10/C-11.

## Decisions

### D1 — Placeholder full de la estructura de consigna (no crecimiento incremental)
Se crean los 6 módulos mínimos (`health`, `duenios`, `mascotas`, `practicas`, `turnos`,
`laboratorio`) con sus archivos vacíos + `__init__.py`, según el árbol de la consigna:
- todos los módulos: `models.py`, `schemas.py`, `service.py`, `router.py` vacíos;
- `health`: solo `router.py` (sin models/schemas/service — la consigna lo lista así);
- `laboratorio`: `cliente.py` (⚠ lo entrega la cátedra, SU-05: placeholder con comentario,
  NO se implementa), `service.py`, `router.py` — **sin `models.py`** (IN-02: no hay
  persistencia en ese módulo).
- *Alternativa descartada*: crear solo `main.py` y que cada change agregue sus archivos —
  el corrector compara contra la estructura dictada; dejarla fijada y verificable acá reduce
  el riesgo de desvío de nombres/ubicaciones (regla dura: `FichaDuenio` en `duenios`,
  `TurnoPractica` en `turnos`).
- Los archivos vacíos quedan ocupados por C-02..C-09 (todo module placeholder tiene change
  asociado — cero huérfanos).

### D2 — `app/core/config.py`: python-dotenv plano, `get_settings()` mínima
`load_dotenv()` + `os.getenv("DATABASE_URL")`; sin `DATABASE_URL` → `RuntimeError` con mensaje
que diga «DATABASE_URL no definida — copiar env.example a .env».
- *Alternativa descartada*: `pydantic-settings` (lleva una dependencia extra que la consigna no
  pide; regla dura: solo `DATABASE_URL` se lee del entorno — nada más de config).
- Cargar pereza: se llama al importarse `app.main`, garantizando el fail-fast **antes** de que
  uvicorn termine el arranque.

### D3 — Pinning `>=` versiones mínimas de la tabla de la consigna
```
fastapi[standard]>=0.111
sqlmodel>=0.0.24
sqlalchemy[asyncio]>=2.0
asyncpg>=0.30
python-dotenv>=1.0
```
Python 3.12 exigido en el README de entrega (C-11) y en ejecución local, no como paquete.
`fastapi[standard]` incluye `uvicorn` (consigna: «el que instala fastapi[standard]»).
- *Alternativa descartada*: lockfile o versiones exactas (==) — SU-07 (alta confianza) dice
  un único `requirements.txt` sin lockfile; `>=` es lo que la rúbrica espera en este TP.
- El extra `[asyncio]` de SQLAlchemy pide Greenlet, necesario para el driver asincrónico.

### D4 — `app/main.py` mínimo con `lifespan` vacío
`FastAPI()` + `@asynccontextmanager` de lifespan con solo `yield` (sin motor, sin routers),
cuerpo comentado indicando que C-02 lo completa. Sin `docs_url` custom ni middleware.
- *Alternativa descartada*: adelantar el motor la sesión acá "para aprovechar" — rompe la
  atomicidad de C-02 y mezcla governance (C-01 es BAJO, sin DB).

### D5 — `reiniciar.py` placeholder explícito
`reiniciar.py` con raise `NotImplementedError` y mensaje «implementado en C-04». Así el formato
de entrega (raíz del repo) queda fijado y `python reiniciar.py` no remonta un borrado parcial
accidental de tablas antes de que los modelos existan (C-03).

### D6 — `.gitignore` mínimo y no ambiguo
Excluye: `.env`, `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, artefactos de pytest/cache.
`env.example` y `.gitkeep` **no** quedan excluidos (patrones específicos, no `\*.example`).
- Nota de entorno: el workspace todavía no es un repo git — el `.gitignore` se crea igual
  (entregable C-01); la primera inicialización de git lo usará.

## Estructura resultante (contrato de este change)

```
proyecto/
├── app/
│   ├── main.py                     # mínimo: FastAPI + lifespan vacío (C-02 lo completa)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py               # DATABASE_URL desde .env; fail-fast si falta
│   └── modules/
│       ├── __init__.py
│       ├── health/                 # solo router.py (consigna)
│       │   ├── __init__.py
│       │   └── router.py
│       ├── duenios/                # models.py, schemas.py, service.py, router.py (vacíos)
│       ├── mascotas/               # ídem
│       ├── practicas/              # ídem
│       ├── turnos/                 # ídem (TurnoPractica vivirá acá)
│       └── laboratorio/
│           ├── __init__.py
│           ├── cliente.py          # placeholder — lo entrega la cátedra (SU-05)
│           ├── service.py
│           └── router.py
├── test/
│   └── .gitkeep                    # los .http/.sql son de C-10
├── reiniciar.py                    # placeholder NotImplementedError (C-04)
├── requirements.txt
├── env.example
└── .gitignore
```

## Risks / Trade-offs

- [Placeholders vacíos «muertos» si un change posterior no los llena] → verificado cruzando
  con CHANGES.md: cada módulo placeholder tiene change asignado (C-02..C-09); se agrega en
  tasks.md el checklist de mapeo.
- [Fail-fast de config complica smoke-tests en CI sin `.env`] → los tests de esta fase
  documenta la variable o usan el fixture de entorno; el servicio en operación siempre arranca
  con `.env` presente (verificación: arranque con variable presente OK, sin ella RuntimeError).
- [Pinning `>=` permite drift silencioso de versiones] → SU-07 aprueba el tradeoff; el README
  de entrega (C-11) fija las versiones observadas en la máquina de corrección.
- [El repo aún no es git] → `.gitignore` funciona igual al inicializarlo; sin `git init`
  automático en este change (commits solo con pedido explícito del usuario — regla universal).

## Open Questions

Ninguna que bloquee el scope: QA-01/QA-03/QA-06 quedan para los changes que los consumen
(C-06 SU-06, C-09 DD-07, C-11 QA-06); ninguno afecta el andamiaje.
