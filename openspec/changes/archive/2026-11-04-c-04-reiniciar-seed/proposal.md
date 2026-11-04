# Proposal — c-04-reiniciar-seed

## Why

C-03 definió las 6 tablas del modelo, pero el esquema todavía no se crea ni se puebla: `reiniciar.py`
es un placeholder que aborta con `NotImplementedError`. La consigna (Ejercicio 3, US-302) exige un
script que deje la base en un estado conocido y que funcione **sobre una base vacía** — condición para
que el TP se corrija. Los casos de prueba `.http` (C-10) dependen de este estado reproducible.

## What Changes

- `reiniciar.py` (raíz): borra las tablas, las crea con `SQLModel.metadata.create_all` y carga el seed
  mínimo (2 dueños, uno con ficha; 3 mascotas; 4 prácticas; 1 turno con 2 prácticas).
- Precios coherentes con el ejemplo de `POST /turnos/` (Consulta 15000.00, Vacuna antirrábica 12000.00)
  para reproducir el caso C-06 (total 27000.00).

## Capabilities

### New Capabilities
- `reiniciar-seed`: estado reproducible de la base vía `reiniciar.py` (US-302 CA-1/CA-2, DD-03).

### Modified Capabilities
- Ninguna: `domain-models` (C-03) define el esquema; este change lo crea y lo puebla.

## Impact

- **Código**: se implementa `reiniciar.py` (raíz) y su test `test/test_reiniciar.py`.
- **API**: sin cambios.
- **Dependencias**: ninguna nueva (SQLModel + asyncpg ya en el stack, DD-01).
- **Base de datos**: crea el esquema y carga el seed (DD-03: sin Alembic).
- **Gobernanza**: nivel BAJO (script de tooling), pero crítico para la corrección (base vacía).
