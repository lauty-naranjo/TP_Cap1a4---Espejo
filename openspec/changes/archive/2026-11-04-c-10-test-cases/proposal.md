# Proposal — c-10-test-cases

## Why

C-04, C-08 y C-09 (y por transitividad C-05..C-07) dejaron operativa toda la API, pero falta la
evidencia exigida por la consigna: la carpeta `test/` con los **9 casos mínimos** (`C-01`..`C-09`)
corribles después de `python reiniciar.py`, cada uno con la respuesta esperada documentada, más la
evidencia de consultas fijas del caso C-07 (US-701, Épica 7).

## What Changes

- `test/C-01.http` .. `test/C-07.http`, `test/C-09.http`: los 8 casos en formato `.http` (VS Code REST
  Client / IntelliJ HTTP Client), cada uno con comentario de la respuesta esperada.
- `test/C-08.sql`: el caso del `UPDATE practica SET precio = 0` ejecutado directo en la base (la base
  lo rechaza por el CHECK).
- `test/LEEME.md`: cómo correr los casos (servidor, orden, `SQL_ECHO=true` para C-07).
- `test/evidencia_c07.txt`: fragmento de consola (`echo=True`) con las consultas del detalle de un
  turno con 1 y con 3 prácticas (2 consultas fijas) — insumo para el README de C-11.
- `app/core/database.py`: toggle `SQL_ECHO=true` para habilitar el log de SQL sólo cuando se captura
  la evidencia (default apagado, backward-compatible).

## Capabilities

### New Capabilities
- `test-cases`: los 9 casos mínimos de la consigna con su resultado esperado (US-701).

### Modified Capabilities
- Ninguna funcional: sólo se agrega el toggle de logging `SQL_ECHO` (no cambia el comportamiento).

## Impact

- **Código**: `app/core/database.py` (toggle echo), `test/*.http`, `test/C-08.sql`, `test/LEEME.md`,
  `test/evidencia_c07.txt`.
- **API**: sin cambios de superficie.
- **Gobernanza**: MEDIO → los casos se verifican contra la app real y documentan la respuesta esperada.
