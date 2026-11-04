# Preguntas Abiertas

> Fuente: `docs/MiniTP_Cap1a4_Consigna.pdf`. El texto de la consigna es bastante denso y coherente: no se detectaron contradicciones internas graves. Se listan primero ambigüedades reales y, al final, las incertidumbres del análisis de conocimiento (discovery).

## Inconsistencias detectadas

### IN-01 — La consigna describe el pipeline "Router → Service → Models" pero no define dónde queda la validación `page > pages` (422) de `GET /mascotas/`
**La consigna dice**: "Una página más allá de `pages` responde 422" (ejercicio 2), pero la tabla de la sección 2.8 asocia 422 a "el cuerpo o los parámetros no cumplen el contrato".
**Impacto**: es ambiguo decidir si el validador es de DTO (Pydantic, 422 automático por `size`) o lógica del service (422 manual cuando `page > pages`). El resultado HTTP es el mismo, pero el código cambia de lugar.
**Resolución propuesta**: `size` fuera de 1..100 y `page` no válido → 422 automático por contrato; `page > pages` → cálculo del service y respuesta 422 explícita del router.
**Estado**: implementación decidible sin bloqueo; no es inconsistente con la rúbrica (pide "envoltorio de paginación" como un solo ítem).

### IN-02 — Un mismo "modulo cliente.py" del laboratorio se menciona como entrega de la cátedra, pero los archivos de estructura del proyecto también listan un `service.py`/`router.py` genérico por módulo
**La consigna dice**: "La cátedra entrega el módulo app/modules/laboratorio/cliente.py" (ejercicio 6) y "la misma estructura en todos (models, schemas, service, router)".
**Impacto**: podría interpretarse que laboratorio necesita `models.py`/`schemas.py`, que no aplican (no hay persistencia para el laboratorio).
**Resolución propuesta**: laboratorio sin `models.py` (no hay entidad persistida); schemas inline (`{"vacuna": ..., "stock": ...}`) y service solo para el offload del hilo. Cualquier decisión en este sentido no toca puntos de la rúbrica.
**Estado**: asumir que laboratorio admite estructura reducida; no hay conflicto real.

## Preguntas abiertas (priorizadas)

| Prioridad | ID | Pregunta | Bloquea | Decisor |
|-----------|----|----------|---------|---------|
| Media | QA-01 | ¿Los otros listados (`GET /practicas/`, `GET /duenios/{id}/mascotas/`) usan el envoltorio `{items,total,page,size,pages}` o listas simples? La consigna solo lo exige en `GET /mascotas/`. | Implementación de épicas 2/5 (baja en la práctica) | Cátedra / suposición registrada (SU-06) |
| Media | QA-02 | ¿El `DuenioRead` de `POST /duenios/` incluye `ficha: null` cuando el dueño aún no tiene ficha? | Contrato exacto de respuesta (menor) | Cátedra |
| Media | QA-03 | ¿Qué mecanismo preferirá la cátedra para ejecutar la función bloqueante `consultar_stock` fuera del bucle de eventos: `ThreadPoolExecutor`, `anyio.to_thread.run_sync`, u otro? La consigna no lo impone. | Implementación de US-601 | Cátedra (riegos en DD-07) |
| Baja | QA-04 | ¿Los casos .http se corren como un único archivo concatenado o archivos separados por caso (`C-01.http` ...)? La consigna solo dice "archivos .http de test/". | Organización de `test/` (cosmético) | Alumno |
| Baja | QA-05 | ¿Está bien que NO exista `GET /duenios/` (listado general)? La tabla de endpoints de referencia no lo incluye. | Nada (la consigna es explícita) — confirmación | Cátedra |
| Baja | QA-06 | ¿La fecha del turno se devuelve normalizada a UTC (`Z`) o se conserva el offset original? El ejemplo de la consigna muestra normalización (`10:30-03:00` → `13:30Z`). | Formato de respuesta (menor) | Alumno (SU-03) |

## [DISCOVERY] Incertidumbres del modo ingest

- [DISCOVERY] `scale` no pudo inferirse con confianza total a partir de la consigna: es un TP académico para una sola veterinaria sin autenticación, así que se tomó el valor de mejor esfuerzo **`single_user`** (inferido, baja confianza). Confirmar que no se espera un escenario multi-usuario real.
- [DISCOVERY] `system_type` se fijó por el documento como **REST API** (no hay frontend ni UI); es una decisión documental de alta confianza igualmente.
- [DISCOVERY] `stack`, `domain` y `needs_infra` se infieren de la sección "Requisitos técnicos" de la consigna (alta confianza): dictados por la cátedra, no por decisión del proyecto.
- El top-level `discovery` del orquestador está en `{ "skipped": true }`: no hubo fase de market discovery, así que **no hay campos pre-cargados** y ningún dato proviene de esa sección.
