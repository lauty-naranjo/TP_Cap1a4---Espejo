# Arquitectura Propuesta

> Fuente: `docs/MiniTP_Cap1a4_Consigna.pdf` (Estructura del proyecto, Ejercicio 1, Formato de entrega). La estructura es **dictada** por la consigna; los detalles no especificados se marcan.

## Patrones aplicados

| Patrón | Dónde se usa | Por qué (consigna) |
|---|---|---|
| Organización por módulo funcional | `app/modules/<módulo>/{models,schemas,service,router}.py` | La misma estructura en todos los módulos (min: health, duenios, mascotas, practicas, turnos, laboratorio) |
| Router → Service → Models/Schemas | Handler delega; la **lógica vive en el service**, que recibe la sesión como parámetro | Sin repositorios ni Unit of Work (fuera de alcance) |
| Inyección de dependencias | `Depends(get_session)` — una sesión por petición | Requisito de capítulo 1; `expire_on_commit=False` (sección 4.5) |
| Ciclo de vida controlado (lifespan) | Motor + fábrica de sesiones en `app.state` | Motor se cierra al apagar (sección 1.9) |
| Integridad delegada en la base | UNIQUE, CHECK, FK RESTRICT/CASCADE + índices | Se escribe y se atrapa `IntegrityError` → 409 (nunca "¿ya existe?") |
| DTO separados de modelos de tabla | `schemas.py` vs `models.py` | Secciones 2.5/2.6 — DTOs Create/Update/Read |
| Freeze de precio en la transacción (snapshot en la relación) | `turno_practica.precio_unitario` | Cambiar el catálogo no altera turnos ya reservados |
| Borrado decidido por la base | `passive_deletes` + ON DELETE CASCADE (`turno`→`turno_practica`), RESTRICT (`mascota.duenio_id`) | La base garantiza, no el ORM |

## Estructura de directorios (consigna)

```
proyecto/
├── app/
│   ├── main.py                     # Aplicación, lifespan y registro de routers
│   ├── core/
│   │   ├── config.py               # Lectura de DATABASE_URL desde el entorno
│   │   └── database.py             # Motor, fábrica de sesiones y dependencia get_session
│   └── modules/
│       ├── health/                 # /health/live, /health/ready
│       │   └── router.py
│       ├── duenios/                # FichaDuenio vive acá
│       │   ├── models.py           # Duenio + FichaDuenio
│       │   ├── schemas.py          # DuenioCreate/DuenioUpdate/FichaCreate/DuenioRead/FichaRead
│       │   ├── service.py          # Lógica, IntegrityError → 409, precarga dueño↔ficha
│       │   └── router.py
│       ├── mascotas/
│       │   ├── models.py, schemas.py, service.py, router.py
│       ├── practicas/
│       │   ├── models.py, schemas.py, service.py, router.py
│       ├── turnos/                 # TurnoPractica vive acá
│       │   ├── models.py           # Turno + TurnoPractica (passive_deletes)
│       │   ├── schemas.py          # TurnoCreate (con practicas anidadas) / TurnoRead
│       │   ├── service.py          # Transacción todo-o-nada, precios copiados, total servidor
│       │   └── router.py
│       └── laboratorio/
│           ├── cliente.py          # ⚠ entrega la cátedra (consultar_stock, sync, time.sleep(1)) — NO modificar
│           ├── service.py          # Descarga la llamada fuera del event loop
│           └── router.py
├── reiniciar.py                    # Borra tablas, create_all, seed inicial
├── test/
│   ├── *.http                      # Casos C-01..C-07, C-09 con respuesta esperada en comentario
│   └── *.sql                       # Caso C-08 (UPDATE practica SET precio = 0)
├── requirements.txt
├── env.example                     # Forma de DATABASE_URL, sin secretos
├── README.md                       # Pasos desde cero + explicación del índice de turno_practica.turno_id
└── .env                            # NO versionado
```

**Módulos mínimos**: `health`, `duenios`, `mascotas`, `practicas`, `turnos` y `laboratorio`.
**Ubicaciones obligatorias**: `FichaDuenio` en `duenios`; `TurnoPractica` en `turnos`.

Requisitos técnicos: `app/main.py` (lifespan), `app.core` (config/database) y, en cada módulo, los cuatro archivos con su rol. Ver `07_flujos_principales.md` para el comportamiento de cada uno.

## Seguridad

- **Autenticación**: no aplica en esta versión (fuera de alcance por consigna). Todos los endpoints son públicos dentro del servicio.
- **Autorización**: no aplica; sin RBAC.
- **Validación de input**: contratos Pydantic/SQLModel (422) para cuerpos y parámetros; integridad y unicidad delegadas a PostgreSQL con `IntegrityError` → 409.
- **Secrets management**: la conexión a la base vive en `DATABASE_URL` dentro de `.env`, **no versionada**. `env.example` muestra la forma del valor **sin ningún secreto**. Condición de corrección: **no pueden existir credenciales reales en el repositorio**.

## Variables de entorno

| Variable | Descripción | Ejemplo | Sensible |
|---|---|---|---|
| `DATABASE_URL` | URL de conexión asincrónica a PostgreSQL 16 usada por asyncpg | `postgresql+asyncpg://usuario:password@localhost:5432/veterinaria` | Sí (en `.env` real; el `env.example` lleva placeholder) |

Única variable exigida por la consigna. (Si en implementación se agregan otras — p. ej. tamaño de pool — documentarlas acá; no son parte del TP.)

## Persistencia y esquema

- El esquema (tablas/columnas/interfaces consultables) es el de `04_modelo_de_datos.md`: 6 tablas obligatorias con nombres exactos.
- El esquema se crea **a partir de los modelos** con `SQLModel.metadata.create_all` — **sin Alembic** (fuera de alcance). `reiniciar.py` borra y recrea todo + seed.
- Lecturas: nunca carga perezosa (asincronía): únicamente `joinedload`/`selectinload` explícitos en la consulta.

## Entrega (formato obligatorio)

- Repositorio con código fuente completo, `requirements.txt`, `env.example`, `reiniciar.py`, carpeta `test/`.
- `README.md`: pasos desde cero (entorno virtual → dependencias → `.env` → `python reiniciar.py` → arranque con uvicorn) **y** explicación del índice de `turno_practica.turno_id` (1–2 líneas).
- Evidencia C-07: fragmento de la consola con consultas del detalle de un turno con una práctica y con tres.
- El archivo `.env` no se sube.

## Riesgos de infra

- PostgreSQL 16 + asyncpg 0.30: versiones mínimas con numeración asincrónica — pin en `requirements.txt` con `>=`.
- `MissingGreenlet`: cualquier acceso perezoso en un handler async rompe; evitarlo por diseño (carga anticipada), no por arreglo puntual.
