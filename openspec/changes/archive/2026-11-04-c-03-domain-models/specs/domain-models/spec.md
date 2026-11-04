# Spec Delta

## Purpose

Define las seis tablas del modelo de dominio de la veterinaria (dueños, fichas, mascotas, prácticas y
turnos con sus prácticas) con sus restricciones de integridad y relaciones, tal como las exige la
consigna del Ejercicio 3 (US-301).

## ADDED Requirements

### Requirement: Tablas del modelo de dominio con nombres obligatorios
El sistema SHALL definir las tablas `duenio`, `ficha_duenio`, `mascota`, `practica`, `turno` y
`turno_practica` con las columnas exactas de la consigna, sin quitar ni renombrar las indicadas.

#### Scenario: Nombres de tablas y columnas
- **WHEN** se inspecciona el esquema de los modelos
- **THEN** existen las 6 tablas con sus columnas obligatorias (`duenio.id/nombre/email`,
  `ficha_duenio.id/duenio_id/telefono/direccion`, `mascota.id/nombre/especie/duenio_id`,
  `practica.id/nombre/precio`, `turno.id/mascota_id/fecha/motivo/total`,
  `turno_practica.turno_id/practica_id/precio_unitario`)

### Requirement: Restricciones de integridad delegadas a la base
El sistema SHALL declarar en la base las restricciones de unicidad, comprobación y claves foráneas con
su regla de borrado, y los índices en las claves foráneas.

#### Scenario: Unicidad y CHECKs
- **WHEN** se inspecciona el esquema
- **THEN** `duenio.email`, `practica.nombre` y `ficha_duenio.duenio_id` son UNIQUE, y existen los
  CHECK `practica.precio > 0`, `turno.total >= 0` y `turno_practica.precio_unitario > 0`

#### Scenario: Claves foráneas y borrado
- **WHEN** se inspecciona el esquema
- **THEN** `mascota.duenio_id` tiene ON DELETE RESTRICT, `turno_practica.turno_id` tiene ON DELETE
  CASCADE, y `turno_practica` tiene clave primaria compuesta `(turno_id, practica_id)`

#### Scenario: Índices en las claves foráneas
- **WHEN** se inspecciona el esquema
- **THEN** hay índices en `mascota.duenio_id`, `turno.mascota_id` y `turno_practica.practica_id`, y no
  hay índice propio en `turno_practica.turno_id` (cubierto por la PK compuesta)

### Requirement: Navegación de relaciones en ambos extremos
El sistema SHALL declarar cada relación con `Relationship(back_populates=...)` en los dos extremos, y
`Duenio.ficha` SHALL devolver un objeto y no una lista.

#### Scenario: Relaciones bidireccionales
- **WHEN** se inspecciona el mapeo ORM
- **THEN** cada relación tiene su contraparte `back_populates`, y `Duenio.ficha` apunta a un único
  `FichaDuenio` (no a una colección)

### Requirement: Borrado de la composición decidido por la base
El sistema SHALL declarar `Turno.practicas` con `passive_deletes` para que el borrado de las prácticas
de un turno lo ejecute la base por ON DELETE CASCADE y no el ORM.

#### Scenario: El ORM no borra las prácticas por su cuenta
- **WHEN** se borra un turno
- **THEN** las filas de `turno_practica` se eliminan por CASCADE en la base, sin que el ORM emita
  borrados individuales

### Requirement: Dinero con Decimal y columnas NUMERIC
El sistema SHALL representar el dinero con `Decimal` y columnas NUMERIC: `precio` y `precio_unitario`
como NUMERIC(10,2) y `turno.total` como NUMERIC(12,2).

#### Scenario: Tipos monetarios exactos
- **WHEN** se inspecciona el esquema
- **THEN** `precio` y `precio_unitario` son NUMERIC(10,2) y `turno.total` es NUMERIC(12,2), con tipos
  Python `Decimal` (nunca `float`)
