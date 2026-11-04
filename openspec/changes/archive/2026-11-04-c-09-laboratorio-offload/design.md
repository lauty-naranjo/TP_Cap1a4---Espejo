# Design — c-09-laboratorio-offload

## Context

El placeholder de `laboratorio/cliente.py` espera el código que entrega la cátedra (SU-05). La
consigna (Ejercicio 6) fija ese código exacto y exige llamarlo fuera del bucle de eventos. Flujos
12/13 de `07_flujos_principales.md`.

## Goals / Non-Goals

**Goals:**
- `consultar_stock` tal cual la entrega la cátedra, sin modificarla (US-601 CA-1).
- `GET /laboratorio/stock/{vacuna}` → `{"vacuna", "stock"}` con offload a hilo (US-601 CA-2).
- El bucle no se bloquea: 3 consultas en paralelo y `/health/live` responde de inmediato (CA-3/C-09).

**Non-Goals:**
- Persistencia para el laboratorio (IN-02: sin `models.py`/`schemas.py`).
- Casos `.http` de la consigna (C-10); README (C-11).

## Decisions

### D1 — Código exacto de la cátedra (SU-05)
- `cliente.py` se reemplaza por `def consultar_stock(vacuna: str) -> int` con `time.sleep(1)` y
  `return 10 + len(vacuna)` (sin tocar).

### D2 — Offload con `anyio.to_thread.run_sync` (DD-07, QA-03)
- La consigna no impone el mecanismo; se elige `anyio.to_thread.run_sync` (anyio ya es dependencia de
  Starlette/FastAPI): descarga la función al worker pool y libera el event loop. Alternativa válida:
  `ThreadPoolExecutor` (DD-07).

### D3 — Respuesta inline, sin schemas (IN-02)
- No hay entidad persistida; el service devuelve `{"vacuna": ..., "stock": ...}` como dict.

## Risks / Trade-offs

- Overhead de un hilo por llamada (aceptable con latencia de 1 s). El test de paralelización (3 × 1 s
  ≈ 1 s, umbral < 2.5 s) detecta regresiones a llamada bloqueante serial.

## Migration Plan

- Sin cambios de esquema. Rollback = revertir código.

## Open Questions

- QA-03 (mecanismo exacto de offload) → resuelto: `anyio.to_thread.run_sync`.
