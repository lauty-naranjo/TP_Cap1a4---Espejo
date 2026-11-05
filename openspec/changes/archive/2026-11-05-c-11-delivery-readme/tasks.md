# Tasks

> Regla dura afectada por tarea se marca inline con `<!-- rn: … -->`. Nota TDD: el test de contrato se
> escribe antes del README (RED → GREEN). No se toca `app/**` en este change.

## 1. Test de contrato de entrega (TDD — RED)

- [x] 1.1 Crear `test/test_entrega.py` con los chequeos de CA-1: existen `README.md`, `requirements.txt`,
  `env.example`, `reiniciar.py` y `test/`; `.env` está ignorado por `.gitignore` y no trackeado; `env.example`
  sólo declara `DATABASE_URL` con placeholders. Verificación: `pytest test/test_entrega.py -q` falla por
  `README.md` ausente y por lo demás pasa.
  <!-- rn: cero credenciales reales en el repo; .env no versionado, env.example sin secretos -->
- [x] 1.2 Ampliar el test con CA-2/CA-3/CA-4: secciones del README, pasos de venv/dependencias/`.env`/
  `python reiniciar.py`/`uvicorn` en orden, mención de Python 3.12 y PostgreSQL 16, explicación del índice
  de `turno_practica.turno_id`, evidencia C-07 (1 y 3 prácticas) integrada o enlazada, y `test/evidencia_c07.txt`
  con los dos casos. Verificación: `pytest test/test_entrega.py -q` falla con mensajes que nombran cada CA
  pendiente (RED esperado, el README todavía no existe).
- [x] 1.3 Confirmar que el test no depende de PostgreSQL ni de la app: `pytest test/test_entrega.py -q`
  no abre conexiones y el archivo no importa `app.core.database` ni `app.main`.

## 2. README — puesta en marcha desde cero (CA-2)

- [x] 2.1 Crear `README.md` en la raíz con descripción de 2–3 líneas, stack (Python 3.12, FastAPI,
  SQLModel/SQLAlchemy async, asyncpg, PostgreSQL 16) y requisitos previos. Verificación: revisión del
  README + chequeos de stack del test de entrega en verde.
- [x] 2.2 Documentar la puesta en marcha en orden: crear/activar entorno virtual → `pip install -r
  requirements.txt` → copiar `env.example` a `.env` → `python reiniciar.py` → `uvicorn app.main:app --reload`,
  con el comando equivalente para PowerShell y bash en los pasos que difieren. Verificación: seguir los
  pasos desde una terminal limpia y llegar al servidor en `http://localhost:8000`.
- [x] 2.3 Documentar la configuración `.env`: única variable `DATABASE_URL`, forma
  `postgresql+asyncpg://usuario:password@localhost:5432/veterinaria`, aclaración de que `.env` no se
  versiona y de que los valores son placeholders. Verificación: los chequeos CA-2/CA-1 del test pasan.
  <!-- rn: no inventar credenciales; env.example sólo con placeholders -->

## 3. README — modelo de datos, índice y evidencia (CA-3, CA-4)

- [x] 3.1 Agregar la sección de modelo de datos con las 6 tablas y la explicación de 1–2 líneas del
  índice de `turno_practica.turno_id`: la PK compuesta `(turno_id, practica_id)` sirve como índice por
  su primera columna, y `practica_id` tiene índice propio porque no es la primera columna. Verificación:
  chequeo CA-3 del test en verde y `\d turno_practica` en `psql` muestra `turno_practica_pkey` e
  `ix_turno_practica_practica_id`.
- [x] 3.2 Integrar la evidencia C-07 al README: fragmento de consola con las 2 consultas del detalle de
  un turno con 1 práctica y con 3, la conclusión de que el número no crece, y enlace a
  `test/evidencia_c07.txt`. Verificación: chequeo CA-4 del test en verde; las consultas citadas coinciden
  con el archivo crudo.
- [x] 3.3 Documentar los 9 casos de `test/` (tabla breve con resultado esperado y orden de ejecución),
  la estructura del proyecto y una nota de alcance (API REST sin UI ni auth). Verificación: revisión del
  README contra `test/LEEME.md`; `pytest test/test_entrega.py -q` completamente en verde (GREEN).

## 4. Chequeo final de entrega (CA-5)

- [x] 4.1 Sobre una base PostgreSQL **vacía**, ejecutar `python reiniciar.py` y verificar que crea las
  6 tablas (`duenio`, `ficha_duenio`, `mascota`, `practica`, `turno`, `turno_practica`) y el seed
  (2 dueños, 3 mascotas, 4 prácticas, 1 turno con 2 prácticas). Verificación: el script termina sin error
  y los conteos coinciden.
  <!-- rn: reiniciar sobre base vacía es condición de corrección de la cátedra -->
- [x] 4.2 Arrancar `uvicorn app.main:app` y verificar `GET /health/live` → 200 y `GET /health/ready` →
  200; el ejemplo de fecha del README devuelve `2026-11-12T13:30:00Z`. Verificación: llamadas HTTP reales.
  <!-- rn: fecha normalizada a UTC con Z (QA-06) -->
- [x] 4.3 Correr la suite completa: `pytest -q` → 65 tests previos + los de `test_entrega.py`, todos en
  verde. Verificación: salida de pytest sin fallos ni skips inesperados.
- [x] 4.4 Revisión final del README: comandos copiables en PowerShell, sin credenciales reales y con
  `.env` fuera del versionado. Verificación: `git check-ignore -v .env` responde y un grep de credenciales
  en `README.md`/`env.example` no encuentra valores reales.

## Workflow follow-up

- `/opsx:archive c-11-delivery-readme`.
- Marcar `[x]` en la entrada `[C-11]` de `CHANGES.md` y actualizar su estado a archivado.
- Confirmar que la entrega cubre las 8 épicas y que el TP queda completo (sin C-04/C-11 no se corrige).
