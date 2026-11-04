# Tasks

> Regla dura afectada por tarea se marca inline con `<!-- rn: … -->`. Nota TDD: Strict TDD en el apply.

## 1. DTOs de mascotas y practicas (RN-HTTP-02)

- [x] 1.1 Escribir los tests del service que fallan contra los placeholders (schemas/service/router vacíos)
- [x] 1.2 Implementar `app/modules/mascotas/schemas.py` (MascotaCreate/Read/Page, DuenioResumen)
- [x] 1.3 Implementar `app/modules/practicas/schemas.py` (PracticaCreate con `precio > 0`, PracticaRead)
  <!-- rn: dinero Decimal; precio ≤ 0 → 422 por DTO (RN-04, RN-DS-01) -->

## 2. Service de mascotas (US-204)

- [x] 2.1 `crear_mascota` (FK → IntegrityError → 409), `obtener_mascota` con `joinedload(duenio)`
  <!-- rn: sin consulta previa de existencia; IntegrityError → rollback + 409 (RN-INT-01) -->
- [x] 2.2 `listar_mascotas` con envoltorio {items,total,page,size,pages} y `page > pages` → 422
  <!-- rn: paginación solo en GET /mascotas/ (RN-HTTP-04); primera página siempre responde -->

## 3. Service de practicas (US-205)

- [x] 3.1 `crear_practica` (UNIQUE nombre → 409) y `listar_practicas` (lista simple, SU-06)

## 4. Routers y registro en la app

- [x] 4.1 Routers de `mascotas` (POST/GET listado/GET detalle) y `practicas` (POST/GET)
  <!-- rn: size Query(ge=1,le=100) → 422; códigos 201/200/404/409/422 -->
- [x] 4.2 Registrar `mascotas_router` y `practicas_router` en el lifespan de `app/main.py`

## 5. Integración del cambio

- [x] 5.1 `pytest test/test_mascotas_service.py test/test_practicas_service.py` → 11 tests verdes
- [x] 5.2 Suite completa verde y smoke HTTP (alta 201/409, paginación 200/422, detalle 200/404, prácticas)

## Workflow follow-up

- `/opsx:archive c-06-mascotas-practicas-crud`.
- Marcar `[x]` en la entrada `[C-06]` de `CHANGES.md`.
- Siguiente: `/opsx:propose c-07-turnos-alta-borrado`.
