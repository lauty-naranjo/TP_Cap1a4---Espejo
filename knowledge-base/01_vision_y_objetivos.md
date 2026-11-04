# Visión y Objetivos

> Fuente: `docs/MiniTP_Cap1a4_Consigna.pdf` (Trabajo Práctico, Programación III, Unidades 1 a 4).

## Propósito del sistema

Desarrollar una **API REST asincrónica para una veterinaria de barrio** que permita registrar a sus clientes (dueños), sus mascotas y los turnos de atención, integrando en un proyecto chico los fundamentos de FastAPI (cap. 1), contratos y CRUD (cap. 2), asincronía sin bloqueos (cap. 3) y persistencia relacional con SQLModel + PostgreSQL con todas sus relaciones (cap. 4).

Es un **Trabajo Práctico académico**: el valor del sistema es demostrar competencias verificables, no servir en producción.

## Objetivos por actor

| Actor | Objetivo principal | Objetivos secundarios |
|---|---|---|
| Veterinaria (negocio) | Llevar registro estructurado de dueños, mascotas y turnos | Congelar precios de prácticas al reservar; mantener catálogo con precios |
| Dueño / cliente (vía API) | Cargar su ficha (teléfono, dirección), registrar mascotas y reservar turnos | Ver sus mascotas y turnos con prácticas detalladas |
| Alumno (autor) | Demostrar dominio de: API asincrónica con `Depends()`, separación modelo/DTO, traducción de 5 tipos de relaciones, carga anticipada sin N+1, delegación de garantías en la base | Entregar repositorio reproducible (`reiniciar.py`, `env.example`, casos `.http`) |
| Cátedra (corrector) | Corregir contra nombres de tablas/columnas obligatorios y reglas de negocio RN-01..RN-09 | Evaluar con rúbrica ponderada (ver criterios) |

## Alcance v1.0 (consigna)

- API asincrónica (**todos los handlers `async def`**) con parámetros tipados y dependencias declaradas con `Depends()`.
- Motor y sesión creados en el **lifespan** de la aplicación; guardados en `app.state`; motor cerrado al apagar.
- Modelos de tabla **separados** de contratos de E/S (DTOs Create/Update/Read).
- Esquema relacional con los 5 tipos de relación: uno a uno, agregación, asociación, composición y muchos a muchos con datos propios.
- Lecturas con **carga anticipada** (`joinedload` / `selectinload`), sin N+1 ni carga perezosa.
- Garantías delegadas en la base: FKs, UNIQUE, CHECK, índices.
- Health checks `GET /health/live` y `GET /health/ready` (SELECT 1 → 503 si la base no contesta).
- Módulo `laboratorio` que llama a biblioteca sincrónica entregada por la cátedra **sin modificarla**, con la llamada fuera del bucle de eventos.
- Casos de prueba `.http` (C-01 a C-09) y `reiniciar.py` con seed conocido.

## Fuera de alcance (explícito en la consigna)

No se evalúa (y no debe implementarse a nivel de requisitos):

- Autenticación ni autorización.
- Repositorios ni Unit of Work (la lógica vive en el `service` de cada módulo que recibe la sesión).
- Colas de tareas.
- Migraciones con Alembic (el esquema se crea con `SQLModel.metadata.create_all`).

## Métricas de éxito (criterios de evaluación)

| Criterio | Peso | Qué se mira |
|---|---|---|
| Proyecto, conexión y ciclo de vida | 10 % | Estructura, lifespan, `Depends`, `.env` y `env.example` |
| Contratos y CRUD | 20 % | DTO separados, códigos HTTP, PATCH parcial, envoltorio de paginación |
| Modelos, restricciones y relaciones | 30 % | Lado de cada FK, 1:1 con UNIQUE, tabla intermedia con su dato, RESTRICT y CASCADE, CHECK, índices y justificación, navegación en ambos extremos |
| Altas con relaciones | 15 % | Ids en agregación/asociación; prácticas dentro del turno en composición; todo o nada |
| Lecturas sin N+1 | 15 % | Carga anticipada adecuada; número fijo de consultas |
| Asincronía sin bloqueos | 10 % | Handlers asincrónicos; biblioteca sincrónica fuera del bucle |

**Condición de corrección**: el proyecto debe levantar, crear su esquema con `python reiniciar.py` sobre una base vacía y no contener credenciales reales en el repositorio; si no, no se corrige hasta subsanar.
