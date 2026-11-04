# Tasks

> Regla dura afectada por tarea se marca inline con `<!-- rn: … -->`. Nota TDD: Strict TDD en el apply.

## 1. Cliente de la cátedra (US-601 CA-1, SU-05)

- [x] 1.1 Reemplazar `cliente.py` (placeholder) por el código exacto: `consultar_stock` con `time.sleep(1)`
  <!-- rn: usar la función SIN modificarla -->

## 2. Service con offload fuera del bucle (RN-AS-02)

- [x] 2.1 `obtener_stock` con `anyio.to_thread.run_sync(consultar_stock, vacuna)`
  <!-- rn: llamada bloqueante FUERA del event loop; handlers async def (RN-AS-01) -->

## 3. Router y registro en la app

- [x] 3.1 `app/modules/laboratorio/router.py`: `GET /laboratorio/stock/{vacuna}` → {"vacuna","stock"}
- [x] 3.2 Registrar `laboratorio_router` en el lifespan de `app/main.py`

## 4. Integración del cambio

- [x] 4.1 `pytest test/test_laboratorio.py` → 3 tests verdes (respuesta + offload paralelo)
- [x] 4.2 Smoke HTTP: `/laboratorio/stock/...` 200 y `/health/live` inmediato

## Workflow follow-up

- `/opsx:archive c-09-laboratorio-offload`.
- Marcar `[x]` en la entrada `[C-09]` de `CHANGES.md`.
