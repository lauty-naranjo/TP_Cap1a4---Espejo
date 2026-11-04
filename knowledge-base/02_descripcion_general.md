# Descripción General

> Fuente: `docs/MiniTP_Cap1a4_Consigna.pdf`, secciones "Requisitos técnicos", "Estructura del proyecto" y "Endpoints de referencia".

## Stack tecnológico

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

## Arquitectura general

API REST de un solo proceso (monolito pequeño), organizada **por módulo funcional**. Sin frontend: los consumidores usan HTTP directamente y los casos de prueba son archivos `.http`.

```
Cliente (.http / HTTP) → uvicorn → FastAPI app (main.py, lifespan: motor + sesión)
                                      │
                                      ├── routers HTTP (app/modules/<módulo>/router.py)
                                      │       └── delega en →
                                      ├── service (app/modules/<módulo>/service.py)  ← lógica, errores, precarga
                                      │       └── usa →
                                      ├── models (app/modules/<módulo>/models.py)    ← tablas, restricciones, relaciones
                                      ├── schemas (app/modules/<módulo>/schemas.py)  ← DTOs Create/Update/Read
                                      └── core (config.py, database.py) → PostgreSQL 16 (asyncpg)
```

Decisiones de alto nivel dadas por la consigna:
- El esquema se crea con `SQLModel.metadata.create_all` (sin Alembic), vía `reiniciar.py`.
- La lógica vive en el `service` de cada módulo, que recibe la sesión como parámetro (sin capa de repositorio ni UoW).
- El service **atrapa `IntegrityError`** de la base, deshace la transacción y responde 409 con mensaje propio — nunca valida con consultas previas tipo "¿ya existe?".
- El borrado del turno lo decide la base con `ON DELETE CASCADE`, no el ORM (`passive_deletes`).

## Integraciones externas

| Servicio | Propósito | Tipo |
|---|---|---|
| Biblioteca del laboratorio (`app/modules/laboratorio/cliente.py`, entregada por la cátedra) | Consultar stock de vacunas; función sincrónica `consultar_stock(vacuna)` que duerme 1 s con `time.sleep` | Llamada directa a función Python |
| PostgreSQL 16 | Persistencia del dominio | Driver asyncpg |

Nota clave: `consultar_stock` **no tiene variante asincrónica y no se modifica**. El endpoint `GET /laboratorio/stock/{vacuna}` debe llamarla **fuera del bucle de eventos** (ejecutarla en un hilo separado, p. ej. `run_in_executor`) para que el servidor siga atendiendo (`/health/live` responde de inmediato aunque haya varias consultas al laboratorio en marcha — caso C-09).

## API REST (endpoints de referencia de la consigna)

| Método | Ruta | Cuerpo | Respuesta | Códigos |
|---|---|---|---|---|
| GET | `/health/live` | — | `{"estado": "vivo"}` | 200 |
| GET | `/health/ready` | — | Estado de la base | 200, 503 |
| POST | `/duenios/` | DuenioCreate | DuenioRead | 201, 409, 422 |
| GET | `/duenios/{id}` | — | Dueño con su ficha | 200, 404, 422 |
| PATCH | `/duenios/{id}` | DuenioUpdate | Dueño con su ficha | 200, 404, 409, 422 |
| DELETE | `/duenios/{id}` | — | Sin cuerpo | 204, 404, 409 |
| POST | `/duenios/{id}/ficha` | FichaCreate | FichaRead | 201, 404, 409 |
| GET | `/duenios/{id}/mascotas` | — | Mascotas del dueño | 200, 404 |
| POST | `/mascotas/` | MascotaCreate | MascotaRead | 201, 409, 422 |
| GET | `/mascotas/` | `page`, `size` | Envoltorio con mascotas | 200, 422 |
| GET | `/mascotas/{id}` | — | Mascota con su dueño | 200, 404 |
| POST | `/practicas/` | PracticaCreate | PracticaRead | 201, 409, 422 |
| GET | `/practicas/` | — | Catálogo de prácticas | 200 |
| POST | `/turnos/` | TurnoCreate (con `practicas`) | Turno con mascota y prácticas | 201, 409, 422 |
| GET | `/turnos/{id}` | — | Turno con mascota y prácticas | 200, 404 |
| DELETE | `/turnos/{id}` | — | Sin cuerpo | 204, 404 |
| GET | `/laboratorio/stock/{vacuna}` | — | `{"vacuna": ..., "stock": ...}` | 200 |

Códigos generales (sección 2.8): **201** al crear, **204** al borrar, **404** si no existe, **409** si la base rechaza la escritura, **422** si cuerpo/parámetros no cumplen el contrato.

Paginación (`GET /mascotas/`): envoltorio `{ items, total, page, size, pages }`; `size` vale 20 por defecto y va de **1 a 100**; una página más allá de `pages` responde **422**; la primera página siempre responde aunque no haya resultados.
