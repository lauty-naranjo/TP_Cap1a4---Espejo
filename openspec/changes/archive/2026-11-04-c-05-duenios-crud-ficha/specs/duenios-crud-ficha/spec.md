# Spec Delta

## Purpose

CRUD de dueños con DTOs separados, códigos HTTP exactos y la ficha 1:1 embebida, usando carga
anticipada y el patrón IntegrityError → 409 (US-201/202/203).

## ADDED Requirements

### Requirement: Alta de dueño
El sistema SHALL exponer `POST /duenios/` que crea un dueño y devuelve 201 con `DuenioRead`; un email
repetido responde 409 (IntegrityError, sin consulta previa) y un cuerpo inválido responde 422.

#### Scenario: Alta exitosa
- **WHEN** se envía `{"nombre": ..., "email": ...}`
- **THEN** responde 201 con el dueño (sin id en la entrada) y ficha nula

#### Scenario: Email duplicado
- **WHEN** se envía un email ya registrado
- **THEN** responde 409 con mensaje propio

### Requirement: Detalle, PATCH parcial y borrado de dueño
El sistema SHALL exponer `GET`, `PATCH` y `DELETE /duenios/{id}` con carga anticipada de la ficha,
PATCH parcial con `exclude_unset`, borrado 204 salvo que tenga mascotas (409 por RESTRICT) y 404 si no
existe.

#### Scenario: Detalle con ficha
- **WHEN** se solicita `GET /duenios/{id}` de un dueño con ficha
- **THEN** responde 200 con la ficha embebida

#### Scenario: PATCH parcial
- **WHEN** se envía un `PATCH` con sólo un campo
- **THEN** sólo ese campo cambia (los ausentes no se tocan)

#### Scenario: Borrado bloqueado por mascotas
- **WHEN** se borra un dueño que tiene mascotas
- **THEN** responde 409 (FK RESTRICT)

### Requirement: Ficha del dueño (uno a uno)
El sistema SHALL exponer `POST /duenios/{id}/ficha` que crea la ficha (201), 404 si el dueño no existe
y 409 si ya tiene ficha (UNIQUE).

#### Scenario: Segunda ficha
- **WHEN** se crea una ficha para un dueño que ya tiene una
- **THEN** responde 409

### Requirement: Mascotas del dueño
El sistema SHALL exponer `GET /duenios/{id}/mascotas` que devuelve las mascotas del dueño con
`selectinload` (200) y 404 si el dueño no existe.

#### Scenario: Listado de mascotas
- **WHEN** se solicita `GET /duenios/{id}/mascotas`
- **THEN** responde 200 con la colección de mascotas precargada

### Requirement: Parámetro de ruta no entero
El sistema SHALL responder 422 cuando un parámetro de ruta que debe ser entero no lo es, sin ejecutar
el handler.

#### Scenario: id no entero
- **WHEN** se solicita `GET /duenios/abc`
- **THEN** responde 422 sin ejecutar el handler
