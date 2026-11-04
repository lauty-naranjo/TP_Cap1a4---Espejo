# Design — c-08-lecturas-sin-n1

## Context

Las lecturas con relaciones nacieron en C-05 (dueño+ficha, mascotas del dueño), C-06 (mascota+dueño) y
C-07 (turno). La consigna (Ejercicio 5) exige que toda respuesta con datos de una relación los obtenga
con carga anticipada declarada y que el detalle del turno se resuelva con un número fijo de consultas.
Flujo 9 de `07_flujos_principales.md`.

## Goals / Non-Goals

**Goals:**
- `GET /turnos/{id}` con mascota y prácticas en 2 consultas fijas (1 joinedload + 1 selectinload).
- Auditoría: cero carga perezosa en todos los handlers con relaciones.
- Evidencia reproducible: conteo de consultas con 1 y con 3 prácticas.

**Non-Goals:**
- Casos `.http` de la consigna (C-10); README con la evidencia (C-11).

## Decisions

### D1 — Estrategia de precarga por forma de relación (RN-REL-03, Flujo 9)
- `joinedload` para «a uno»: `mascota→dueño`, `turno→mascota`, `dueño→ficha`.
- `selectinload` para colecciones: `dueño→mascotas`, `turno→practicas` (con `joinedload` de la práctica).

### D2 — Detalle del turno en 2 consultas fijas
- `select(Turno).options(joinedload(Turno.mascota), selectinload(Turno.practicas).joinedload(TurnoPractica.practica))`
  → 1 SELECT con LEFT JOIN mascota + 1 SELECT de `turno_practica` con LEFT JOIN `practica` (IN por
  `turno_id`). No crece con la cantidad de prácticas.

### D3 — Evidencia con listener SQLAlchemy
- Test con `event.listen(engine.sync_engine, "before_cursor_execute", ...)` contando sentencias; el
  fragmento de consola para la entrega se captura con `echo=True` en C-10/C-11.

## Risks / Trade-offs

- `selectinload` emite siempre 1 SELECT adicional (no es 1 query total, sino 2 fijas); así lo describe
  el Flujo 9 de la KB. El N+1 se evita porque la segunda query usa `IN` y no una query por práctica.

## Migration Plan

- Sin cambios de esquema. Rollback = revertir código.

## Open Questions

- QA-06 (formato de fecha en la respuesta) → resuelto por SU-03 (normalización a UTC).
