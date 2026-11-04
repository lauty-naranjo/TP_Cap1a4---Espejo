# Tasks

> Regla dura afectada por tarea se marca inline con `<!-- rn: … -->`. Nota TDD: Strict TDD en el apply.

## 1. Script de reinicio con seed (US-302)

- [x] 1.1 Escribir el test que corre `python reiniciar.py` sobre la base real y verifica el seed
  (2 dueños/1 ficha, 3 mascotas, 4 prácticas, 1 turno con 2 prácticas, precios C-06)
  - Verificación: el test falla (reiniciar.py aún es placeholder de C-01).
- [x] 1.2 Implementar `reiniciar.py`: borrar tablas, `create_all` y cargar el seed (US-302 CA-1/CA-2)
  <!-- rn: DD-03 create_all (sin Alembic); dinero Decimal (RN-DS-01); precios coherentes con C-06 -->
  - Verificación: `python reiniciar.py` termina 0; el test 1.1 pasa (verde) y la base queda sembrada.

## 2. Integración del cambio

- [x] 2.1 Suite completa verde (el test de reiniciar usa el `.env` real sin depender del entorno
  pisado por otros tests)
  - Verificación: `pytest -q` → 26 passed (25 previos + 1 de reiniciar).

## Workflow follow-up

- `/opsx:verify c-04-reiniciar-seed` y luego `/opsx:archive c-04-reiniciar-seed`.
- Marcar `[x]` en la entrada `[C-04]` de `CHANGES.md`.
- Siguiente change: `/opsx:propose c-05-duenios-crud-ficha` (depende de C-03).
