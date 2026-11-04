# Tasks

> Regla dura afectada por tarea se marca inline con `<!-- rn: … -->`. Verificación esperada por
> tarea en su propio bullet (norma del schema). Nota TDD: el orquestador corre Strict TDD en el apply.

## 1. Modelo `duenios` (Duenio + FichaDuenio, 1:1)

- [x] 1.1 Escribir el test que inspecciona `duenio` y `ficha_duenio`: nombres de tabla/columna,
  `email` UNIQUE, `duenio_id` UNIQUE (el 1:1), y `Duenio.ficha` devuelve objeto (no lista)
  - Verificación: el test falla (import vacío: los `models.py` de C-01 son placeholders).
- [x] 1.2 Implementar `app/modules/duenios/models.py`: `Duenio` y `FichaDuenio` con relaciones
  `ficha`/`duenio` y `mascotas`/`duenio` (`back_populates`), `email` y `duenio_id` UNIQUE
  <!-- rn: FichaDuenio vive en duenios; Duenio.ficha objeto, no lista; nombres exactos (SU-02) -->
  - Verificación: el test 1.1 pasa (verde).

## 2. Modelo `mascotas` (Mascota, agregación con RESTRICT)

- [x] 2.1 Escribir el test que inspecciona `mascota`: columnas, FK `duenio_id` con ON DELETE
  RESTRICT y índice en `duenio_id`
  - Verificación: el test falla contra placeholder.
- [x] 2.2 Implementar `app/modules/mascotas/models.py`: `Mascota` con `duenio_id` FK RESTRICT +
  índice, y relaciones `duenio`/`mascotas` y `turnos`/`mascota` (`back_populates`)
  <!-- rn: ON DELETE RESTRICT + índice en duenio_id; borrado de dueño lo decide la base (RN-08) -->
  - Verificación: el test 2.1 pasa (verde).

## 3. Modelo `practicas` (Practica, catálogo con precio)

- [x] 3.1 Escribir el test que inspecciona `practica`: columnas, `nombre` UNIQUE, CHECK `precio > 0`,
  precio NUMERIC(10,2) tipo `Decimal`
  - Verificación: el test falla contra placeholder.
- [x] 3.2 Implementar `app/modules/practicas/models.py`: `Practica` con `nombre` UNIQUE, `precio`
  `Decimal`/NUMERIC(10,2) + CHECK, y relación `turno_practicas`/`practica` (`back_populates`)
  <!-- rn: dinero Decimal nunca float (RN-DS-01); CHECK precio > 0 en la base (RN-04) -->
  - Verificación: el test 3.1 pasa (verde).

## 4. Modelo `turnos` (Turno + TurnoPractica, composición y M:N con datos)

- [x] 4.1 Escribir el test que inspecciona `turno` y `turno_practica`: columnas, PK compuesta
  `(turno_id, practica_id)`, `turno_practica.turno_id` ON DELETE CASCADE, CHECK `total >= 0` y
  `precio_unitario > 0`, `total` NUMERIC(12,2), índices en `turno.mascota_id` y
  `turno_practica.practica_id`, sin índice propio en `turno_practica.turno_id`, y
  `Turno.practicas` con `passive_deletes=True`
  - Verificación: el test falla contra placeholder.
- [x] 4.2 Implementar `app/modules/turnos/models.py`: `Turno` y `TurnoPractica` con las relaciones
  `mascota`/`turnos`, `practicas`/`turno` y `practica`/`turno_practicas` (`back_populates`),
  `passive_deletes=True` en `Turno.practicas`, y las restricciones/índices indicados
  <!-- rn: ON DELETE CASCADE decidido por la base + passive_deletes (RN-INT-02, RN-09); PK compuesta (RN-07); total NUMERIC(12,2) -->
  - Verificación: el test 4.1 pasa (verde).

## 5. Integración del cambio

- [x] 5.1 Import de los 4 módulos juntos y verificación de que `SQLModel.metadata` registra las 6
  tablas sin errores de resolución de forward-refs
  - Verificación: `python -c "import app.modules.duenios.models, app.modules.mascotas.models, app.modules.practicas.models, app.modules.turnos.models"` corre limpio; `SQLModel.metadata.tables` tiene las 6 tablas.
- [x] 5.2 Suite completa verde (`pytest`), sin romper los 15 tests previos
  - Verificación: `pytest -q` → 15 previos + nuevos de modelos, todos verdes.

## Workflow follow-up

- `/opsx:verify c-03-domain-models` y luego `/opsx:archive c-03-domain-models`.
- Marcar `[x]` en la entrada `[C-03]` de `CHANGES.md`.
- Siguiente change del camino crítico: `/opsx:propose c-04-reiniciar-seed` (depende de C-03).
