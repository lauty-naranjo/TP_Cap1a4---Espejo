# Tasks

> Regla dura afectada por tarea se marca inline con `<!-- rn: … -->`. Nota TDD: Strict TDD en el apply.

## 1. Detalle del turno con precarga (US-501 CA-2)

- [x] 1.1 Escribir tests con conteo de consultas (listener SQLAlchemy) que fallan sin `obtener_turno`
- [x] 1.2 `obtener_turno` con `joinedload(mascota)` + `selectinload(practicas).joinedload(practica)`
  <!-- rn: joinedload a uno / selectinload colección; sin lazy load (RN-REL-03) -->

## 2. Auditoría de lecturas existentes (US-501 CA-1, CA-3)

- [x] 2.1 Verificar `duenios` (joinedload ficha, selectinload mascotas) y `mascotas` (joinedload dueño)
  <!-- rn: cero carga perezosa en ningún handler (MissingGreenlet) -->
- [x] 2.2 Test de detalle de dueño+ficha → 1 consulta fija

## 3. Router y verificación del número fijo de consultas

- [x] 3.1 `app/modules/turnos/router.py`: `GET /turnos/{id}` (200/404)
- [x] 3.2 Test: detalle de turno con 1 y con 3 prácticas → misma cantidad de consultas (2, caso C-07)

## 4. Integración del cambio

- [x] 4.1 `pytest test/test_lecturas_sin_n1.py` → 2 tests verdes
- [x] 4.2 Suite completa verde

## Workflow follow-up

- `/opsx:archive c-08-lecturas-sin-n1`.
- Marcar `[x]` en la entrada `[C-08]` de `CHANGES.md`.
- Siguiente: `/opsx:propose c-09-laboratorio-offload`.
