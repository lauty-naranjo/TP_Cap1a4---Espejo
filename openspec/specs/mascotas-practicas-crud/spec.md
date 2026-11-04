# mascotas-practicas-crud Specification

## Purpose
CRUD de mascotas (con paginación de la sección 2.9) y catálogo de prácticas, con DTOs separados,
códigos HTTP exactos, carga anticipada en el detalle y el patrón IntegrityError → 409 (US-204/205).

## Requirements

### Requirement: Alta de mascota (agregación)
El sistema SHALL exponer `POST /mascotas/` que crea una mascota a nombre de un dueño existente y
devuelve 201 con `MascotaRead`; un `duenio_id` inexistente responde 409 (FK violada, sin consulta
previa) y un cuerpo inválido responde 422.

#### Scenario: Alta exitosa
- **WHEN** se envía `{"nombre": ..., "especie": ..., "duenio_id": <existente>}`
- **THEN** responde 201 con la mascota creada

#### Scenario: Dueño inexistente
- **WHEN** se envía un `duenio_id` que no existe
- **THEN** responde 409 (IntegrityError) y no queda guardado nada

### Requirement: Listado paginado de mascotas
El sistema SHALL exponer `GET /mascotas/` con el envoltorio `{items,total,page,size,pages}`; `size`
por defecto 20 y rango 1..100; una página más allá de `pages` responde 422 y la primera página
siempre responde aunque no haya resultados.

#### Scenario: Página más allá de pages
- **WHEN** se solicita una página mayor a `pages`
- **THEN** responde 422

#### Scenario: Primera página sin resultados
- **WHEN** no hay mascotas y se solicita la primera página
- **THEN** responde 200 con `items` vacío

### Requirement: Detalle de mascota con su dueño
El sistema SHALL exponer `GET /mascotas/{id}` que devuelve la mascota con su dueño embebido
(`joinedload` a uno) y 404 si no existe.

#### Scenario: Detalle con dueño
- **WHEN** se solicita una mascota existente
- **THEN** responde 200 con el dueño embebido

### Requirement: Catálogo de prácticas
El sistema SHALL exponer `POST /practicas/` (201, nombre repetido → 409, precio ≤ 0 → 422) y
`GET /practicas/` que devuelve el catálogo completo como lista simple.

#### Scenario: Nombre duplicado
- **WHEN** se crea una práctica con un nombre ya existente
- **THEN** responde 409 (UNIQUE)

#### Scenario: Precio no positivo
- **WHEN** se crea una práctica con precio ≤ 0
- **THEN** responde 422 (validación del DTO, RN-04)
