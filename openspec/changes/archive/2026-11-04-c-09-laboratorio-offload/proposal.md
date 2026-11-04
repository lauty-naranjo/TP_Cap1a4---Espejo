# Proposal — c-09-laboratorio-offload

## Why

Todos los handlers deben ser `async def` y ninguno puede ejecutar una llamada bloqueante en el bucle
de eventos. La cátedra entrega `app/modules/laboratorio/cliente.py` (hoy un placeholder) con
`consultar_stock(vacuna)` sincrónica (`time.sleep(1)`). La consigna (Ejercicio 6, US-601) exige
llamarla sin modificarla y fuera del bucle, para que `GET /health/live` siga respondiendo mientras
hay consultas al laboratorio en marcha.

## What Changes

- `app/modules/laboratorio/cliente.py`: reemplaza el placeholder por el código exacto de la consigna
  (`consultar_stock` con `time.sleep(1)`, SU-05).
- `app/modules/laboratorio/service.py`: `obtener_stock` descarga la función a un hilo con
  `anyio.to_thread.run_sync` (offload fuera del event loop, DD-07/QA-03).
- `app/modules/laboratorio/router.py`: `GET /laboratorio/stock/{vacuna}` → `{"vacuna", "stock"}`.
- `app/main.py`: registra el router de `laboratorio`.
- `test/test_laboratorio.py`: respuesta correcta + offload que paraleliza 3 consultas (no serializa).

## Capabilities

### New Capabilities
- `laboratorio-offload`: consulta al laboratorio fuera del bucle de eventos (US-601).

### Modified Capabilities
- Ninguna.

## Impact

- **Código**: `app/modules/laboratorio/{cliente,service,router}.py`, `app/main.py`,
  `test/test_laboratorio.py`.
- **API**: nace `GET /laboratorio/stock/{vacuna}`.
- **Base de datos**: sin persistencia (IN-02): no hay `models.py`.
- **Gobernanza**: nivel ALTO → no bloquear el event loop (RN-AS-01/02), evidencia del caso C-09.
