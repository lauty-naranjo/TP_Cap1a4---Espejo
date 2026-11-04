# Proposal — c-07-turnos-alta-borrado

## Why

C-06 dejó operativos los módulos `mascotas` y `practicas` (los ids que el turno referencia), pero el
módulo `turnos` solo tiene los modelos de C-03. La consigna (Ejercicio 4, US-401) exige el flujo
central: el alta de un turno con sus prácticas anidadas en una sola transacción, con precios
congelados y total calculado en el servidor, y el borrado con CASCADE decidido por la base.

## What Changes

- `app/modules/turnos/schemas.py`: `TurnoCreate` (`mascota_id`, `fecha`, `motivo`, `practicas:
  [{practica_id}]` con al menos una), `TurnoRead` (mascota embebida + prácticas con `precio_unitario`),
  `PracticaTurnoCreate/Read`, `MascotaResumen`.
- `app/modules/turnos/service.py`: `crear_turno` en una sola transacción (precios copiados del
  catálogo, total del servidor, todo-o-nada) y `borrar_turno` (la base borra las prácticas por
  CASCADE).
- `app/modules/turnos/router.py`: `POST /turnos/` y `DELETE /turnos/{id}`.
- `app/main.py`: registra el router de `turnos`.

## Capabilities

### New Capabilities
- `turnos-alta-borrado`: alta de turno con composición M:N (todo-o-nada) y borrado con CASCADE (US-401).

### Modified Capabilities
- Ninguna.

## Impact

- **Código**: `app/modules/turnos/{schemas,service,router}.py`, `app/main.py`.
- **API**: nacen `POST /turnos/` y `DELETE /turnos/{id}`.
- **Base de datos**: usa el esquema de C-03 (PK compuesta, CASCADE, CHECK `total >= 0`); sin cambios.
- **Gobernanza**: nivel ALTO → transacción todo-o-nada, precios congelados y contrato exacto de la
  consigna (ejemplo de `POST /turnos/`).
