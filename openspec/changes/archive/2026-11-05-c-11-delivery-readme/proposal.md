# Proposal — c-11-delivery-readme

## Why

C-01..C-10 dejaron la API completa, con seed reproducible y los 9 casos de la consigna verdes, pero
falta el **formato de entrega obligatorio** (Épica 8, US-801): el repositorio todavía no tiene
`README.md`, y sin los pasos desde cero, la explicación del índice de `turno_practica.turno_id` y la
evidencia del caso C-07 integrada, el TP **no se corrige**. Es el último eslabón del camino crítico y
la condición que cierra la cursada.

## What Changes

- **`README.md`** nuevo en la raíz, en español, con:
  - requisitos (Python 3.12, PostgreSQL 16) y pasos desde cero: entorno virtual → dependencias →
    `.env` desde `env.example` → `python reiniciar.py` → arranque con `uvicorn` (US-801 CA-2);
  - explicación de 1–2 líneas del **índice de `turno_practica.turno_id`**: la PK compuesta
    `(turno_id, practica_id)` ya sirve como índice por su primera columna, por eso no se declara un
    índice propio (US-301 CA-2, US-801 CA-3);
  - **evidencia del caso C-07** integrada: fragmento de consola con el detalle de un turno con 1 y con
    3 prácticas (2 consultas fijas), enlazando `test/evidencia_c07.txt` como fuente cruda
    (US-801 CA-4);
  - resumen de la estructura del proyecto y de los 9 casos de `test/` con el orden de ejecución;
  - chequeo final documentado: `python reiniciar.py` sobre base vacía crea las 6 tablas + seed y el
    proyecto levanta (US-801 CA-5).
- **`test/test_entrega.py`** nuevo: test de contrato de la entrega que verifica de forma automática
  CA-1..CA-4 (existencia y secciones del README, pasos y su orden, explicación del índice, evidencia
  C-07, `.env` ignorado y `env.example` sin credenciales reales). Se escribe **antes** del README
  (TDD: primero RED).
- **Sin cambios de código de aplicación ni de esquema**: la entrega es documentación + verificación.

## Capabilities

### New Capabilities
- `delivery-format`: contrato de entrega del repositorio — README reproducible desde cero,
  explicación del índice de `turno_practica.turno_id`, evidencia C-07 integrada, higiene de secretos
  (`.env` no versionado, `env.example` solo con placeholders) y verificación automática de ese
  contrato (US-801).

### Modified Capabilities
- Ninguna. El comportamiento de la API no cambia; C-11 sólo documenta y verifica lo ya construido.

## Impact

- **Documentación**: `README.md` (nuevo, raíz del repo).
- **Tests**: `test/test_entrega.py` (nuevo, sin base de datos); `test/evidencia_c07.txt` se referencia,
  no se regenera.
- **Código de aplicación**: ninguno (`app/**` intacto).
- **API / esquema**: sin cambios de superficie ni de base.
- **Gobernanza**: BAJO — el alcance es documental y la verificación es un test de contrato de archivos.
