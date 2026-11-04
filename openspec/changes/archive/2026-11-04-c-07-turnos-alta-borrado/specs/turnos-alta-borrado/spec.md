# Spec Delta

## Purpose

Alta de turno con prácticas anidadas (composición M:N) en una sola transacción todo-o-nada, con
precios congelados y total calculado en el servidor, y borrado con CASCADE decidido por la base
(US-401).

## ADDED Requirements

### Requirement: Alta de turno con prácticas anidadas
El sistema SHALL exponer `POST /turnos/` que recibe `mascota_id`, `fecha` (con zona horaria), `motivo`
y `practicas: [{practica_id}, ...]` (al menos una), copia el precio de cada práctica del catálogo,
calcula el total en el servidor y devuelve 201 con `TurnoRead`. Ni el precio ni el total viajan en el
DTO.

#### Scenario: Alta válida
- **WHEN** se envía un turno con prácticas existentes
- **THEN** responde 201 con los precios copiados y el total calculado

#### Scenario: Práctica inexistente (todo-o-nada)
- **WHEN** una de las prácticas no existe
- **THEN** responde 409 y no queda guardado nada (ni el turno ni sus prácticas)

#### Scenario: Práctica duplicada
- **WHEN** la misma práctica aparece dos veces
- **THEN** responde 409 (clave primaria compuesta)

#### Scenario: Lista vacía
- **WHEN** la lista de prácticas está vacía
- **THEN** responde 422 (RN-05)

### Requirement: Borrado del turno (composición)
El sistema SHALL exponer `DELETE /turnos/{id}` que borra el turno (204); la base borra sus
`turno_practica` por ON DELETE CASCADE, sin intervención del ORM, y responde 404 si no existe.

#### Scenario: Borrado con prácticas
- **WHEN** se borra un turno con prácticas
- **THEN** responde 204 y sus prácticas ya no están
