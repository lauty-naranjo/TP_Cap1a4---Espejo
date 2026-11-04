# Design — c-06-mascotas-practicas-crud

## Context

C-03 (modelos) y C-05 (CRUD de dueños) dejan el esquema y el primer módulo listos. La consigna
(Ejercicio 2) define el alta de mascotas por agregación (viaja `duenio_id`), el listado con el
envoltorio de la sección 2.9 y el catálogo de prácticas (SU-06: lista simple). Flujos 6 y 7 de
`07_flujos_principales.md`.

## Goals / Non-Goals

**Goals:**
- `POST /mascotas/` (201) con dueño inexistente → 409 (FK violada, caso C-04).
- `GET /mascotas/` con envoltorio `{items,total,page,size,pages}` (size 1..100, `page>pages` → 422).
- `GET /mascotas/{id}` con el dueño embebido (joinedload a uno).
- `POST /practicas/` (nombre repetido → 409; precio ≤ 0 → 422 por DTO) y `GET /practicas/` (lista).

**Non-Goals:**
- Turnos (C-07); auditoría exhaustiva de N+1 (C-08); laboratorio (C-09); PATCH/DELETE de mascotas
  (no existen en la superficie dictada, DD-08).

## Decisions

### D1 — DTOs separados y alta sin `id` (RN-HTTP-02)
- `MascotaCreate(nombre, especie, duenio_id)`, `MascotaRead(id, nombre, especie, duenio_id, duenio?)`,
  `MascotaPage(items, total, page, size, pages)`, `DuenioResumen(id, nombre, email)`.
- `PracticaCreate(nombre, precio: Decimal > 0)`, `PracticaRead(id, nombre, precio)`.

### D2 — Integridad vía base (DD-04, RN-INT-01)
- Alta de mascota: INSERT; FK `mascota.duenio_id` rechaza dueño inexistente → `IntegrityError` → 409.
- Alta de práctica: INSERT; UNIQUE `nombre` rechaza duplicado → `IntegrityError` → 409.

### D3 — Precio > 0 en el DTO y en la base (RN-04)
- `precio: Decimal = Field(gt=0)` → 422 en el contrato; el CHECK `precio > 0` de C-03 respalda.

### D4 — Paginación (RN-HTTP-04, IN-01)
- `size` fuera de 1..100 → 422 automático (Query `ge/le`); `page > pages` → 422 del service
  (`pages = max(1, ceil(total/size))`, la primera página siempre responde aunque no haya resultados).

### D5 — Detalle con carga anticipada (RN-REL-03)
- `GET /mascotas/{id}`: `joinedload(Mascota.duenio)` (a uno). El alta/listado devuelven `duenio: null`
  sin tocar la relación (evita `MissingGreenlet`).

## Risks / Trade-offs

- `GET /mascotas/` no embebe el dueño en cada ítem (evita N+1); el dueño se obtiene en el detalle. Es
  coherente con la tabla de endpoints ("Envoltorio con mascotas").

## Migration Plan

- Sin cambios de esquema. Rollback = revertir código.

## Open Questions

- QA-01 (envoltorio solo en `GET /mascotas/`) → resuelto por SU-06: `GET /practicas/` es lista simple.
