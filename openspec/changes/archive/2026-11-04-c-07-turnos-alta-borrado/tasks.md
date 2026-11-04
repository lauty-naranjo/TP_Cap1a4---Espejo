# Tasks

> Regla dura afectada por tarea se marca inline con `<!-- rn: … -->`. Nota TDD: Strict TDD en el apply.

## 1. DTOs del módulo turnos (RN-HTTP-02, RN-05, RN-06)

- [x] 1.1 Escribir los tests del service que fallan contra los placeholders (schemas/service/router vacíos)
- [x] 1.2 Implementar `app/modules/turnos/schemas.py`: `TurnoCreate` con `practicas` (min_length=1) y
  `TurnoRead` con mascota embebida y prácticas con `precio_unitario`
  <!-- rn: ni precio ni total viajan en el DTO (RN-06); lista vacía → 422 (RN-05) -->

## 2. Service de turnos: alta todo-o-nada (US-401)

- [x] 2.1 `crear_turno`: precios del catálogo → copia a `precio_unitario` (freeze), total del servidor,
  UNA transacción (RN-TX-01)
  <!-- rn: sin consulta previa de unicidad; IntegrityError → rollback + 409 (RN-INT-01) -->
- [x] 2.2 Errores: práctica inexistente → 409 sin guardar nada; duplicada → 409 (PK compuesta, RN-07);
  mascota inexistente → 409
- [x] 2.3 Normalizar fecha a UTC en la respuesta (`session.refresh`, SU-03)

## 3. Borrado del turno (RN-09, RN-INT-02)

- [x] 3.1 `borrar_turno`: DELETE; la base borra las `turno_practica` por CASCADE (passive_deletes)
  <!-- rn: el borrado lo decide la base, no el ORM (RN-INT-02) -->

## 4. Router y registro en la app

- [x] 4.1 `app/modules/turnos/router.py`: `POST /turnos/` (201) y `DELETE /turnos/{id}` (204)
- [x] 4.2 Registrar `turnos_router` en el lifespan de `app/main.py`

## 5. Integración del cambio

- [x] 5.1 `pytest test/test_turnos_service.py` → 7 tests verdes
- [x] 5.2 Smoke HTTP: contrato exacto del ejemplo (total "27000.00", fecha "13:30:00Z")

## Workflow follow-up

- `/opsx:archive c-07-turnos-alta-borrado`.
- Marcar `[x]` en la entrada `[C-07]` de `CHANGES.md`.
- Siguiente: `/opsx:propose c-08-lecturas-sin-n1`.
