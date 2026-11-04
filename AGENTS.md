# API Veterinaria — TP Programación III (Cap. 1 a 4) — Instrucciones para Agentes

> Este archivo (y su copia `CLAUDE.md`) es lo PRIMERO que todo agente lee al entrar al repo.
> Generado a partir de `knowledge-base/` y `CHANGES.md`. No editar a mano sin re-sincronizar ambos archivos.

---

## Stack Tecnológico

<!-- Copiar la tabla de knowledge-base/02_descripcion_general.md §Stack tecnológico -->

**Dictado por la consigna** (no es una decisión libre — ver `09_decisiones_y_supuestos.md`, DD-01):

| Capa | Tecnología | Versión mínima | Uso |
|---|---|---|---|
| Lenguaje | Python | 3.12 | — |
| Framework web | FastAPI | 0.111 | Todos los handlers con `async def` |
| ORM | SQLModel | 0.0.24 | Modelos de tabla y contratos |
| Motor ORM | SQLAlchemy 2.0 (asincrónico) | 2.0 | Motor, sesión y carga anticipada |
| Driver DB | asyncpg | 0.30 | Controlador asincrónico de PostgreSQL |
| Base de datos | PostgreSQL | 16 | Persistencia |
| Configuración | python-dotenv | 1.0 | Lectura del archivo `.env` |
| Servidor ASGI | uvicorn | el que instala `fastapi[standard]` | — |

Configuración: la dirección de la base se lee de la variable de entorno `DATABASE_URL`, definida en un `.env` que **no se versiona**; el repositorio incluye `env.example` con la forma del valor y sin secretos.

Detalle completo: [knowledge-base/02_descripcion_general.md](knowledge-base/02_descripcion_general.md)

---

## Base de Conocimiento

La fuente de verdad del dominio vive en `knowledge-base/`. **Leé el archivo relevante ANTES de implementar.**

| Archivo | Cuándo leerlo |
|---------|---------------|
| [01_vision_y_objetivos.md](knowledge-base/01_vision_y_objetivos.md) | Entender propósito, alcance, rúbrica de la cátedra y formato de entrega |
| [02_descripcion_general.md](knowledge-base/02_descripcion_general.md) | Stack dictado, arquitectura, integraciones (laboratorio) y endpoints de referencia |
| [03_actores_y_roles.md](knowledge-base/03_actores_y_roles.md) | Actores del dominio, rutas públicas (sin auth/RBAC) |
| [04_modelo_de_datos.md](knowledge-base/04_modelo_de_datos.md) | Entidades, columnas/restricciones obligatorias, ERD, seed de `reiniciar.py` |
| [05_reglas_de_negocio.md](knowledge-base/05_reglas_de_negocio.md) | Reglas codificadas (RN-XX) — la fuente de las reglas duras de abajo |
| [06_funcionalidades.md](knowledge-base/06_funcionalidades.md) | Historias de usuario por épica + casos de prueba C-01..C-09 |
| [07_flujos_principales.md](knowledge-base/07_flujos_principales.md) | 14 flujos E2E (lifespan, sesiones, transacción de turnos, offload) |
| [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md) | Patrones, estructura de directorios obligatoria, env vars, entrega |
| [09_decisiones_y_supuestos.md](knowledge-base/09_decisiones_y_supuestos.md) | Decisiones dictadas (DD-XX) y supuestos inferidos (SU-XX) |
| [10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md) | ⚠️ Inconsistencias (IN-01..02) y preguntas QA-01..QA-06 a resolver ANTES de codear |

> ⚠️ Estado de `10_preguntas_abiertas.md`: **no hay inconsistencias de prioridad Alta pendientes**. Los ítems activos son QA-01..QA-03 (prioridad **Media** — resuélvelos según la resolución propuesta en cada change; QA-04..QA-06 son Baja). Leer antes del primer change.

---

## Skills Disponibles

<!-- Fuente de verdad: .atl/skill-registry.md (generado por skill-registry). Adaptar filas a las skills que lista el registry. -->

| Agente | Rol | Skills que carga |
|--------|-----|------------------|
| **Backend Core** | FastAPI / SQLModel / PostgreSQL / async | `fastapi-templates`, `postgresql-table-design`, `supabase-postgres-best-practices`, `async-python-patterns`, `security-and-hardening` |
| **Backend Aux / Testing** | Tests, TDD, casos `.http` de la consigna | `python-testing-patterns`, `tdd`, `test-driven-development` |
| **Orquestación / Fundación** | SDD / KB / roadmap / registro de skills | `active-orchestrator`, `kb-creator`, `discovery-research`, `roadmap-generator`, `agents-md-generator`, `skill-registry`, `skill-creator`, `find-skill`, `web-scraper` |
| **OPSX (OpenSpec)** | Workflow de changes con `/opsx:*` | `openspec-propose`, `openspec-apply-change`, `openspec-verify-change`, `openspec-archive-change`, `openspec-sync-specs`, `openspec-update-change`, `openspec-explore` |

**No hay fila de Frontend**: el proyecto es backend-only (`visual_design.mode: deferred`). Las skills de diseño (`design-system`, `emil-design-eng`, `design-taste-frontend-v1`) quedan anotadas en el registry y se invocan solo si emerge un cambio visual real.

Cargá la skill correspondiente al contexto ANTES de escribir código.

> Los compact rules de cada skill los resuelve el orquestador desde `.atl/skill-registry.md` (generado por `skill-registry`; no versionado — no está en el repo). Esta tabla solo mapea skill→rol.

---

## Roadmap de Changes

<!-- Resumen de CHANGES.md — NO duplicar el detalle completo -->

El plan de implementación completo está en [CHANGES.md](CHANGES.md). Resumen:

- **Total**: 11 changes en 6 fases (C-01..C-11), cubriendo las 8 épicas de la consigna con 14 user stories y 9 casos de prueba. Proyecto API REST **sin UI** — no hay changes de frontend ni de design-system.
- **Camino crítico** (9 changes): `C-01 → C-02 → C-03 → C-05 → C-06 → C-07 → C-08 → C-10 → C-11` (C-04 y C-09 cuelgan temprano y se reencuentran en C-10).
- **Paralelismo**: GATE 0 (C-01) → C-02, luego FORK C-03 ∥ C-09 y C-04 ∥ C-05; sincronización final en GATE 7 para C-10 y la entrega C-11.
- **Primer change**: `C-01` (`foundation-setup`).
- **Regla de oro**: el TP debe completarse en su totalidad — sin C-04 y C-11 el TP **no se corrige** (condición de la cátedra).

**Antes de cualquier `/opsx:propose`**: leé [CHANGES.md](CHANGES.md), identificá las dependencias del change y los archivos de "Leer antes".

---

## Reglas Duras (específicas del proyecto)

> Reglas globales ya definidas en las instrucciones globales instaladas de OpenCode (`C:\Users\ramir\.config\opencode\AGENTS.md` — orquestador fino, governance, engram, TDD estricto, política de stage design-mockups): el proyecto las **hereda**, no se repiten acá. Acá viven solo las reglas **específicas de este proyecto** + las universales que el global no cubra.

Acá van: (a) las reglas específicas de este proyecto, derivadas de su stack real (Python 3.12 + FastAPI + SQLModel/SQLAlchemy async + asyncpg + PostgreSQL 16) y **confirmadas con el usuario**; y (b) cualquier regla universal que el global no cubra todavía. Son contrato; romperlas es un defecto. Formato `NUNCA X → hacer Y`:

- NUNCA validar unicidad/existencia con consultas previas → escribir y atrapar `IntegrityError`, rollback, responder 409 con mensaje propio. [05 §RN-INT-01 + RN-01/02/03/07/08; 02 §Arquitectura]
- NUNCA handler `def` ni código bloqueante en el event loop → todos los endpoints `async def`; `consultar_stock` de la cátedra sin modificar, offload a hilo. [05 §RN-AS-01/02; 02 §Integraciones]
- NUNCA decidir borrados desde el ORM → declarar en la base (`ON DELETE CASCADE` en `turno_practica.turno_id`, `RESTRICT` en `mascota.duenio_id`) y `passive_deletes=True` en `Turno.practicas`. [05 §RN-INT-02, RN-08, RN-09; 02]
- NUNCA representar dinero con `float` → `Decimal`; `NUMERIC(10,2)` precios, `NUMERIC(12,2)` total. [05 §RN-DS-01]
- NUNCA aceptar `precio`/`total` del cliente en el alta de turno → copiar precio del catálogo a `turno_practica.precio_unitario` (freeze), calcular total en el servidor, UNA transacción todo-o-nada. [05 §RN-05/06, RN-TX-01, RN-DS-02; 02]
- NUNCA depender de lazy loading en lecturas async → `joinedload` (a uno) / `selectinload` (colecciones) en la misma consulta; `back_populates` en ambos extremos; `Duenio.ficha` objeto, no lista. [05 §RN-REL-01..03; 08 §Persistencia]
- NUNCA salirse del contrato HTTP: 201 crear, 204 borrar, 404 no existe, 409 la base rechaza, 422 contrato violado; PATCH con `exclude_unset`; paginación solo en `GET /mascotas/` con envoltorio `{items,total,page,size,pages}`, size 20 (1..100), `page > pages` → 422, primera página siempre responde. [05 §RN-HTTP-01..04; 02]
- NUNCA agregar Alembic, repositorios/UoW, ni auth/RBAC → `SQLModel.metadata.create_all` vía `reiniciar.py`, lógica en service que recibe la sesión como parámetro, endpoints públicos. [02 §Arquitectura + DD-03/04; 08 §Patrones, §Seguridad]
- NUNCA crear el `async_sessionmaker` sin `expire_on_commit=False`, ni leer config fuera de `DATABASE_URL`; `.env` no versionado, `env.example` sin secretos, cero credenciales reales en el repo. [08 §Patrones DI, §Variables de entorno, §Seguridad]
- NUNCA mover/renombrar las piezas obligatorias de la consigna → `app/modules/<módulo>/{router,service,models,schemas}`; `FichaDuenio` en `duenios`; `TurnoPractica` en `turnos`; nombres de tablas/columnas intactos (agregar sí, renombrar/quitar no); `GET /health/live` sin tocar la base, `GET /health/ready` con `SELECT 1` → 503 si falla. [08 §Estructura + Ubicaciones; 05 §Excepciones globales, §RN-HL-01/02]
- NUNCA considerar funcional un módulo cuyos casos `test/*.http` no corran después de `python reiniciar.py` sobre una base vacía (condición de corrección de la cátedra). [02; 06 §Epica 7 US-701; CHANGES C-10/C-11]

### Universales ausentes (el global no las cubre todavía)

- NUNCA commitear/push sin pedido explícito del usuario.
- SIEMPRE Conventional Commits (`feat|fix|chore|docs|refactor|test: ...`) en los mensajes de commit.
- SIEMPRE omitir co-autoría/attribution en commits.

---

## Flujo de Trabajo

```
1. Leer la KB relevante (knowledge-base/)        → entender el dominio
2. Identificar el change en CHANGES.md           → respetar dependencias
3. /opsx:propose C-NN-nombre                     → proposal + design + specs + tasks
4. Implementar las tasks (apply, cargando skills) → respetando las reglas duras
5. /opsx:verify + /opsx:archive C-NN-nombre + marcar [x] → cerrar el change
```

Aplicar TODAS las reglas duras en cada paso. Ante conflicto entre la KB y este archivo, las reglas duras prevalecen.
