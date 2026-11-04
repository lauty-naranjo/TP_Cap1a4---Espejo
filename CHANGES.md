# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **API Veterinaria — TP Programación III (Cap. 1 a 4)**.
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

> Regla de oro del TP (user): **el TP debe completarse en su totalidad** — cada épica y user story
> de la consigna (`docs/consigna_extracted.txt`) tiene un change acá. Nada puede caerse del plan.
> Cobertura: Épica 1 → C-01/C-02 · Épica 2 → C-05/C-06 · Épica 3 → C-03/C-04 · Épica 4 → C-07 ·
> Épica 5 → C-08 · Épica 6 → C-09 · Épica 7 → C-10 · Épica 8 → C-11.
> Proyecto API REST **sin UI**: no hay changes de frontend ni de design-system (`visual_design.mode: deferred`).

---

## Cómo usar este documento

1. Identificar el change a implementar (verificar que sus dependencias están en `openspec/changes/archive/`).
2. Leer los docs de la knowledge-base indicados en "Leer antes".
3. Ejecutar `/opsx:propose <nombre-del-change>`.
4. Al terminar el change, archivarlo con `/opsx:archive <nombre-del-change>`.
5. Marcar el checkbox `[x]` en este archivo.

---

## Árbol de dependencias

```
C-01 foundation-setup
  └── C-02 database-lifespan-health            ← desbloquea TODO el dominio y la asincronía
        │
        ├── C-03 domain-models                 ← CRITICO: los 6 modelos que todo lo demás referencia
        │     │
        │     ├── C-04 reiniciar-seed          ← estado reproducible para todos los casos de prueba
        │     │
        │     └── C-05 duenios-crud-ficha      ← primer CRUD; patrón IntegrityError → 409
        │           └── C-06 mascotas-practicas-crud
        │                 └── C-07 turnos-alta-borrado   ← transacción todo-o-nada, precios congelados
        │                       └── C-08 lecturas-sin-n1 ← precarga transversal + consultas fijas
        │
        └── C-09 laboratorio-offload           ← solo necesita C-02 (paralelo desde GATE 2)
              │
(sincronización final: dominio + tooling + asincronía)
C-10 test-cases ← necesita C-04 ✓ + C-08 ✓ + C-09 ✓ (y C-05..C-07 vía C-08)
  └── C-11 delivery-readme                     ← evidencia C-07 nace al correr C-10
```

### Paralelismo por fase

> Cada "gate" es un punto de sincronización. Los changes dentro de un grupo pueden ejecutarse en paralelo.

```
GATE 0: ninguna
  → C-01 (solo)

GATE 1: C-01 ✓
  → C-02 database-lifespan-health              [Agente A]

GATE 2: C-02 ✓                                 ← FORK (dominio ∥ asincronía)
  → C-03 domain-models                         [Agente A]
  → C-09 laboratorio-offload                   [Agente B]

GATE 3: C-03 ✓                                 ← FORK (tooling ∥ CRUD core)
  → C-04 reiniciar-seed                        [Agente B — si C-09 ✓]
  → C-05 duenios-crud-ficha                    [Agente A]

GATE 4: C-05 ✓
  → C-06 mascotas-practicas-crud               [Agente A]

GATE 5: C-06 ✓
  → C-07 turnos-alta-borrado                   [Agente A]

GATE 6: C-07 ✓
  → C-08 lecturas-sin-n1                       [Agente A]

GATE 7: C-04 ✓ + C-08 ✓ + C-09 ✓               ← sincronización para la ronda de casos
  → C-10 test-cases                            [Agente B]

GATE 8: C-10 ✓
  → C-11 delivery-readme                       [Agente A]
```

### Camino crítico (9 changes — mínimo irreducible)

```
C-01 → C-02 → C-03 → C-05 → C-06 → C-07 → C-08 → C-10 → C-11
```

- `C-04` (reiniciar-seed) y `C-09` (laboratorio) **están fuera** del camino lineal: cuelgan de
  nodos tempranos (C-03 y C-02 respectivamente) y se reencuentran en C-10. Nunca bloquean al core.
- Sin C-04 y sin C-11 el TP **no se corrige** (condición explícita de la cátedra): quedan cubiertos
  por el join en C-10 antes de la entrega.

### Plan óptimo con 3 agentes

> Proyecto 100 % backend (API REST): Agent A = Backend Core (modelos/CRUD/turnos),
> Agente B = Backend Aux (infra temprana, laboratorio, seed, tests), Agente C = QA/Entrega (no hay UI: `visual_design.mode: deferred`).

```
Paso │ Agente A (Backend Core)            │ Agente B (Backend Aux)      │ Agente C (QA / Entrega)
─────┼────────────────────────────────────┼─────────────────────────────┼────────────────────────
  1  │ C-01 foundation-setup              │             —               │            —
  2  │ C-02 database-lifespan-health      │             —               │            —
  3  │ C-03 domain-models                 │ C-09 laboratorio-offload    │            —
  4  │ C-05 duenios-crud-ficha            │ C-04 reiniciar-seed         │            —
  5  │ C-06 mascotas-practicas-crud       │ (libre — respaldo review C-05) │         —
  6  │ C-07 turnos-alta-borrado           │             —               │            —
  7  │ C-08 lecturas-sin-n1               │             —               │            —
  8  │            —                       │ C-10 test-cases             │            —
  9  │ C-11 delivery-readme               │             —               │   revisión final de cobertura de épicas
```

*(Proyecto chico: la carga es despareja del lado de B/C; pueden adelantarse propuestas paralelas o
reviewes cruzadas de los CA de la consigna mientras A avanza por el camino crítico.)*

---

## FASE 0 — Infraestructura y ciclo de vida (Épica 1 · Ejercicio 1 — 10 %)

### [C-01] `foundation-setup`
- **Estado**: `[x]` archivado (2026-11-04) — `openspec/changes/archive/2026-11-04-c-01-foundation-setup/`
- **Scope**: Scaffolding del repositorio con la estructura EXACTA que dicta la consigna
  - Estructura de directorios: `app/` (`main.py`, `core/`, `modules/`), `test/`, `reiniciar.py` (placeholder), `requirements.txt`, `env.example`, `.gitignore` que excluye `.env`
  - `requirements.txt`: Python 3.12 + `fastapi[standard]>=0.111` (uvicorn incluido) + `sqlmodel>=0.0.24` + `sqlalchemy[asyncio]>=2.0` + `asyncpg>=0.30` + `python-dotenv>=1.0`
  - `app/core/config.py`: lee `DATABASE_URL` desde `.env` via python-dotenv (US-103 CA-1); falla en el arranque si falta
  - `env.example`: forma de `postgresql+asyncpg://usuario:password@localhost:5432/veterinaria` **sin ningún secreto** (US-103 CA-2)
  - `app/main.py`: app FastAPI mínima con hook `lifespan` vacío listo para C-02 (sin routers aún)
  - Cubre: **US-103** (Épica 1)
- **Dependencias**: ninguna
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md`
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios + §Variables de entorno
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-01, §DD-07/SU-07 (pinning de versiones)

---

### [C-02] `database-lifespan-health`
- **Estado**: `[x]` archivado (2026-11-04) — `openspec/changes/archive/2026-11-04-c-02-database-lifespan-health/`
- **Scope**: Ciclo de vida de la base + inyección de sesión + salud del servicio
  - `app/core/database.py`: fábrica de `create_async_engine` y `async_sessionmaker` con `expire_on_commit=False` (US-101 CA-2)
  - `app/main.py`: `lifespan` crea motor + sessionmaker en `app.state`, registra routers de la app y cierra el motor con `engine.dispose()` al apagar (US-101 CA-1)
  - Dependencia `get_session`: una sesión nueva por petición vía `Depends(get_session)` (Flujo 2)
  - Módulo `app/modules/health/router.py`: `GET /health/live` → `{"estado": "vivo"}` 200, **sin tocar la base** (RN-HL-01); `GET /health/ready` → `SELECT 1`, **503** si la base no contesta (RN-HL-02, US-102)
  - Tests: live responde aunque la DB esté caída; ready responde 503 con base caída
  - Cubre: **US-101, US-102** (Épica 1)
- **Dependencias**: `C-01`
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/07_flujos_principales.md` §Flujo 1, §Flujo 2, §Flujo 13
  - `knowledge-base/05_reglas_de_negocio.md` §Salud del servicio
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones aplicados (lifespan, DI)

---

## FASE 1 — Modelos, restricciones y estado reproducible (Épica 3 · Ejercicio 3 — 30 %)

### [C-03] `domain-models`
- **Estado**: `[x]` archivado (2026-11-04) — `openspec/changes/archive/2026-11-04-c-03-domain-models/`
- **Scope**: Los 6 modelos de tabla con TODAS las restricciones — base de integridad de todo el TP
  - Modelos: `Duenio` (tabla `duenio`), `FichaDuenio` (tabla `ficha_duenio`, **vive en el módulo `duenios`**), `Mascota` (`mascota`), `Practica` (`practica`), `Turno` (`turno`), `TurnoPractica` (tabla `turno_practica`, **vive en el módulo `turnos`**) — nombres de tablas/columnas obligatorios (SU-02): no quitar ni renombrar
  - Constraints: UNIQUE `duenio.email`, UNIQUE `ficha_duenio.duenio_id` (garantiza el 1:1), UNIQUE `practica.nombre`; CHECK `practica.precio > 0`, CHECK `turno.total >= 0`, CHECK `turno_practica.precio_unitario > 0`; FK `mascota.duenio_id` **ON DELETE RESTRICT**, FK `turno_practica.turno_id` **ON DELETE CASCADE**; PK compuesta `(turno_id, practica_id)`
  - Índices en FKs (PostgreSQL no los crea solo): `mascota.duenio_id`, `turno.mascota_id`, `turno_practica.practica_id`; **sin índice propio** en `turno_practica.turno_id` (cubierto por la PK compuesta — explicación 1-2 líneas queda para el README de C-11)
  - Relaciones declaradas **en los dos extremos** con `Relationship(back_populates=...)` (RN-REL-01); `Duenio.ficha` devuelve **objeto, no lista** (RN-REL-02)
  - `Turno.practicas` con `passive_deletes=True` — el borrado lo decide la base, no el ORM (RN-INT-02, DD-05)
  - Dinero con `Decimal`, nunca `float`; NUMERIC(10,2) precios / NUMERIC(12,2) total (RN-DS-01)
  - Tests: migrabilidad no aplica (sin Alembic — DD-03); verificación de restricciones vía `create_all` + escrituras inválidas rechazadas por la base (se demuestra en C-10)
  - Cubre: **US-301** (Épica 3)
- **Dependencias**: `C-02`
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` (completo: ERD, entidades, reglas transversales)
  - `knowledge-base/05_reglas_de_negocio.md` §RN-01..RN-09 + §Política de integridad + §Navegación de relaciones
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-03, §DD-05, §SU-02

---

### [C-04] `reiniciar-seed`
- **Estado**: `[ ]` pendiente
- **Scope**: Script de reinicio con seed conocido — condición para que el TP se corrija
  - `reiniciar.py` en raíz: borra las tablas (drop con orden inverso de dependencias), las crea con `SQLModel.metadata.create_all` y carga el seed (US-302 CA-1)
  - Seed mínimo obligatorio: **2 dueños** (uno con ficha), **3 mascotas**, **4 prácticas**, **1 turno con 2 prácticas** (US-302 CA-2; seed de `04_modelo_de_datos.md`)
  - Precios coherentes con el contrato del turno de ejemplo (Consulta 15000.00, Vacuna antirrábica 12000.00) para reproducir el caso C-06
  - `python reiniciar.py` funciona **sobre una base vacía** (condición de corrección de la cátedra)
  - Cubre: **US-302** (Épica 3)
- **Dependencias**: `C-03`
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Seed data inicial
  - `knowledge-base/07_flujos_principales.md` §Flujo 14
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-03

---

## FASE 2 — CRUD y contratos HTTP (Épica 2 · Ejercicio 2 — 20 %)

> Los changes C-05 y C-06 se proponen en secuencia (C-06 necesita dueños reales por FK), pero los
> módulos son independientes en código: la integridad la garantiza la base, no el ORM (DD-04).

### [C-05] `duenios-crud-ficha`
- **Estado**: `[ ]` pendiente
- **Scope**: Módulo `duenios` completo (dueño + ficha 1:1) con el patrón IntegrityError → 409
  - `app/modules/duenios/{models,schemas,service,router}.py`: modelos ya en C-03; DTOs separados `DuenioCreate` (sin `id`), `DuenioUpdate`, `FichaCreate`, `DuenioRead`, `FichaRead` (RN-HTTP-02)
  - `POST /duenios/` → 201 + `DuenioRead`; email repetido → 409 atrapando `IntegrityError` del INSERT (cero consulta previa "¿ya existe?", RN-01/RN-INT-01); cuerpo inválido → 422 (US-201)
  - `GET /duenios/{id}` → dueño **con su ficha** precargada (`joinedload` a uno); id no entero → 422 sin ejecutar el handler (caso C-01); 404 si no existe (US-202)
  - `PATCH /duenios/{id}` con `exclude_unset` — aplica solo los campos enviados (RN-HTTP-03); 200/404/409/422
  - `DELETE /duenios/{id}` → 204; **409 si tiene mascotas** (FK RESTRICT + `IntegrityError` → rollback, RN-08, caso C-05); 404 si no existe
  - `POST /duenios/{id}/ficha` → 201 + `FichaRead`; 404 dueño inexistente; **409 si ya tiene ficha** (UNIQUE `ficha_duenio.duenio_id`, RN-03, caso C-03) (US-203)
  - `GET /duenios/{id}/mascotas` → mascotas del dueño (200/404) con `selectinload` para la colección
  - NO existen GET/PATCH dedicados de ficha: la ficha se lee embebida en el dueño (superficie de DD-08)
  - Tests: alta, PATCH parcial, 409 email duplicado, 409 segunda ficha, 409 borrado con mascotas, 422 id no entero
  - Cubre: **US-201, US-202, US-203** (Épica 2)
- **Dependencias**: `C-03`
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §Épica 2 (US-201..US-203)
  - `knowledge-base/05_reglas_de_negocio.md` §RN-01..RN-03 + §Política de integridad + §Contratos HTTP
  - `knowledge-base/07_flujos_principales.md` §Flujo 3, §Flujo 4, §Flujo 5, §Flujo 11
  - `knowledge-base/03_actores_y_roles.md` §Rutas públicas

---

### [C-06] `mascotas-practicas-crud`
- **Estado**: `[ ]` pendiente
- **Scope**: Módulos `mascotas` y `practicas` (agregación dueño→mascota + catálogo de prácticas)
  - `app/modules/mascotas/{models,schemas,service,router}.py`: `POST /mascotas/` con `MascotaCreate` que trae `duenio_id` existente (en la **agregación viaja un id**); dueño inexistente → FK violada → `IntegrityError` → 409 y no queda nada (caso C-04); 201 + `MascotaRead` (US-204 CA-1)
  - `GET /mascotas/` → envoltorio de la sección 2.9 `{ items, total, page, size, pages }`; `size` default 20, rango 1..100; página más allá de `pages` → 422 (cálculo del service, IN-01); la primera página siempre responde aunque no haya resultados (US-204 CA-2)
  - `GET /mascotas/{id}` → mascota **con su dueño** (`joinedload` a uno); 404 si no existe (US-204 CA-3); **sin PATCH ni DELETE de mascotas** (superficie DD-08)
  - `app/modules/practicas/{models,schemas,service,router}.py`: `POST /practicas/` → 201; nombre repetido → 409 (RN-02); precio ≤ 0 → 422 por DTO y respaldo CHECK de la base (RN-04) (US-205)
  - `GET /practicas/` → catálogo completo (lista simple por SU-06/QA-01, no requiere envoltorio)
  - Tests: FK dueño inexistente 409, paginación (rango de `size`, `page > pages`, primera página vacía), 409 nombre de práctica duplicado, 422 precio ≤ 0
  - Cubre: **US-204, US-205** (Épica 2)
- **Dependencias**: `C-05` *(entidad referenciada antes que la que referencia: los dueños deben existir antes de crear mascotas)*
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §Épica 2 (US-204, US-205)
  - `knowledge-base/04_modelo_de_datos.md` §mascota, §practica
  - `knowledge-base/05_reglas_de_negocio.md` §Contratos HTTP (RN-HTTP-04) + §RN-02, RN-04
  - `knowledge-base/07_flujos_principales.md` §Flujo 6, §Flujo 7

---

## FASE 3 — Altas con relaciones y lecturas sin N+1 (Épicas 4 y 5 · Ejercicios 4 y 5 — 15 % + 15 %)

### [C-07] `turnos-alta-borrado`
- **Estado**: `[ ]` pendiente
- **Scope**: Módulo `turnos` — el flujo central: alta con composición M:N con datos, todo-o-nada y precios congelados
  - `app/modules/turnos/{models,schemas,service,router}.py` (TurnoPractica vive acá): DTOs `TurnoCreate` con `practicas: [{practica_id}, ...]` anidadas — **ni precios ni total viajan en el DTO** (RN-06); `TurnoRead` con `mascota` embebida y prácticas con `precio_unitario` copiado
  - `POST /turnos/` en **una sola transacción** (RN-TX-01): trae precios del catálogo por cada `practica_id`, inserta `turno`, inserta cada `turno_practica` con `precio_unitario` copiado (freeze, RN-DS-02), calcula `total` el servidor
  - Códigos: lista vacía → 422 (RN-05); práctica inexistente → 409 con **rollback total** (no queda guardado nada, caso C-04); práctica repetida → violación de PK compuesta → 409 (RN-07); mascota inexistente → 409; contrato exacto del ejemplo (`total: "27000.00"`, fecha `10:30-03:00` → `13:30Z` — SU-03)
  - `DELETE /turnos/{id}` → 204; la **base** borra sus `turno_practica` por CASCADE (RN-09), el ORM no la toca (`passive_deletes` — ya declarada en C-03); 404 si no existe (Flujo 10)
  - Lectura embebida del alta: `TurnoRead` arma la respuesta con los datos ya en la sesión (sin recorrido perezoso — `MissingGreenlet`)
  - Tests: todo-o-nada (turno válido con 2 prácticas → 201 con total; una práctica inexistente → 409 y 0 filas), 409 duplicada, 422 lista vacía, 204 con prácticas borradas
  - Cubre: **US-401** (Épica 4)
- **Dependencias**: `C-05, C-06` *(mascota y práctica deben existir; el turno referencia a ambas)*
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §Épica 4 (US-401)
  - `knowledge-base/07_flujos_principales.md` §Flujo 8 (contrato exacto), §Flujo 10
  - `knowledge-base/05_reglas_de_negocio.md` §RN-05..RN-07, §RN-DS-02 + §Transaccionalidad (RN-TX-01)
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-06, §SU-03

---

### [C-08] `lecturas-sin-n1`
- **Estado**: `[ ]` pendiente
- **Scope**: Precarga transversal (Épica 5): toda lectura con relaciones resuelve con carga anticipada declarada
  - Auditoría/ajuste de TODAS las lecturas con relaciones: `joinedload` para «a uno» (mascota→dueño, turno→mascota, dueño→ficha), `selectinload` para colecciones (dueño→mascotas, turno→turno_practica+practicas) (US-501 CA-1)
  - `GET /turnos/{id}` → turno con mascota y prácticas: exactamente 2 consultas fijas (1 joinedload + 1 selectinload), que NO crecen con la cantidad de prácticas (US-501 CA-2, caso C-07)
  - Verificación del detalle de dueño con ficha: misma garantía de consultas fijas (US-501 CA-3)
  - Cero carga perezosa en ningún handler (`MissingGreenlet`); evidencia con `echo=True` en la consola (US-501 CA-4, se captura en C-10)
  - Ninguna lectura depende del lazy loading; respuestas ensambladas solo con datos precargados
  - Tests: mismo número de consultas con 1 y con 3 prácticas (evidencia consola), ninguna query de lazy-load en los detalles
  - Cubre: **US-501** (Épica 5)
- **Dependencias**: `C-05, C-06, C-07` *(auditúa las lecturas que esos changes crearon)*
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §Épica 5 (US-501)
  - `knowledge-base/07_flujos_principales.md` §Flujo 9 (estrategia de precarga por forma de relación)
  - `knowledge-base/05_reglas_de_negocio.md` §Navegación de relaciones (RN-REL-03)
  - `knowledge-base/08_arquitectura_propuesta.md` §Persistencia y esquema + §Riesgos de infra (MissingGreenlet)

---

## FASE 4 — Asincronía sin bloqueos (Épica 6 · Ejercicio 6 — 10 %)

### [C-09] `laboratorio-offload`
- **Estado**: `[ ]` pendiente
- **Scope**: Módulo `laboratorio` — biblioteca sincrónica llamada fuera del bucle de eventos
  - `app/modules/laboratorio/cliente.py` con `consultar_stock(vacuna)` sincrónica (`time.sleep(1)`) tal como la entrega la cátedra — **usarla sin modificarla** (US-601 CA-1; si la cátedra no la entrega, reimplementarla con el código exacto del PDF — SU-05); módulo sin `models.py` (no hay persistencia — IN-02), schemas inline
  - `app/modules/laboratorio/{service,router}.py`: `GET /laboratorio/stock/{vacuna}` → `{"vacuna": ..., "stock": ...}` 200, ejecutando la función bloqueante **fuera del event loop** (offload a hilo — mecanismo exacto a fijar en el propose: `anyio.to_thread.run_sync` o `ThreadPoolExecutor`, QA-03/DD-07)
  - Todos los handlers `async def`; ninguna llamada bloqueante en el bucle (US-601 CA-4, RN-AS-01)
  - Con N consultas al laboratorio en marcha, `GET /health/live` sigue respondiendo de inmediato (US-601 CA-3, caso C-09 — la evidencia se captura en C-10)
  - Tests: 3 llamadas simultáneas al laboratorio + `GET /health/live` concurrente → el health responde sin esperar los sleep
  - Cubre: **US-601** (Épica 6)
- **Dependencias**: `C-02` *(el caso C-09 demuestra su valor contra `/health/live`, creado en C-02 — puede proponerse en paralelo con C-03 en GATE 2)*
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §Épica 6 (US-601)
  - `knowledge-base/07_flujos_principales.md` §Flujo 12, §Flujo 13
  - `knowledge-base/05_reglas_de_negocio.md` §Asincronía (RN-AS-01, RN-AS-02)
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-07 + `knowledge-base/10_preguntas_abiertas.md` §QA-03, §IN-02

---

## FASE 5 — Casos de prueba mínimos y entrega (Épicas 7 y 8)

### [C-10] `test-cases`
- **Estado**: `[ ]` pendiente
- **Scope**: Carpeta `test/` con los 9 casos mínimos demostrando RN-01..RN-09, integridad y asincronía
  - `test/*.http` (uno por caso o concatenados — QA-04), cada uno con comentario de la respuesta esperada, corribles después de `python reiniciar.py` (US-701)
  - C-01: `/duenios/abc` → 422 sin ejecutar el handler · C-02: email o nombre de práctica repetido → 409 con mensaje propio · C-03: segunda ficha → 409 · C-04: mascota con dueño inexistente y turno con práctica inexistente → 409 sin quedarse nada guardado · C-05: borrar dueño con mascotas → 409; borrar turno → 204 y sus prácticas ya no están · C-06: turno válido con 2 prácticas → 201 con precios copiados y total calculado · C-07: detalle de turno con 1 y con 3 prácticas → misma cantidad de consultas (`echo=True`) · C-09: 3 consultas simultáneas al laboratorio + `GET /health/live` de inmediato
  - `test/*.sql`: caso **C-08** — `UPDATE practica SET precio = 0` ejecutado directo en la base → rechazado por el CHECK (archivo `.sql` aparte, no `.http`)
  - Capturar la **evidencia del caso C-07** (fragmento de consola con las consultas) para la entrega (US-801 CA-4)
  - Tests: los 9 casos de la consigna corren en orden sobre el seed de C-04, todos verdes
  - Cubre: **US-701** (Épica 7)
- **Dependencias**: `C-04, C-08, C-09` *(y por transitividad C-05, C-06, C-07)*
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §Épica 7 (tabla de casos C-01..C-09)
  - `knowledge-base/05_reglas_de_negocio.md` (completo: cada caso demuestra un grupo de RN)
  - `knowledge-base/07_flujos_principales.md` §Flujo 14
  - `knowledge-base/10_preguntas_abiertas.md` §QA-04

---

### [C-11] `delivery-readme`
- **Estado**: `[ ]` pendiente
- **Scope**: Formato de entrega obligatorio — sin esto el TP **no se corrige**
  - Repositorio completo con código fuente, `requirements.txt`, `env.example`, `reiniciar.py` y carpeta `test/`; `.env` **no versionado** y **cero credenciales reales** en el repo (US-801 CA-1)
  - `README.md` con los pasos desde cero: entorno virtual → dependencias → `.env` → `python reiniciar.py` → arranque del servidor con `uvicorn` (US-801 CA-2)
  - `README.md` con la **explicación de 1-2 líneas del índice de `turno_practica.turno_id`**: la PK compuesta `(turno_id, practica_id)` ya sirve como índice por su primera columna (US-301 CA-2 + US-801 CA-3)
  - **Evidencia del caso C-07** integrada al README o a la entrega: fragmento de consola del detalle del turno con una práctica y con tres (US-801 CA-4)
  - Chequeo final: el proyecto levanta y `python reiniciar.py` crea el esquema sobre una base **vacía** (condición de corrección, US-801 CA-5)
  - Cubre: **US-801** (Épica 8)
- **Dependencias**: `C-10` *(la evidencia C-07 nace al correr los casos)*
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/08_arquitectura_propuesta.md` §Entrega (formato obligatorio)
  - `knowledge-base/06_funcionalidades.md` §Épica 8 (US-801)
  - `knowledge-base/04_modelo_de_datos.md` §turno_practica (explicación del índice)
  - `knowledge-base/10_preguntas_abiertas.md` §QA-06 (formato de fecha en los ejemplos del README)

---

## Tabla resumen

| ID | Change | Fase | Épica/US de la consigna | Deps | Governance |
|---|---|---|---|---|---|
| C-01 | `foundation-setup` | 0 | Épica 1 · US-103 | ninguna | BAJO |
| C-02 | `database-lifespan-health` | 0 | Épica 1 · US-101, US-102 | C-01 | MEDIO |
| C-03 | `domain-models` | 1 | Épica 3 · US-301 | C-02 | CRITICO |
| C-04 | `reiniciar-seed` | 1 | Épica 3 · US-302 | C-03 | BAJO |
| C-05 | `duenios-crud-ficha` | 2 | Épica 2 · US-201, US-202, US-203 | C-03 | MEDIO |
| C-06 | `mascotas-practicas-crud` | 2 | Épica 2 · US-204, US-205 | C-05 | MEDIO |
| C-07 | `turnos-alta-borrado` | 3 | Épica 4 · US-401 | C-05, C-06 | ALTO |
| C-08 | `lecturas-sin-n1` | 3 | Épica 5 · US-501 | C-05, C-06, C-07 | MEDIO |
| C-09 | `laboratorio-offload` | 4 | Épica 6 · US-601 | C-02 | ALTO |
| C-10 | `test-cases` | 5 | Épica 7 · US-701 | C-04, C-08, C-09 | MEDIO |
| C-11 | `delivery-readme` | 5 | Épica 8 · US-801 | C-10 | BAJO |

**Cobertura total**: 8 épicas · 14 user stories · 9 casos de prueba (C-01..C-09) · condición de corrección (reiniciar sobre base vacía + README + evidencia) — sin Ninguna US suelta.

**Primer change recomendado**: `/opsx:propose C-01-foundation-setup`
