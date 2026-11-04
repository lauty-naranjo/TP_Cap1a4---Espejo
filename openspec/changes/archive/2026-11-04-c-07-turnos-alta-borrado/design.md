# Design — c-07-turnos-alta-borrado

## Context

C-03 declaró `Turno` (asociación con `mascota`, índice en `mascota_id`) y `TurnoPractica` (PK
compuesta, CASCADE, `precio_unitario` NUMERIC). C-06 dejó operativos `mascotas` y `practicas`. La
consigna (Ejercicio 4) y los Flujos 8/10 definen el alta todo-o-nada y el borrado por CASCADE.

## Goals / Non-Goals

**Goals:**
- `POST /turnos/` en una sola transacción (RN-TX-01), cumpliendo RN-05..RN-07 y el contrato exacto.
- Precio de cada práctica copiado del catálogo (freeze, RN-DS-02) y total del servidor (RN-06).
- `DELETE /turnos/{id}` con CASCADE en la base (RN-09), sin que el ORM toque las prácticas.
- Respuesta `TurnoRead` con fecha normalizada a UTC y Decimal como string (SU-03).

**Non-Goals:**
- `GET /turnos/{id}` (C-08); auditoría N+1 (C-08); laboratorio (C-09); casos `.http` (C-10).

## Decisions

### D1 — DTOs: ni precio ni total viajan (RN-06)
- `TurnoCreate(mascota_id, fecha, motivo, practicas: [{practica_id}])` con `min_length=1` (RN-05 → 422).
- `TurnoRead` con `mascota` embebida y `practicas` con `precio_unitario`.

### D2 — Alta en una sola transacción (RN-TX-01)
- Traer precios del catálogo (`Practica.id.in_(set(ids))`); práctica inexistente → 409 sin guardar
  nada. Insertar `turno`, luego cada `turno_practica` con el precio copiado; total = suma en el
  servidor; `commit` único. Cualquier `IntegrityError` → rollback → 409 (mascota inexistente,
  práctica duplicada por PK compuesta, RN-07).

### D3 — Fecha normalizada a UTC (SU-03)
- `fecha` es `timestamptz`; tras el commit se hace `session.refresh(turno)` para devolver el instante
  normalizado a UTC (el ejemplo de la consigna: `10:30-03:00` → `13:30Z`).

### D4 — Borrado decidido por la base (RN-09, RN-INT-02)
- `DELETE` del turno; `Turno.practicas` con `passive_deletes=True` (C-03) → el ORM no vacía/borra las
  `turno_practica`; el `ON DELETE CASCADE` de la base las elimina.

## Risks / Trade-offs

- [Práctica duplicada] depende de que el INSERT duplicado alcance la base para violar la PK compuesta;
  se verifica con test (409 y rollback total). Si el ORM la rechazara antes, se ajustaría sin cambiar
  el contrato HTTP (sigue siendo 409).

## Migration Plan

- Sin cambios de esquema. Rollback = revertir código.

## Open Questions

- QA-03/DD-07 (mecanismo de offload) → no aplica a este change (es C-09).
