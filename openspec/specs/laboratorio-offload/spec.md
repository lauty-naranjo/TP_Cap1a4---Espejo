# laboratorio-offload Specification

## Purpose
Consulta al laboratorio de vacunas usando una biblioteca sincrónica (`consultar_stock`) llamada sin
modificarla y fuera del bucle de eventos, de modo que el servidor siga atendiendo mientras hay
consultas en marcha (US-601).

## Requirements

### Requirement: Stock del laboratorio fuera del bucle de eventos
El sistema SHALL exponer `GET /laboratorio/stock/{vacuna}` que responde `{"vacuna": ..., "stock": ...}`
llamando a `consultar_stock(vacuna)` (sincrónica, 1 s) sin modificarla y descargándola a un hilo fuera
del bucle de eventos.

#### Scenario: Consulta de stock
- **WHEN** se solicita el stock de una vacuna
- **THEN** responde 200 con el stock calculado por la biblioteca

### Requirement: No bloquear el bucle de eventos
El sistema SHALL mantener el bucle libre mientras hay consultas al laboratorio en marcha: todas las
llamadas bloqueantes se descargan a hilos y `GET /health/live` responde de inmediato aunque haya
varias consultas simultáneas.

#### Scenario: Concurrencia con el health check
- **WHEN** hay varias consultas al laboratorio en marcha y se llama a `GET /health/live`
- **THEN** el health check responde de inmediato (200)
