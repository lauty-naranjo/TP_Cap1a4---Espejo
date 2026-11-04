# Proposal — c-03-domain-models

> Nota de naming: el CLI de openspec exige kebab-case en minúsculas; `C-03-domain-models`
> (CHANGES.md) se registra acá como `c-03-domain-models`. Es el mismo change del roadmap.

## Why

El change C-02 dejó el ciclo de vida de la base y la sesión por petición listos, pero el proyecto
todavía no tiene ningún modelo de tabla: `app/modules/<módulo>/models.py` son placeholders vacíos.
Sin los modelos, no hay esquema que crear (`create_all` en C-04), ni integridad que la base garantice,
ni relaciones que los CRUD (C-05/C-06), las altas (C-07) y las lecturas sin N+1 (C-08) puedan usar.
Este change es la base de integridad de todo el TP (Ejercicio 3, US-301, 30 % de la nota) y está en el
camino crítico (C-02 → C-03 → C-05...).

## What Changes

- `app/modules/duenios/models.py`: modelos `Duenio` (tabla `duenio`) y `FichaDuenio` (tabla
  `ficha_duenio`, vive en `duenios`).
- `app/modules/mascotas/models.py`: modelo `Mascota` (tabla `mascota`).
- `app/modules/practicas/models.py`: modelo `Practica` (tabla `practica`).
- `app/modules/turnos/models.py`: modelos `Turno` (tabla `turno`) y `TurnoPractica` (tabla
  `turno_practica`, vive en `turnos`).
- Todas las restricciones de la consigna: UNIQUE, CHECK, claves foráneas con su regla de borrado,
  índices en las FKs, PK compuesta, navegación en los dos extremos y dinero en `Decimal`/`NUMERIC`.

## Capabilities

### New Capabilities
- `domain-models`: las 6 tablas del modelo de dominio con sus restricciones de integridad y
  relaciones (US-301, RN-01..RN-09, RN-INT-01/02, RN-REL-01/02, RN-DS-01).

### Modified Capabilities
- Ninguna: `project-configuration`, `database-lifespan` y `service-health` (C-01/C-02) no cambian.

## Impact

- **Código**: se implementan los 4 `models.py` de `duenios`, `mascotas`, `practicas` y `turnos`.
- **API**: sin cambios de endpoints (los CRUD son C-05+).
- **Dependencias**: ninguna nueva (SQLModel ya está en el stack, DD-01).
- **Base de datos**: define el esquema (se crea con `create_all` recién en C-04; sin Alembic, DD-03).
- **Gobernanza**: nivel CRITICO (modelo de datos central) → implementación con checkpoints y sin
  renombrar/quitar columnas obligatorias (SU-02).
