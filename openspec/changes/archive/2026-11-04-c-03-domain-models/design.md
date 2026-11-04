# Design — c-03-domain-models

## Context

C-02 dejó el ciclo de vida de la base listo pero sin modelos: los `models.py` de `duenios`,
`mascotas`, `practicas` y `turnos` están vacíos (placeholders de C-01). La consigna (Ejercicio 3) y
`knowledge-base/04_modelo_de_datos.md` + `05_reglas_de_negocio.md` definen el modelo objetivo: 6 tablas
con nombres y columnas **obligatorios** (no quitar ni renombrar, SU-02), cada relación de las vistas
en el capítulo 4 aparece una vez, y la integridad la garantiza la base (DD-04), no el ORM.

Relaciones (una de cada tipo, KB 04):
1. **1:1** Duenio ↔ FichaDuenio (FK `ficha_duenio.duenio_id` + UNIQUE).
2. **Agregación** Duenio → Mascota (FK `mascota.duenio_id` ON DELETE RESTRICT + índice).
3. **Asociación** Turno → Mascota (FK `turno.mascota_id` + índice).
4. **Composición** Turno → TurnoPractica (FK `turno_practica.turno_id` ON DELETE CASCADE, sin índice
   propio).
5. **M:N con datos** Turno ↔ Practica vía `turno_practica` (`precio_unitario` es de la relación).

## Goals / Non-Goals

**Goals:**
- Definir las 6 tablas con sus columnas/restricciones exactas (nombres obligatorios, SU-02).
- Declarar las relaciones en los dos extremos con `Relationship(back_populates=...)` (RN-REL-01) y
  `Duenio.ficha` devolviendo **objeto, no lista** (RN-REL-02).
- `Turno.practicas` con `passive_deletes=True` (RN-INT-02, DD-05); borrado decidido por la base.
- Dinero con `Decimal` y columnas NUMERIC(10,2)/NUMERIC(12,2) (RN-DS-01).

**Non-Goals:**
- CRUD/contratos HTTP (C-05/C-06); schemas Pydantic (C-05/C-06); altas con relaciones (C-07);
  lecturas con precarga (C-08); `reiniciar.py` + seed (C-04); casos `.http` (C-10); README (C-11).
- Auth/RBAC, Alembic, repositorios/UoW, lazy loading, float money — fuera de alcance por reglas duras.

## Decisions

### D1 — Nombres de tablas y columnas literal (SU-02)
- `duenio`(id, nombre, email), `ficha_duenio`(id, duenio_id, telefono, direccion),
  `mascota`(id, nombre, especie, duenio_id), `practica`(id, nombre, precio),
  `turno`(id, mascota_id, fecha, motivo, total), `turno_practica`(turno_id, practica_id,
  precio_unitario). `id` PK autoincremental; `fecha` con zona horaria (`timestamptz`).
- Tablas en singular (la consigna usa `duenio`, no `duenios`).

### D2 — Restricciones en la base (DD-04)
- UNIQUE: `duenio.email`, `practica.nombre`, `ficha_duenio.duenio_id` (el 1:1).
- CHECK: `practica.precio > 0`, `turno.total >= 0`, `turno_practica.precio_unitario > 0`
  (`CheckConstraint` con nombre explícito).
- FK + borrado: `mascota.duenio_id` ON DELETE **RESTRICT** (RN-08); `turno_practica.turno_id`
  ON DELETE **CASCADE** (RN-09); `turno.mascota_id` y `turno_practica.practica_id` sin `ondelete`
  (la consigna no pide borrado para esos lados).
- PK compuesta `(turno_id, practica_id)` en `turno_practica` (RN-07).

### D3 — Índices manuales en las FKs (PostgreSQL no los crea solo, sección 4.10)
- Índices en `mascota.duenio_id`, `turno.mascota_id`, `turno_practica.practica_id` (`index=True`).
- **Sin índice propio** en `turno_practica.turno_id`: lo cubre la PK compuesta `(turno_id,
  practica_id)` cuya primera columna ya sirve para buscar por turno (explicación 1-2 líneas para el
  README de C-11).

### D4 — Navegación en los dos extremos (RN-REL-01/02)
- `Duenio.ficha` (objeto, `Optional`) ↔ `FichaDuenio.duenio`; `Duenio.mascotas` ↔ `Mascota.duenio`;
  `Mascota.turnos` ↔ `Turno.mascota`; `Turno.practicas` ↔ `TurnoPractica.turno`;
  `Practica.turno_practicas` ↔ `TurnoPractica.practica`.
- Referencias entre módulos por cadena (string) para evitar importaciones circulares; la resolución
  es vía el registry de SQLModel/SQLAlchemy (se importan los 4 módulos antes del primer uso).

### D5 — `passive_deletes` en la composición (RN-INT-02, DD-05)
- `Turno.practicas` con `Relationship(back_populates="turno",
  sa_relationship_kwargs={"passive_deletes": True})`: el ORM no vacía ni borra `turno_practica` al
  borrar un turno; lo hace la base por CASCADE.

### D6 — Dinero con `Decimal` y NUMERIC (RN-DS-01)
- `precio`/`precio_unitario`: `Field(max_digits=10, decimal_places=2)` → `NUMERIC(10,2)`.
- `turno.total`: `Field(max_digits=12, decimal_places=2)` → `NUMERIC(12,2)`.

## Risks / Trade-offs

- [Referencias entre módulos por string] → si SQLModel no resuelve un forward-ref, se detecta en el
  import-test del apply y se corrige con import explícito (los módulos no tienen ciclo real de imports,
  solo de nombres).
- [El borrado `ficha_duenio.duenio_id` no lleva `ondelete`] → la consigna no especifica regla para ese
  lado; queda con el default de PostgreSQL (NO ACTION). El DELETE de dueño se resuelve en C-05 contra
  RN-08 (mascotas). Documentado como riesgo, no bloquea el modelado.

## Migration Plan

- Sin `create_all` en este change (DD-03: lo ejecuta `reiniciar.py` en C-04). No hay migración de datos
  ni Alembic; rollback = revertir `models.py`.

## Open Questions

- QA-01/QA-02/QA-03 (paginación de otros listados, forma de `DuenioRead`, mecanismo de offload) no
  tocan el modelado: quedan para C-05/C-06/C-09.
- El índice de `turno_practica.turno_id` se documenta en el README (C-11), como pide la consigna.
