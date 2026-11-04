# Funcionalidades

> Fuente: `docs/MiniTP_Cap1a4_Consigna.pdf`. Organizada por **épica = ejercicio de la consigna** (en el mismo orden para poder verificar cobertura completa). El objetivo del TP es completar **la totalidad** de las consignas.

## Épica 1: Proyecto, conexión y ciclo de vida (Ejercicio 1 — 10 % / 10 puntos)

### US-101 — Ciclo de vida del motor y la sesión
**Como** desarrollador del servicio
**Quiero** crear el motor asincrónico y la fábrica de sesiones en el `lifespan` de la aplicación, guardarlos en `app.state` y cerrar el motor al apagar
**Para** integrar el ciclo de vida de la base con el de la aplicación (sección 1.9)

**Criterios de aceptación**:
- [ ] CA-1: motor asincrónico + fábrica de sesiones creados en `lifespan`, almacenados en `app.state`, motor cerrado en el apagado.
- [ ] CA-2: la sesión llega a cada handler con `Depends(get_session)`, una por petición, creada con `expire_on_commit=False` (sección 4.5).

### US-102 — Health checks
**Como** operador del servicio
**Quiero** un endpoint que diga que el proceso está vivo y otro que diga que la base está lista
**Para** distinguir fallas de proceso y de dependencia

**Criterios de aceptación**:
- [ ] CA-1: `GET /health/live` no toca la base → `{"estado": "vivo"}`, 200 y siempre rápido (aunque haya consultas al laboratorio en marcha — C-09).
- [ ] CA-2: `GET /health/ready` ejecuta `SELECT 1`; responde 503 si la base no contesta.

**Reglas relacionadas**: RN-HL-01, RN-HL-02.

### US-103 — Configuración por entorno
**Como** desarrollador del servicio
**Quiero** leer `DATABASE_URL` del entorno vía archivo `.env` no versionado, con un `env.example` sin secretos
**Para** desplegar el proyecto sin credenciales reales en el repositorio

**Criterios de aceptación**:
- [ ] CA-1: `app/core/config.py` lee `DATABASE_URL` (python-dotenv 1.0).
- [ ] CA-2: repositorio incluye `env.example` con la forma del valor y sin ningún secreto; `.env` no se sube.

**Reglas relacionadas**: RN-HTTP-01 (entorno).

## Épica 2: Contratos y CRUD (Ejercicio 2 — 20 % / 20 puntos)

### US-201 — Alta de dueño
**Como** operador de la veterinaria
**Quiero** registrar un dueño con nombre y email
**Para** tenerlo como cliente del sistema

**Criterios de aceptación**:
- [ ] CA-1: `POST /duenios/` con `DuenioCreate` (sin `id`) → 201 + `DuenioRead`.
- [ ] CA-2: email repetido → 409 con mensaje propio, atrapando `IntegrityError` sin consulta previa (RN-01).
- [ ] CA-3: cuerpo inválido → 422.

**Reglas relacionadas**: RN-01, RN-HTTP-01, RN-HTTP-02, RN-INT-01.

### US-202 — Detalle, PATCH parcial y borrado de dueño
**Como** operador de la veterinaria
**Quiero** consultar y editar un dueño, y borrarlo si no tiene mascotas
**Para** mantener el registro actualizado

**Criterios de aceptación**:
- [ ] CA-1: `GET /duenios/{id}` → dueño **con su ficha** (precargada, consultas fijas); 404 si no existe; 422 si el id no es entero (C-01).
- [ ] CA-2: `PATCH /duenios/{id}` con `DuenioUpdate` aplica sólo los campos enviados vía `exclude_unset` (sección 2.6). Códigos 200/404/409/422.
- [ ] CA-3: `DELETE /duenios/{id}` → 204; 409 si tiene mascotas (RESTRICT, RN-08, caso C-05); 404 si no existe.

**Reglas relacionadas**: RN-03 (vía ficha embebida), RN-08, RN-INT-01, RN-REL-01, RN-REL-03.

### US-203 — Ficha del dueño (uno a uno)
**Como** dueño (registrado por el operador)
**Quiero** tener una ficha con teléfono y dirección
**Para** que la veterinaria pueda contactarme

**Criterios de aceptación**:
- [ ] CA-1: `POST /duenios/{id}/ficha` con `FichaCreate` → 201 + `FichaRead`; 404 si el dueño no existe; 409 si ya tiene ficha (UNIQUE en `ficha_duenio.duenio_id`, RN-03, caso C-03).
- [ ] CA-2: la navegación 1:1 está declarada en ambos extremos y `Duenio.ficha` devuelve **un objeto, no una lista** (RN-REL-02).
- [ ] CA-3: no existen GET/PATCH dedicados de ficha (la ficha se lee embebida en el dueño) — según la tabla de endpoints de la consigna.

**Reglas relacionadas**: RN-03, RN-REL-01, RN-REL-02, RN-INT-01.

### US-204 — CRUD de mascotas (con paginación)
**Como** operador de la veterinaria
**Quiero** registrar mascotas a nombre de un dueño y listarlas paginadas
**Para** llevar el registro de pacientes

**Criterios de aceptación**:
- [ ] CA-1: `POST /mascotas/` con `MascotaCreate` que trae `duenio_id` existente (en la **agregación** viaja un id) → 201; dueño inexistente → 409 (C-04); especie/nombre válidos.
- [ ] CA-2: `GET /mascotas/` devuelve el envoltorio `{ items, total, page, size, pages }`; `size` por defecto 20, rango 1..100; página más allá de `pages` → 422; la primera página siempre responde aunque no haya resultados.
- [ ] CA-3: `GET /mascotas/{id}` → mascota **con su dueño** (joinedload a uno); 404 si no existe.
- [ ] CA-4: según la consigna, no hay PATCH ni DELETE de mascotas (superficie de endpoints dictada por la cátedra).

**Reglas relacionadas**: RN-HTTP-04, RN-INT-01, RN-REL-03.

### US-205 — CRUD del catálogo de prácticas
**Como** operador de la veterinaria
**Quiero** crear prácticas con precio (consulta, vacuna, desparasitación, ...) y listar el catálogo
**Para** armar los turnos con precios actuales del catálogo

**Criterios de aceptación**:
- [ ] CA-1: `POST /practicas/` con `PracticaCreate` → 201; nombre repetido → 409 (RN-02); precio ≤ 0 → 422 por DTO o rechazo del CHECK (RN-04).
- [ ] CA-2: `GET /practicas/` → catálogo completo (lo que usemos: lista simple según consigna — ver QA-01 en `10_preguntas_abiertas.md`).

**Reglas relacionadas**: RN-02, RN-04, RN-INT-01.

## Épica 3: Modelos, restricciones y relaciones (Ejercicio 3 — 30 % / 30 puntos)

### US-301 — Modelos de tabla con restricciones completas
**Como** desarrollador del servicio
**Quiero** escribir los modelos del modelo de dominio (`duenio`, `ficha_duenio`, `mascota`, `practica`, `turno`, `turno_practica`) con todas sus restricciones
**Para** que la base garantice la integridad (no el ORM ni el service)

**Criterios de aceptación**:
- [ ] CA-1: claves foráneas con su regla de borrado (RESTRICT en `mascota.duenio_id`, CASCADE en `turno_practica.turno_id`), UNIQUE, CHECK (precio > 0, total >= 0, precio_unitario > 0) e índices pedidos.
- [ ] CA-2: índices en las FKs (PostgreSQL no los crea solo): `mascota.duenio_id`, `turno.mascota_id`, `turno_practica.practica_id`; **no** en `turno_practica.turno_id` (cubierto por la PK compuesta — explicación de 1–2 líneas **obligatoria en el README**).
- [ ] CA-3: `Relationship(back_populates="...")` en los **dos extremos** de cada FK; `Duenio.ficha` objeto; `passive_deletes` en `Turno.practicas` (el borrado lo decide la base, no el ORM).

**Reglas relacionadas**: RN-01..RN-09, RN-REL-01..03, RN-DS-01.

### US-302 — reiniciar.py (estado conocido)
**Como** corrector de la cátedra
**Quiero** un script que borre las tablas, las cree con `create_all` y cargue datos iniciales
**Para** correr los casos de prueba desde un estado reproducible

**Criterios de aceptación**:
- [ ] CA-1: `python reiniciar.py` funciona **sobre una base vacía** (condición para que el TP se corrija).
- [ ] CA-2: seed al menos: **2 dueños** (uno con ficha), **3 mascotas**, **4 prácticas**, **1 turno con 2 prácticas**.

## Épica 4: Altas con relaciones — ids y datos (Ejercicio 4 — 15 % / 15 puntos)

### US-401 — Alta de turno con prácticas anidadas (composición + todo-o-nada)
**Como** operador de la veterinaria
**Quiero** reservar un turno enviando la lista de prácticas dentro del cuerpo
**Para** que el turno quede completo en una sola operación y con su precio congelado

**Criterios de aceptación**:
- [ ] CA-1: `POST /turnos/` recibe `mascota_id` (asociación viaja id), `fecha` (con zona horaria), `motivo` y `practicas: [{practica_id}, ...]` (composición solo necesita ids que identifican datos que nacen con el turno; el DTO anidado no trae precio ni total).
- [ ] CA-2: al menos una práctica; lista vacía → 422 (RN-05). Práctica repetida → 409 (RN-07, PK compuesta). Práctica inexistente → 409 y **no queda guardado nada** (todo-o-nada, C-04).
- [ ] CA-3: el service copia el precio de cada práctica del catálogo a `precio_unitario` (RN-06, RN-DS-02) y calcula `total`; en **una sola transacción** (RN-TX-01).
- [ ] CA-4: respuesta `TurnoRead` con mascota embebida y prácticas con `precio_unitario` copiado; ejemplo objetivo (contrato exacto de la consigna): body `{"mascota_id":1, "fecha":"2026-11-12T10:30:00-03:00", "motivo":"Control anual", "practicas":[{"practica_id":1},{"practica_id":3}]}` → 201 con `total: "27000.00"` y `fecha` normalizada (`2026-11-12T13:30:00Z`).

**Reglas relacionadas**: RN-05, RN-06, RN-07, RN-TX-01, RN-DS-01, RN-DS-02, RN-INT-01, RN-REL-03.

## Épica 5: Lecturas sin N+1 (Ejercicio 5 — 15 % / 15 puntos)

### US-501 — Carga anticipada declarada en cada lectura
**Como** desarrollador del servicio
**Quiero** que toda respuesta que incluya datos de una relación los obtenga con carga anticipada declarada en la misma consulta
**Para** no caer en N+1 ni depender de la carga perezosa (que en async falla con `MissingGreenlet`)

**Criterios de aceptación**:
- [ ] CA-1: `joinedload` para relaciones «a uno» (mascota→dueño; turno→mascota; dueño→ficha) y `selectinload` para colecciones (dueño→mascotas; turno→ turno_practica/practicas) (sección 4.6).
- [ ] CA-2: el detalle de un turno con mascota y prácticas se resuelve con un **número fijo de consultas** que no crece con la cantidad de prácticas (caso C-07).
- [ ] CA-3: ídem para el detalle de un dueño con su ficha.
- [ ] CA-4: verificable con `echo=True` en la consola (evidencia exigida en la entrega).

**Reglas relacionadas**: RN-REL-03.

## Épica 6: Asincronía sin bloqueos (Ejercicio 6 — 10 % / 10 puntos)

### US-601 — Módulo laboratorio con biblioteca sincrónica
**Como** operador de la veterinaria
**Quiero** consultar el stock de vacunas informado por el laboratorio
**Para** decidir si se puede vacunar sin bloquear el servidor

**Criterios de aceptación**:
- [ ] CA-1: la cátedra entrega `app/modules/laboratorio/cliente.py` con `consultar_stock(vacuna)` sincrónica (`time.sleep(1)`); se usa **sin modificarla**.
- [ ] CA-2: `GET /laboratorio/stock/{vacuna}` responde `{"vacuna": ..., "stock": ...}` llamando a esa función **fuera del bucle de eventos**.
- [ ] CA-3: con N consultas al laboratorio en marcha, `GET /health/live` sigue respondiendo de inmediato (C-09).
- [ ] CA-4: todos los handlers son `async def`; ninguna llamada bloqueante en el bucle (sección 3.6).

**Reglas relacionadas**: RN-AS-01, RN-AS-02.

## Épica 7: Casos de prueba mínimos (test/)

### US-701 — Casos .http demostrando todo el comportamiento exigido
**Como** corrector de la cátedra
**Quiero** archivos `.http` (a correr después de `python reiniciar.py`) que demuestren los casos mínimos con comentario de la respuesta esperada
**Para** comprobar el cumplimiento de las reglas de negocio

**Criterios de aceptación** (tabla de la consigna):
- [ ] CA-1 (**C-01**): parámetro de ruta no entero (`/duenios/abc`) → 422, sin ejecutar el handler.
- [ ] CA-2 (**C-02**): email de dueño o nombre de práctica repetido → 409 con mensaje propio.
- [ ] CA-3 (**C-03**): segunda ficha para el mismo dueño → 409.
- [ ] CA-4 (**C-04**): mascota con dueño inexistente, y turno con una práctica inexistente → 409; del turno no queda guardado nada.
- [ ] CA-5 (**C-05**): borrar un dueño con mascotas → 409; borrar un turno → 204 y sus prácticas ya no están.
- [ ] CA-6 (**C-06**): turno válido con dos prácticas → 201 con precios copiados y total calculado.
- [ ] CA-7 (**C-07**): detalle de un turno con una práctica y con tres → misma cantidad de consultas en la consola (`echo=True`).
- [ ] CA-8 (**C-08**): `UPDATE practica SET precio = 0` ejecutado directo en la base (**en un archivo `.sql`**) → la base lo rechaza por el CHECK. Nota: este caso usa un archivo `.sql` distinto de los `.http`.
- [ ] CA-9 (**C-09**): tres consultas simultáneas al laboratorio y un `GET /health/live` → el de salud responde de inmediato.

## Épica 8: Formato de entrega

### US-801 — Repositorio de entrega
**Como** alumno
**Quiero** entregar el repositorio con el formato exigido
**Para** que el TP se corrija sin observaciones bloqueantes

**Criterios de aceptación**:
- [ ] CA-1: repositorio con código fuente completo, `requirements.txt`, `env.example`, `reiniciar.py` y carpeta `test/`; `.env` **no se sube**; sin credenciales reales en el repositorio.
- [ ] CA-2: `README.md` con los pasos para levantar el proyecto desde cero (entorno virtual, dependencias, `.env`, `python reiniciar.py` y arranque del servidor **con uvicorn**).
- [ ] CA-3: `README.md` con la **explicación del índice de `turno_practica.turno_id`** pedido en el modelo de dominio (1–2 líneas).
- [ ] CA-4: **evidencia del caso C-07**: fragmento de la consola con las consultas del detalle del turno con una práctica y con tres.
- [ ] CA-5: el proyecto levanta y crea su esquema con `python reiniciar.py` sobre una base vacía (condición de corrección).
