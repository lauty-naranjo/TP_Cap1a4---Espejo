# Spec Delta

## Purpose

Toda lectura que incluya datos de una relación los obtiene con carga anticipada declarada
(joinedload para «a uno», selectinload para colecciones), con un número fijo de consultas que no
crece con la cantidad de filas relacionadas (US-501).

## ADDED Requirements

### Requirement: Detalle de turno con consultas fijas
El sistema SHALL exponer `GET /turnos/{id}` que devuelve el turno con su mascota y sus prácticas
resuelto en un número fijo de consultas (2: joinedload a uno + selectinload de la colección), que no
crece con la cantidad de prácticas, y responde 404 si no existe.

#### Scenario: Misma cantidad con 1 y 3 prácticas
- **WHEN** se solicita el detalle de un turno con 1 práctica y de otro con 3
- **THEN** ambos se resuelven con la misma cantidad de consultas (2)

### Requirement: Precarga en el detalle de dueño con ficha
El sistema SHALL resolver el detalle del dueño con su ficha con carga anticipada declarada
(joinedload a uno) y en una cantidad fija de consultas.

#### Scenario: Detalle con ficha
- **WHEN** se solicita el detalle de un dueño con ficha
- **THEN** se resuelve con 1 consulta (joinedload), sin carga perezosa

### Requirement: Cero carga perezosa
Ningún handler SHALL depender de la carga perezosa de relaciones; toda respuesta se ensambla con datos
precargados en la misma consulta (de lo contrario fallaría con `MissingGreenlet`).

#### Scenario: Lectura de colección
- **WHEN** se lee una colección (mascotas del dueño, prácticas del turno)
- **THEN** se obtiene con `selectinload`, no con acceso perezoso
