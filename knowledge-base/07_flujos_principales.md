# Flujos Principales

> Fuente: `docs/MiniTP_Cap1a4_Consigna.pdf`. Cada flujo extremo a extremo con componentes, transacciones y manejo de errores. Pipas: un solo proceso FastAPI sobre PostgreSQL.

## Flujo 1: Arranque y ciclo de vida (lifespan)
**Disparador**: `uvicorn` arranca / apaga el proceso.
**Actor**: sistema (sin usuario).

**Pasos**:
1. `app/main.py` crea la aplicación FastAPI.
2. En el **lifespan**: se crea el motor asincrónico (`create_async_engine` con `DATABASE_URL`) y la fábrica de sesiones (`async_sessionmaker`), se guardan en `app.state`.
3. Se registran los routers de los módulos: `health`, `duenios`, `mascotas`, `practicas`, `turnos` y `laboratorio`.
4. Al apagar: el motor se **cierra** (libera el pool).

**Diagrama**:
```
uvicorn → main.lifespan → app.state.engine / app.state.sessionmaker → routers
                                    ↓ (shutdown)
                              engine.dispose()
```

**Casos de error**:
- `DATABASE_URL` ausente o malformada → falla en el arranque (leida por `app/core/config.py` desde `.env`; lo indica el `env.example`).

## Flujo 2: Sesión por petición
**Disparador**: cualquier request.
**Actor**: handler HTTP.

**Pasos**:
1. FastAPI resuelve `Depends(get_session)` → una sesión nueva por petición (creada con `expire_on_commit=False`).
2. El handler delega en el **service** del módulo, pasándole la sesión como parámetro.
3. El service ejecuta consultas con precarga y hace commit/rollback según corresponda.
4. Al terminar, la dependencia cierra la sesión.

Nota: es el flujo aplicado por TODOS los demás flujos (no lo repito).

> (línea de referencia: la sesión "llega a cada handler con Depends(get_session), una por petición, creada con expire_on_commit=False").

## Flujo 3: Alta de dueño (RN-01, IntegrityError-first)
**Disparador**: `POST /duenios/`.
**Actor**: operador (cliente HTTP).

**Pasos**:
1. Router valida cuerpo con `DuenioCreate` (sin `id`). Cuerpo inválido → 422 (FastAPI).
2. Router delega en `duenios.service`.
3. Service **escribe directamente** (sin consulta previa "¿ya existe?") — RN-INT-01.
4. Bien → commit → `DuenioRead` → **201**.
5. Si la base rechaza por `email` UNIQUE: `IntegrityError` atrapado en el service → **rollback** → respuesta **409 con mensaje propio** (ej. "email ya registrado").

**Diagrama**:
```
Cliente → Router (422 si DTO inválido) → Service → INSERT duenio
                                         ├─ ok    → commit → 201 + DuenioRead
                                         └─ IntegrityError → rollback → 409 mensaje propio
```

**Casos de error**: email repetido → 409 (C-02); DTO inválido → 422.

## Flujo 4: PATCH parcial de dueño
**Disparador**: `PATCH /duenios/{id}`.
**Actor**: operador.

**Pasos**:
1. Router valida `DuenioUpdate`; si el id no es entero → 422 **sin ejecutar el handler** (C-01).
2. Service busca el dueño (404 si no existe).
3. Service aplica **solo los campos enviados** con `exclude_unset` (sección 2.6) — los ausentes no se tocan.
4. Commit → 200 con el dueño (y ficha) actualizados; UNIQUE rechazada → 409.

**Casos de error**: 404 no existe; 409 integridad; 422 contrato/parámetro.

## Flujo 5: Segunda ficha del dueño (1:1, RN-03)
**Disparador**: `POST /duenios/{id}/ficha`.
**Actor**: operador.

**Pasos**:
1. Router valida `FichaCreate`; 422 si rompe contrato; 404 si el dueño no existe (404 definido por la tabla de endpoints).
2. Service INSERT en `ficha_duenio`.
3. Base rechaza por UNIQUE en `ficha_duenio.duenio_id` (segunda ficha) → `IntegrityError` → rollback → **409** (caso C-03).
4. Éxito → 201 + `FichaRead`.

**Casos de error**: 404 dueño inexistente; 409 ficha ya existente.

## Flujo 6: Alta de mascota (agregación)
**Disparador**: `POST /mascotas/`.
**Actor**: operador.

**Pasos**:
1. `MascotaCreate` trae `nombre`, `especie` y `duenio_id` (en la **agregación viaja un id**).
2. Service INSERT mascota; la FK garantiza que el dueño exista.
3. Dueño inexistente → FK violada → `IntegrityError` → rollback → **409**, no queda guardado nada (C-04).
4. Éxito → 201 + `MascotaRead`.

**Casos de error**: 409 dueño inexistente; 422 contrato.

## Flujo 7: Listado de mascotas (paginación)
**Disparador**: `GET /mascotas/?page=&size=` — oculta el detalle de la validación de rango y el número de páginas.
**Actor**: operador.

**Pasos**:
1. FastAPI valida parámetros: `size` fuera de 1..100 → **422**.
2. Service consulta total y página con límite/offset.
3. Envoltorio de la sección 2.9: `{ items, total, page, size, pages }`.
4. Página más allá de `pages` → **422**; la primera página siempre responde, aunque no haya resultados.

**Casos de error**: 422 por `size` fuera de rango o `page > pages`.

## Flujo 8: Alta de turno (el flujo central, Ejercicio 4)
**Disparador**: `POST /turnos/`.
**Actor**: operador.

**Pasos**:
1. Router valida `TurnoCreate`: `mascota_id`, `fecha` (con zona horaria), `motivo`, `practicas: [{practica_id}, ...]`.
   - Lista vacía → **422** (RN-05).
   - `practica_id`/`total`/precios NO viajan en el DTO (RN-06).
2. Service abre **una sola transacción** (RN-TX-01):
   a. Trae los precios del catálogo por cada `practica_id pedido`.
   b. Si una práctica no existe → **rollback total** → 409; del turno no queda guardado nada (C-04).
   c. Inserta el `turno` (FK a mascota garantizada por la base).
   d. Inserta cada `turno_practica` con `precio_unitario` **copiado del catálogo** (freeze; RN-DS-02).
   e. Calcula `total` el **servidor**: suma de `precio_unitario`; la base lo respalda con CHECK `total >= 0`.
   f. Si un `practica_id` aparece dos veces → violación de PK compuesta → rollback → 409 (RN-07).
3. Commit → `TurnoRead` con: `id`, `fecha`, `motivo`, `total`, `mascota` embebida, `practicas` con `practica_id`, `nombre` y `precio_unitario` → **201**.

**Contrato exacto (consigna)**:
```json
// REQUEST
{ "mascota_id": 1, "fecha": "2026-11-12T10:30:00-03:00", "motivo": "Control anual",
  "practicas": [ { "practica_id": 1 }, { "practica_id": 3 } ] }
// RESPONSE 201
{ "id": 2, "fecha": "2026-11-12T13:30:00Z", "motivo": "Control anual", "total": "27000.00",
  "mascota": { "id": 1, "nombre": "Toby", "especie": "perro" },
  "practicas": [
    { "practica_id": 1, "nombre": "Consulta", "precio_unitario": "15000.00" },
    { "practica_id": 3, "nombre": "Vacuna antirrábica", "precio_unitario": "12000.00" } ] }
```
(Observar: la fecha `10:30:00-03:00` se devuelve como `13:30:00Z`; misma hora, normalizada a UTC. Decimales como string.)

**Casos de error**: 422 lista vacía o contrato; 409 práctica inexistente / duplicada / mascota inexistente; todo-o-nada.

## Flujo 9: Lecturas con relaciones sin N+1 (Ejercicio 5)
**Disparador**: detalle (`GET /duenios/{id}`, `GET /mascotas/{id}`, `GET /turnos/{id}`) o `GET /duenios/{id}/mascotas`.
**Actor**: operador.

**Pasos**:
1. Service construye el SELECT con **carga anticipada dictada por la forma de la relación**:
   - joinedload (a uno): dueño→ficha; mascota→dueño; turno→mascota.
   - selectinload (colecciones): dueño→mascotas; turno→practicas (tabla intermedia y práctica).
2. La respuesta usa los datos precargados (nunca recorrido perezoso: fallaría con `MissingGreenlet`).
3. El número de consultas es **fijo**: detalle de turno con 1 o con 3 prácticas → misma cantidad de consultas (C-07, verificable con `echo=True`).

**Diagrama** (turno):
```
GET /turnos/{id} → service → SELECT turno LEFT JOIN mascota (joinedload)
                          + SELECT mascotas de turno_practica+practica WHERE turno_id IN (...) (selectinload)
                           → exactamente 2 consultas, digamos K prácticas (que no crece)
```

**Casos de error**: 404 no existe; 422 parámetro no entero.

## Flujo 10: Borrado de turno (composición, CASCADE)
**Disparador**: `DELETE /turnos/{id}`.
**Actor**: operador.

**Pasos**:
1. Service busca el turno (404 si no existe).
2. `DELETE` del turno → la **base** borra sus `turno_practica` por `ON DELETE CASCADE` (RN-09); el ORM no toca esas filas (`passive_deletes`, RN-INT-02).
3. Éxito → **204** (C-05: sus prácticas ya no están).
4. Sin conflicto posible en este borrado (no hay referencias a turno).

**Casos de error**: 404 si no existe.

## Flujo 11: Borrado de dueño (agregación, RESTRICT)
**Disparador**: `DELETE /duenios/{id}`.
**Actor**: operador.

**Pasos**:
1. Service busca el dueño (404 si no existe).
2. `DELETE` del dueño:
   - Si tiene mascotas → la FK de `mascota.duenio_id` con ON DELETE RESTRICT la rechaza → `IntegrityError` → rollback → **409** (RN-08, C-05).
   - Si no tiene mascotas → éxito → **204**.

**Casos de error**: 404 no existe; 409 con mascotas a su nombre.

## Flujo 12: Consulta al laboratorio (asincronía, Ejercicio 6)
**Disparador**: `GET /laboratorio/stock/{vacuna}`.
**Actor**: operador.

**Pasos**:
1. Handler `async def` recibe la ruta.
2. En vez de llamar directo (bloquearía 1 s el bucle), el handler **descarga la función** `consultar_stock(vacuna)` (sincrónica, entregada por la cátedra y sin modificar) a un **hilo externo** (mecanismo exacto a decidir; ver DD-07/QA-03).
3. Mientras la llamada corre fuera del bucle, el servidor sigue atendiendo otras peticiones.
4. Responde `{"vacuna": ..., "stock": ...}` → 200.

**Diagrama**:
```
GET /laboratorio/stock/antirrabica ─→ handler(async)
                                          │ anyio/hilo
                                          ▼
                                 time.sleep(1)  [FUERA del event loop]
otras peticiones siguen atendiéndose: GET /health/live responde al instante (C-09)
```

**Casos de error**: consigna define 200 como único código documentado; consistencia (C-09) es el resultado esperado.

## Flujo 13: Health checks
**Disparador**: `GET /health/live` / `GET /health/ready`.
**Actor**: operador / orquestador.

**Pasos**:
1. `/health/live`: no toca la base → `{"estado": "vivo"}`, 200, diagnóstico de proceso.
2. `/health/ready`: ejecuta `SELECT 1`; si la base no contesta → **503**.

**Casos de error**: base caída en `/health/ready` → 503.

## Flujo 14: Reinicio y prueba (tooling)
**Disparador**: `python reiniciar.py` y luego runner de `test/*.http`.
**Actor**: desarrollador/corrector.

**Pasos**:
1. `reiniciar.py` borra las tablas, las crea con `SQLModel.metadata.create_all` y carga el seed (2 dueños — uno con ficha -, 3 mascotas, 4 prácticas, 1 turno con 2 prácticas).
2. Se corren los casos `test/*.http` (y el archivo `.sql` del caso C-08) en orden, cada uno con comentario de la respuesta esperada.
3. La consola con `echo=True` da la evidencia de C-07 (misma cantidad de consultas).
