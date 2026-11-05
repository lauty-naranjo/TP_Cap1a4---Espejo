# API Veterinaria — TP Programación III (Capítulos 1 a 4)

## Descripción

API REST para gestionar dueños, mascotas, prácticas y turnos de una veterinaria. Cubre los ejercicios
1 a 8 de la consigna: ciclo de vida asincrónico, CRUD con integridad delegada en PostgreSQL, altas con
relaciones, lecturas sin N+1 y offload de llamadas bloqueantes. Es una API sin UI: se prueba con HTTP
(`test/`) o con la documentación interactiva de FastAPI.

## Stack

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.12 (probado también con 3.14) |
| Framework web | FastAPI (`async def` en todos los handlers) |
| ORM | SQLModel |
| Motor ORM | SQLAlchemy 2.0 asincrónico |
| Driver | asyncpg |
| Base de datos | PostgreSQL 16 |

## Requisitos previos

- **Python 3.12 o superior** con `pip`.
- **PostgreSQL 16** en ejecución en `localhost:5432`.
- Una base **vacía** llamada `veterinaria` (el esquema lo crea `python reiniciar.py`):

```bash
createdb -U usuario veterinaria
```

> `usuario` es un placeholder: usá el usuario real de tu instalación de PostgreSQL. Si preferís `psql`:
> `psql -U usuario -c "CREATE DATABASE veterinaria;"`.

## Puesta en marcha desde cero

Todos los comandos se ejecutan desde la raíz del repositorio, **en este orden**.

### 1. Crear y activar el entorno virtual

```bash
python -m venv .venv
```

**PowerShell (Windows):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**bash (Linux/macOS/Git Bash):**

```bash
source .venv/bin/activate
```

> Si PowerShell bloquea la ejecución de scripts, habilitá el proceso actual con
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y volvé a activar.

### 2. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 3. Crear el archivo `.env`

Copiá la plantilla y completá `DATABASE_URL` con tus datos locales.

**PowerShell:**

```powershell
Copy-Item env.example .env
```

**bash:**

```bash
cp env.example .env
```

Editá `.env` y reemplazá `usuario:password` por tus credenciales reales. El archivo `.env` **no se
versiona** (está en `.gitignore`); `env.example` sólo contiene la forma del valor.

### 4. Crear el esquema y cargar el seed

```bash
python reiniciar.py
```

Deja la base en un estado conocido: 6 tablas y los datos de ejemplo (2 dueños, 3 mascotas, 4 prácticas
y 1 turno con 2 prácticas).

### 5. Arrancar el servidor

```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000` (documentación interactiva en
`http://localhost:8000/docs`). Verificá el arranque con:

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

## Configuración de `.env`

La única variable que el proyecto necesita en `.env` es `DATABASE_URL`:

| Variable | Descripción | Forma |
|---|---|---|
| `DATABASE_URL` | URL asincrónica de PostgreSQL usada por asyncpg | `postgresql+asyncpg://usuario:password@localhost:5432/veterinaria` |

- `usuario` y `password` son **placeholders**: poné los de tu instalación.
- El archivo `.env` **no se versiona** y no debe subirse al repositorio; `env.example` es la plantilla
  versionada y no lleva credenciales reales.
- Sin `DATABASE_URL`, la aplicación aborta al arrancar con un error que indica copiar `env.example` a
  `.env` (fail-fast).

Para ver el SQL generado (evidencia del caso C-07) se puede exportar `SQL_ECHO` en la sesión; no es una
variable obligatoria del proyecto:

```powershell
# PowerShell
$env:SQL_ECHO="true"; uvicorn app.main:app --reload
```

```bash
# bash
SQL_ECHO=true uvicorn app.main:app --reload
```

## Modelo de datos

El esquema tiene **6 tablas**:

| Tabla | Rol |
|---|---|
| `duenio` | Cliente de la veterinaria (nombre y email único). |
| `ficha_duenio` | Ficha 1:1 del dueño (teléfono y dirección). |
| `mascota` | Paciente, asociado a un dueño (FK `duenio_id` con `ON DELETE RESTRICT`). |
| `practica` | Catálogo de prácticas con precio (consulta, vacuna, etc.). |
| `turno` | Turno de atención: mascota, fecha con zona horaria, motivo y total. |
| `turno_practica` | Prácticas del turno con el precio congelado (`precio_unitario`); PK compuesta. |

### ¿Por qué `turno_practica.turno_id` no tiene índice propio?

La PK compuesta `turno_practica_pkey (turno_id, practica_id)` ya es un índice B-tree cuya **primera columna**
es `turno_id`, así que cubre las búsquedas por turno y **no hace falta un índice propio** en `turno_id`.
`practica_id` sí lleva índice propio (`ix_turno_practica_practica_id`) porque queda en segunda posición
dentro de la PK.

Comprobación opcional en `psql`:

```sql
\d turno_practica
```

## Evidencia del caso C-07

El detalle de un turno siempre emite **2 consultas fijas**: una para el turno con su mascota
(`joinedload`) y otra para las prácticas con su catálogo (`selectinload`). El número **no crece** con la
cantidad de prácticas:

```text
C-07 · DETALLE CON 1 PRÁCTICA (turno id=2)
SELECT turno.id, turno.mascota_id, turno.fecha, turno.motivo, turno.total, ...
FROM turno LEFT OUTER JOIN mascota AS mascota_1 ON mascota_1.id = turno.mascota_id
WHERE turno.id = $1::INTEGER

SELECT turno_practica.turno_id, turno_practica.practica_id, turno_practica.precio_unitario, ...
FROM turno_practica LEFT OUTER JOIN practica AS practica_1 ON practica_1.id = turno_practica.practica_id
WHERE turno_practica.turno_id IN ($1::INTEGER)
-> 2 consultas

C-07 · DETALLE CON 3 PRÁCTICAS (turno id=3)
SELECT turno.id, turno.mascota_id, turno.fecha, turno.motivo, turno.total, ...
FROM turno LEFT OUTER JOIN mascota AS mascota_1 ON mascota_1.id = turno.mascota_id
WHERE turno.id = $1::INTEGER

SELECT turno_practica.turno_id, turno_practica.practica_id, turno_practica.precio_unitario, ...
FROM turno_practica LEFT OUTER JOIN practica AS practica_1 ON practica_1.id = turno_practica.practica_id
WHERE turno_practica.turno_id IN ($1::INTEGER)
-> las MISMAS 2 consultas

CONCLUSIÓN
  Con 1 práctica: 2 consultas. Con 3 prácticas: las MISMAS 2 consultas.
  El número no crece con la cantidad de prácticas -> no hay N+1.
```

La captura completa de la consola (`echo=True`) está en
[`test/evidencia_c07.txt`](test/evidencia_c07.txt). Para reproducirla, arrancá el servidor con
`SQL_ECHO=true` (ver §Configuración de `.env`) y corré `test/C-07.http`.

## Casos de prueba (test/)

Los casos se corren **en orden** después de `python reiniciar.py`, con el servidor en
`http://localhost:8000`. Los `.http` son compatibles con VS Code *REST Client* e IntelliJ *HTTP Client*;
`C-08` se ejecuta aparte con `psql`.

| Orden | Archivo | Caso | Resultado esperado |
|---|---|---|---|
| 1 | `C-01.http` | C-01 | `GET /duenios/abc` → **422** sin ejecutar el handler. |
| 2 | `C-02.http` | C-02 | Email de dueño o nombre de práctica repetido → **409** con mensaje propio. |
| 3 | `C-03.http` | C-03 | Segunda ficha para el mismo dueño → **409**. |
| 4 | `C-04.http` | C-04 | Mascota con dueño inexistente y turno con práctica inexistente → **409**; del turno no queda nada. |
| 5 | `C-05.http` | C-05 | Borrar dueño con mascotas → **409**; borrar turno → **204** y sus prácticas ya no están. |
| 6 | `C-06.http` | C-06 | Turno válido con dos prácticas → **201** con precios copiados y total `27000.00`. |
| 7 | `C-07.http` | C-07 | Detalle con 1 y con 3 prácticas → **mismas 2 consultas** en la consola. |
| 8 | `C-08.sql` | C-08 | `UPDATE practica SET precio = 0` directo en la base → la base lo rechaza por el **CHECK**. |
| 9 | `C-09.http` | C-09 | Consultas simultáneas al laboratorio + `GET /health/live` → el health responde de inmediato. |

Para la evidencia de C-07, activá el log de SQL antes de arrancar el servidor:

```powershell
# PowerShell
$env:SQL_ECHO="true"; uvicorn app.main:app --reload
```

```bash
# bash
SQL_ECHO=true uvicorn app.main:app --reload
```

### Fecha del turno en las respuestas

La API acepta la fecha con offset y **normaliza la respuesta a UTC con sufijo `Z`** (QA-06). Ejemplo
del caso C-06:

```json
{
  "mascota_id": 1,
  "fecha": "2026-11-12T10:30:00-03:00",
  "motivo": "Control anual",
  "practicas": [{ "practica_id": 1 }, { "practica_id": 3 }]
}
```

Respuesta `201` (fragmento): `"fecha": "2026-11-12T13:30:00Z"`.

## Estructura del proyecto

```text
.
├── app/
│   ├── main.py                  # FastAPI, lifespan y registro de routers
│   ├── core/
│   │   ├── config.py            # Lectura fail-fast de DATABASE_URL
│   │   └── database.py          # Motor, sessionmaker y get_session
│   └── modules/
│       ├── health/              # /health/live, /health/ready
│       ├── duenios/             # Duenio + FichaDuenio (models, schemas, service, router)
│       ├── mascotas/            # CRUD de mascotas con paginación
│       ├── practicas/           # Catálogo de prácticas
│       ├── turnos/              # Turno + TurnoPractica (transacción todo-o-nada)
│       └── laboratorio/         # Offload de consultar_stock (cliente de la cátedra)
├── test/                        # Casos C-01..C-09, evidencia C-07 y tests de pytest
├── reiniciar.py                 # Borra, crea el esquema y carga el seed
├── requirements.txt
├── env.example                  # Plantilla de DATABASE_URL sin secretos
└── README.md
```

**Alcance**: API REST de backend, **sin UI** y **sin autenticación** ni RBAC (fuera de la consigna).
No usa Alembic, Docker ni CI: el esquema se crea con `SQLModel.metadata.create_all` desde
`reiniciar.py`.

## Chequeo final de entrega

Condición de corrección: el proyecto debe levantar **desde una base vacía**.

1. Partí de una base PostgreSQL sin tablas (por ejemplo, `DROP SCHEMA public CASCADE; CREATE SCHEMA public;`
   con un usuario con permisos, o una base `veterinaria` recién creada).
2. Ejecutá `python reiniciar.py`. Debe terminar sin error y crear las **6 tablas**: `duenio`,
   `ficha_duenio`, `mascota`, `practica`, `turno` y `turno_practica`.
3. Verificá el seed: **2 dueños**, **3 mascotas**, **4 prácticas** y **1 turno** con 2 prácticas.
   ```sql
   SELECT (SELECT count(*) FROM duenio)   AS duenios,
          (SELECT count(*) FROM mascota)  AS mascotas,
          (SELECT count(*) FROM practica) AS practicas,
          (SELECT count(*) FROM turno)    AS turnos;
   ```
   Resultado esperado: `2 | 3 | 4 | 1`.
4. Arrancá `uvicorn app.main:app` y comprobá:
   - `GET /health/live` → **200** `{"estado": "vivo"}` (no toca la base).
   - `GET /health/ready` → **200** con la base disponible (`503` si no contesta).
5. Creá el turno de ejemplo de C-06 y confirmá que la fecha vuelve como `2026-11-12T13:30:00Z` y el
   total como `27000.00`.
