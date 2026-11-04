# Proposal — c-06-mascotas-practicas-crud

## Why

C-03 definió los modelos `Mascota` y `Practica` y C-05 dejó operativo el módulo `duenios`, pero los
`router.py`/`service.py`/`schemas.py` de `mascotas` y `practicas` siguen vacíos. La consigna
(Ejercicio 2, US-204/205) exige el alta de mascotas (agregación: viaja `duenio_id`), el listado
paginado con el envoltorio de la sección 2.9, el detalle de mascota con su dueño y el catálogo de
prácticas con su precio > 0.

## What Changes

- `app/modules/mascotas/schemas.py`: `MascotaCreate` (con `duenio_id`), `MascotaRead` (dueño embebido
  en el detalle), `MascotaPage` (envoltorio `{items,total,page,size,pages}`) y `DuenioResumen`.
- `app/modules/mascotas/service.py`: alta (FK → `IntegrityError` → 409), listado paginado
  (`page > pages` → 422) y detalle con `joinedload(Mascota.duenio)`.
- `app/modules/mascotas/router.py`: `POST /mascotas/`, `GET /mascotas/`, `GET /mascotas/{id}`.
- `app/modules/practicas/{schemas,service,router}.py`: alta (nombre repetido → 409; precio ≤ 0 → 422
  por DTO) y catálogo completo (`GET /practicas/`, lista simple — SU-06).
- `app/main.py`: registra los routers de `mascotas` y `practicas`.

## Capabilities

### New Capabilities
- `mascotas-practicas-crud`: CRUD de mascotas (con paginación) y catálogo de prácticas (US-204/205).

### Modified Capabilities
- Ninguna: los modelos de C-03 y el CRUD de dueños de C-05 no cambian de comportamiento.

## Impact

- **Código**: `app/modules/mascotas/{schemas,service,router}.py`,
  `app/modules/practicas/{schemas,service,router}.py`, `app/main.py`.
- **API**: nacen los 5 endpoints de mascotas/practicas de la tabla de referencia.
- **Base de datos**: usa el esquema de C-03; sin cambios de esquema.
- **Gobernanza**: nivel MEDIO → integridad vía FK/UNIQUE con `IntegrityError` → 409.
