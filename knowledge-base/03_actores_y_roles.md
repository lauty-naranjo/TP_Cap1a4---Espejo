# Actores y Roles

> Fuente: `docs/MiniTP_Cap1a4_Consigna.pdf` (Contexto, Estructura del proyecto, Ejercicio 6).

## Actores del sistema

| Actor | Descripción | Cómo interactúa |
|---|---|---|
| **Dueño (cliente de la veterinaria)** | Persona registrada con nombre y email; máximo una ficha (teléfono, dirección); tiene mascotas a su nombre | A través de los datos que cargan los operadores: es sujeto de CRUD en `/duenios/`, tiene ficha y sus mascotas |
| **Mascota** | Figura a nombre de un (único) dueño; entidad con existencia propia (puede cambiar de dueño) | Sujeto de CRUD en `/mascotas/`; referida por los turnos |
| **Turno (atención)** | Reserva para una mascota en una fecha con zona horaria, con motivo; se crea junto a sus prácticas (composición) | CRUD parcial en `/turnos/` (alta, detalle, borrado) |
| **Veterinaria / operador del sistema** | Usa la API para registrar dueños, mascotas, catálogo y turnos | Consumidor de todos los endpoints; sin autenticación en esta versión |
| **Laboratorio externo (simulado)** | Provee stock de vacunas vía función sincrónica entregada por la cátedra | Llamado por `GET /laboratorio/stock/{vacuna}` — la función no se modifica |
| **Alumno / desarrollador** | Autor del TP | Escribe el código, `reiniciar.py`, casos `.http`, README |
| **Cátedra (corrector)** | Evalúa contra nombres de tablas/columnas obligatorios, RN-01..RN-09 y rúbrica | Corre el proyecto, corre `reiniciar.py`, verifica casos C-01..C-09 |

**Sin autenticación ni autorización** (explícitamente fuera de alcance): no hay usuarios ni roles RBAC. Cualquier cliente HTTP puede usar todos los endpoints.

## RBAC — Matriz de permisos

No aplica en esta versión (no hay autenticación/autorización). Todos los endpoints son públicos dentro del servicio.

| Rol | Recurso | Permisos |
|---|---|---|
| (sin rol / público) | Todos los recursos | CREATE, READ, UPDATE, DELETE |

Única limitación real: las reglas de negocio de la base (ver `05_reglas_de_negocio.md`), no de identidad.

## Rutas públicas

Todas. Sin autenticación, cada ruta es pública (ver tabla completa en `02_descripcion_general.md`):

- `GET /health/live` — no toca la base.
- `GET /health/ready` — ejecuta `SELECT 1`; 503 si la base no contesta.
- `/duenios/` (POST), `/duenios/{id}` (GET, PATCH, DELETE), `/duenios/{id}/ficha` (POST), `/duenios/{id}/mascotas` (GET).
- `/mascotas/` (POST, GET listado paginado), `/mascotas/{id}` (GET).
- `/practicas/` (POST, GET catálogo).
- `/turnos/` (POST), `/turnos/{id}` (GET, DELETE).
- `/laboratorio/stock/{vacuna}` (GET).
