# Proposal — c-08-lecturas-sin-n1

## Why

C-05/C-06/C-07 crearon lecturas con relaciones (detalle de dueño+ficha, detalle de mascota+dueño),
pero falta el detalle de turno (`GET /turnos/{id}`) y la garantía transversal de que ninguna lectura
depende de la carga perezosa (que en async falla con `MissingGreenlet`). La consigna (Ejercicio 5,
US-501) exige carga anticipada declarada y un número fijo de consultas.

## What Changes

- `app/modules/turnos/service.py`: `obtener_turno` con `joinedload(Turno.mascota)` (a uno) +
  `selectinload(Turno.practicas).joinedload(TurnoPractica.practica)` (colección) → 2 consultas fijas.
- `app/modules/turnos/router.py`: `GET /turnos/{id}`.
- Auditoría de las lecturas existentes: `duenios` (`joinedload(ficha)`, `selectinload(mascotas)`),
  `mascotas` (`joinedload(duenio)`), `turnos` — todas con precarga, sin lazy load.
- `test/test_lecturas_sin_n1.py`: conteo de consultas vía listener SQLAlchemy (detalle de turno con
  1 y con 3 prácticas → misma cantidad; detalle de dueño+ficha → 1 consulta).

## Capabilities

### New Capabilities
- `lecturas-sin-n1`: precarga declarada en toda lectura con relaciones y número fijo de consultas (US-501).

### Modified Capabilities
- `turnos-alta-borrado`: se agrega `GET /turnos/{id}` (detalle con mascota y prácticas).

## Impact

- **Código**: `app/modules/turnos/{service,router}.py`, `test/test_lecturas_sin_n1.py`.
- **API**: nace `GET /turnos/{id}`.
- **Base de datos**: sin cambios de esquema.
- **Gobernanza**: nivel MEDIO → evidencia con conteo de consultas (`echo`/listener) para el caso C-07.
