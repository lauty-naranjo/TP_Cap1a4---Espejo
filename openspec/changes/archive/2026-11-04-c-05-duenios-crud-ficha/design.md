# Design — c-05-duenios-crud-ficha

## Context

C-03 (modelos) y C-04 (seed) dejan la base lista, pero el módulo `duenios` no tiene DTOs, service ni
router. La consigna (Ejercicio 2) y los Flujos 3/4/5/11 (`07_flujos_principales.md`) definen el
comportamiento: alta con IntegrityError → 409, PATCH parcial, detalle con ficha embebida, borrado con
RESTRICT y ficha 1:1.

## Goals / Non-Goals

**Goals:**
- CRUD completo de dueños con códigos exactos (201/200/204, 404, 409, 422) y DTOs separados.
- Ficha 1:1 (POST con 409 si ya existe, RN-03) y mascotas del dueño (selectinload).
- Lecturas con carga anticipada (joinedload a uno, selectinload colección) — sin lazy load.

**Non-Goals:**
- CRUD de mascotas/practicas (C-06); altas de turno (C-07); N+1 exhaustivo (C-08); laboratorio (C-09);
  casos `.http` (C-10); README (C-11).

## Decisions

### D1 — DTOs separados y sin `id` en alta (RN-HTTP-02)
- `DuenioCreate(nombre, email)`, `DuenioUpdate(nombre?, email?)`, `DuenioRead(id, nombre, email, ficha)`,
  `FichaCreate(telefono, direccion)`, `FichaRead(id, telefono, direccion)`, `MascotaRead(id, nombre,
  especie)`.

### D2 — Integridad vía base: IntegrityError → 409 (DD-04, RN-INT-01)
- Sin consultas previas "¿ya existe?". Se escribe; `except IntegrityError` → rollback → 409 con mensaje
  propio ("email ya registrado", "ya tiene ficha", "tiene mascotas").

### D3 — PATCH parcial con `exclude_unset` (RN-HTTP-03)
- `payload.model_dump(exclude_unset=True)` aplica sólo los campos enviados; los ausentes no se tocan.

### D4 — Lecturas con carga anticipada (RN-REL-03)
- `GET /duenios/{id}` y PATCH: `joinedload(Duenio.ficha)` (a uno).
- `GET /duenios/{id}/mascotas`: `selectinload(Duenio.mascotas)` (colección).
- El service devuelve DTOs construidos desde los datos precargados (nunca acceso perezoso → evitar
  `MissingGreenlet`).

### D5 — 422 de id no entero (caso C-01)
- Path param tipado `int` → FastAPI responde 422 automáticamente sin ejecutar el handler.

### D6 — Registro de router e import de modelos en `app/main.py`
- `include_router(duenios_router)` en el lifespan (Flujo 1).
- Import de los 4 `models.py` para poblar el registry (resuelve forward-refs entre módulos).

## Risks / Trade-offs

- [Borrado de dueño con ficha] → la FK `ficha_duenio.duenio_id` no lleva `ondelete` (consigna no lo
  dicta); borrar un dueño con ficha (y sin mascotas) también da 409. Fuera del alcance de los casos de
  la consigna (C-05 solo prueba el bloqueo por mascotas). Documentado como riesgo, no bloquea.

## Migration Plan

- Sin cambios de esquema. Rollback = revertir código.

## Open Questions

- QA-02 (forma de `DuenioRead` cuando no hay ficha) → se resuelve con `ficha: null` (SU-04), registrado
  en los tests.
