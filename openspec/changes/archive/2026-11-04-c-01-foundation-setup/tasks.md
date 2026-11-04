# Tasks

> Regla dura afectada por tarea se marca inline con `<!-- rn: … -->`. Verificación esperada por
> tarea en su propio bullet (norma del schema). Nota TDD: el orquestador corre Strict TDD en el
> apply; las tareas 3.1/3.2 ya declaran el orden rojo→verde del test de fail-fast.

## 1. Dependencias e higiene del repositorio

- [x] 1.1 Crear `requirements.txt` con el stack pinneado de DD-01: `fastapi[standard]>=0.111`,
  `sqlmodel>=0.0.24`, `sqlalchemy[asyncio]>=2.0`, `asyncpg>=0.30`, `python-dotenv>=1.0`
  <!-- rn: stack dictado, un único requirements.txt sin lockfile (SU-07) → hacerlo tal cual -->
  - Verificación: `pip install -r requirements.txt` termina sin errores; `python -c "import fastapi, sqlmodel, sqlalchemy, asyncpg, dotenv"` corre limpio; `python -m uvicorn --version` responde.
- [x] 1.2 Crear `.gitignore` que excluya `.env` (+ `__pycache__/`, `*.pyc`, `.venv/`, `venv/`,
  artefactos de pytest/cache) sin excluir `env.example` ni `.gitkeep`
  <!-- rn: NUNCA versionar `.env`; cero credenciales reales en el repo -->
  - Verificación: el archivo contiene la línea `.env`; `env.example` no matchea ningún patrón del `.gitignore`.

## 2. Estructura de directorios exacta de la consigna

- [x] 2.1 Crear `app/`, `app/core/` y `app/modules/` con `__init__.py` de paquete y el esqueleto
  importable del proyecto
  <!-- rn: piezas obligatorias de la consigna en sus ubicaciones exactas -->
  - Verificación: el árbol coincide 1:1 con la sección «Estructura resultante» de `design.md`.
- [x] 2.2 Crear los 6 módulos placeholder: `duenios/`, `mascotas/`, `practicas/`, `turnos/` con
  `models.py`, `schemas.py`, `service.py`, `router.py` vacíos; `health/` solo con `router.py`;
  `laboratorio/` con `cliente.py`, `service.py`, `router.py` y **sin** `models.py`
  <!-- rn: nombres de tablas/ubicaciones intocables (FichaDuenio en duenios, TurnoPractica en turnos); models.py en laboratorio prohibido por IN-02 -->
  - Verificación: listing de archivos de `app/modules/` idéntico al de `design.md`; ningún módulo `laboratorio/models.py`.
- [x] 2.3 Crear `reiniciar.py` placeholder que lanza `NotImplementedError` con mensaje
  «implementado en C-04», y `test/` con `.gitkeep`
  <!-- rn: nada de DDL prematuro: borrado/create_all/seed es C-04 -->
  - Verificación: `python reiniciar.py` termina con `NotImplementedError` (falla esperada = criterio de pase) y el mensaje menciona C-04.

## 3. Configuración por entorno (US-103)

- [x] 3.1 Escribir PRIMERO el test de fail-fast (rojo): sin `DATABASE_URL` (entorno limpio, sin
  `.env` con la variable) importar la configuración lanza un error claro que menciona la
  variable faltante
  - Verificación: el test rojo falla (todavía no hay `app/core/config.py`).
- [x] 3.2 Implementar `app/core/config.py` mínimo: `load_dotenv()` + `os.getenv("DATABASE_URL")`;
  si falta → `RuntimeError` con mensaje «DATABASE_URL no definida — copiar env.example a .env»
  <!-- rn: solo DATABASE_URL se lee del entorno; nada más de config (sin pydantic-settings) -->
  - Verificación: el test 3.1 pasa (verde).
- [x] 3.3 Test de lectura feliz: con `.env` provisional que define `DATABASE_URL`
  `postgresql+asyncpg://usuario:password@localhost:5432/veterinaria`, la configuración la carga
  y la expone intacta
  - Verificación: `pytest` (o el runner del repo) pasa con ambos tests de config.
- [x] 3.4 Crear `env.example` con la forma del valor **solo placeholders**:
  `DATABASE_URL=postgresql+asyncpg://usuario:password@localhost:5432/veterinaria`
  <!-- rn: env.example sin ningún secreto (US-103 CA-2) -->
  - Verificación: el archivo contiene exactamente esa línea con placeholders y ningún otro valor real (sin contraseñas reales).

## 4. App mínima arrancable (sin routers)

- [x] 4.1 Crear `app/main.py`: `FastAPI()` con hook `lifespan` vacío (solo `yield`,
  `@asynccontextmanager`) y sin routers; comentario indicando que C-02 completa el lifespan
  <!-- rn: todo handler futuro async def; nada de DB ni lógica acá (C-02 dueño del lifespan real) -->
  - Verificación: `python -c "import app.main"` corre sin errores y `app.main.app` es una instancia de FastAPI.
- [x] 4.2 Smoke de arranque: con un `.env` local (no versionado) que define `DATABASE_URL`
  placeholder, `uvicorn app.main:app` levanta; sin la variable, el arranque aborta con el error
  de configuración de 3.2
  - Verificación: arranque con variable → servidor arriba (docs apareciables, sin rutas del dominio); arranque sin variable y sin entorno → proceso aborta con el mensaje de `RuntimeError`.

## 5. Integración final del change

- [x] 5.1 Recorrido completo desde cero: crear entorno virtual, `pip install -r
  requirements.txt`, copiar `env.example` → `.env`, importar y arrancar; dejar la secuencia de
  comandos anotada (la usará el README de C-11) y limpiar el `.env` provisional después
  <!-- rn: NUNCA commitear sin pedido explícito; `.env` local se borra/queda ignorado -->
  - Verificación: la secuencia completa corre verde de punta a punta; `git status` (si hay repo) nunca lista `.env`.
- [x] 5.2 Chequeo de reglas duras vs. alcance: confirmar que C-01 no tocó DB (`app/core/database.py`
  no existe), lifespan sin lógica, cero routers registrados, `reiniciar.py` sin seed — lo delegado queda en
  las fronteras de C-02..C-04
  - Verificación: recorrido por checklist de la sección «Non-Goals» de `design.md`, todo confirmado.

## Workflow follow-up

- `/opsx:verify c-01-foundation-setup` y luego `/opsx:archive c-01-foundation-setup`.
- Marcar `[x]` en la entrada `[C-01]` de `CHANGES.md`.
- Siguiente change del camino crítico: `/opsx:propose C-02-database-lifespan-health` (CLI: nombre en minúsculas: `c-02-database-lifespan-health`).
