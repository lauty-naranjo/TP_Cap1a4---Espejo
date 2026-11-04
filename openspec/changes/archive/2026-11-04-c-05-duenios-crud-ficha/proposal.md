# Proposal — c-05-duenios-crud-ficha

## Why

C-03 definió los modelos y C-04 el seed reproducible, pero ningún endpoint de dominio existe todavía:
los `router.py`/`service.py`/`schemas.py` de `duenios` están vacíos. La consigna (Ejercicio 2, US-201/202/203)
exige el CRUD de dueños con el patrón IntegrityError → 409, el PATCH parcial con `exclude_unset`, el
detalle con la ficha embebida (carga anticipada) y la ficha 1:1. Es el primer módulo funcional del camino
crítico (C-03 → C-05 → ...).

## What Changes

- `app/modules/duenios/schemas.py`: DTOs separados de los modelos (RN-HTTP-02) — `DuenioCreate` (sin id),
  `DuenioUpdate` (opcional, PATCH), `DuenioRead` (ficha embebida), `FichaCreate`, `FichaRead`, `MascotaRead`.
- `app/modules/duenios/service.py`: alta/detalle/PATCH/borrado + ficha + mascotas; lecturas con
  `joinedload`/`selectinload`; `IntegrityError` → 409 con mensaje propio (DD-04, RN-INT-01).
- `app/modules/duenios/router.py`: `POST /duenios/`, `GET /duenios/{id}`, `PATCH /duenios/{id}`,
  `DELETE /duenios/{id}`, `POST /duenios/{id}/ficha`, `GET /duenios/{id}/mascotas`.
- `app/main.py`: registra el router de duenios en el lifespan e importa todos los modelos (resuelve
  forward-refs entre módulos).

## Capabilities

### New Capabilities
- `duenios-crud-ficha`: CRUD de dueños + ficha 1:1 + mascotas del dueño (US-201/202/203, RN-01/03/08).

### Modified Capabilities
- Ninguna: `domain-models`, `reiniciar-seed` y las de C-01/C-02 no cambian de comportamiento.

## Impact

- **Código**: `app/modules/duenios/{schemas,service,router}.py`, `app/main.py`.
- **API**: nacen los 6 endpoints de dueños de la tabla de referencia.
- **Dependencias**: ninguna nueva.
- **Base de datos**: usa el esquema de C-03 y el seed de C-04; sin cambios de esquema.
- **Gobernanza**: nivel MEDIO → checkpoints y `IntegrityError` → 409 sin validación previa.
