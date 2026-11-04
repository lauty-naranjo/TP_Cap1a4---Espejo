# Tasks

> Regla dura afectada por tarea se marca inline con `<!-- rn: … -->`. Nota TDD: Strict TDD en el apply.

## 1. DTOs del módulo duenios (RN-HTTP-02)

- [x] 1.1 Escribir los tests del service que fallan contra los placeholders (schemas/service/router vacíos)
  - Verificación: fallan en import (`cannot import name 'service'` / DTOs inexistentes).
- [x] 1.2 Implementar `app/modules/duenios/schemas.py`: DTOs separados, alta sin `id` (RN-HTTP-02)
  - Verificación: los tests 1.1 pasan.

## 2. Service con IntegrityError → 409 y precarga (US-201/202/203)

- [x] 2.1 `crear_duenio` (201 / 409 email duplicado) y `obtener_duenio` con `joinedload(ficha)` (RN-REL-03)
  <!-- rn: sin consulta previa; IntegrityError → rollback + 409 (RN-INT-01, RN-01) -->
- [x] 2.2 `actualizar_duenio` con `exclude_unset` (RN-HTTP-03), `borrar_duenio` (409 RESTRICT, RN-08),
  `crear_ficha` (409 segunda ficha, RN-03) y `obtener_mascotas_duenio` (selectinload)
  <!-- rn: joinedload a uno / selectinload colección; dinero Decimal en mascotas no aplica -->
  - Verificación: `pytest test/test_duenios_service.py` → 16 tests verdes contra PostgreSQL real.

## 3. Router y registro en la app

- [x] 3.1 `app/modules/duenios/router.py`: 6 endpoints con códigos exactos (201/200/204, 404/409/422)
  <!-- rn: path param int → 422 automático (C-01); Response(204) para borrado -->
- [x] 3.2 `app/main.py`: registrar `duenios_router` en el lifespan e importar los 4 `models.py`
  (resuelve forward-refs; sin el import falla `InvalidRequestError`)
  - Verificación: smoke HTTP sobre uvicorn con base real → todos los endpoints/códigos OK.

## 4. Integración del cambio

- [x] 4.1 Suite completa verde (`pytest` → 42 passed) y smoke HTTP del módulo duenios
  - Verificación: 42 tests + smoke (alta, email duplicado, PATCH parcial, borrado 409/204, ficha 409, 422 id no entero).

## Workflow follow-up

- `/opsx:verify c-05-duenios-crud-ficha` y luego `/opsx:archive c-05-duenios-crud-ficha`.
- Marcar `[x]` en la entrada `[C-05]` de `CHANGES.md`.
- Siguiente change del camino crítico: `/opsx:propose c-06-mascotas-practicas-crud`.
