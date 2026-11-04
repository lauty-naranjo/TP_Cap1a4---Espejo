# test-cases Specification

## Purpose
Los 9 casos mínimos de la consigna (`C-01`..`C-09`) corribles después de `python reiniciar.py`, cada
uno con su resultado esperado documentado, incluyendo la evidencia de consultas fijas del caso C-07
(US-701).

## Requirements

### Requirement: Casos .http de la consigna
El sistema SHALL proveer en `test/` los casos `C-01`..`C-07` y `C-09` en formato `.http`, cada uno con
el resultado esperado documentado y corribles en orden sobre el seed de `python reiniciar.py`.

#### Scenario: C-01 parámetro no entero
- **WHEN** se llama `GET /duenios/abc`
- **THEN** responde 422 sin ejecutar el handler

#### Scenario: C-02 unicidad
- **WHEN** se repite un email de dueño o un nombre de práctica
- **THEN** responde 409 con mensaje propio

#### Scenario: C-03 segunda ficha
- **WHEN** se crea una segunda ficha para un dueño
- **THEN** responde 409

#### Scenario: C-04 FK inexistente
- **WHEN** se crea una mascota con dueño inexistente o un turno con práctica inexistente
- **THEN** responde 409 y del turno no queda nada guardado

#### Scenario: C-05 borrados
- **WHEN** se borra un dueño con mascotas y luego un turno
- **THEN** el dueño da 409 y el turno da 204 (sus prácticas ya no están)

#### Scenario: C-06 turno válido
- **WHEN** se crea un turno válido con dos prácticas
- **THEN** responde 201 con los precios copiados y el total calculado

#### Scenario: C-07 consultas fijas
- **WHEN** se consulta el detalle de un turno con 1 y con 3 prácticas
- **THEN** ambos emiten la misma cantidad fija de consultas (2)

#### Scenario: C-09 laboratorio y health
- **WHEN** hay consultas al laboratorio en marcha y se llama a `/health/live`
- **THEN** el health responde de inmediato

### Requirement: Caso C-08 en SQL
El sistema SHALL incluir `test/C-08.sql` con un `UPDATE practica SET precio = 0` que la base rechaza
por el CHECK `ck_practica_precio_positivo`.

#### Scenario: UPDATE de precio inválido
- **WHEN** se ejecuta el `UPDATE` directo contra la base
- **THEN** la base lo rechaza por el CHECK (no queda el precio en 0)

### Requirement: Evidencia de consultas fijas
El sistema SHALL incluir la evidencia del caso C-07: un fragmento de consola (`echo=True`) con las
consultas del detalle de un turno con una y con tres prácticas.

#### Scenario: Evidencia C-07
- **WHEN** se ejecuta el detalle con el log de SQL activado
- **THEN** se observan 2 consultas fijas en ambos casos (no crece con las prácticas)
