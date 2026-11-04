# Reglas de Negocio

> Fuente: `docs/MiniTP_Cap1a4_Consigna.pdf` (Reglas de negocio, página 5) + reglas transversales de los ejercicios 2 a 6. Los códigos RN-01..RN-09 son los de la propia consigna (mantener exactos, son el contrato con la cátedra).

## Dominio: Restricciones codificadas de la consigna (RN-01..RN-09)

| Regla | Enunciado | Garante esperado |
|---|---|---|
| **RN-01** | El email de un dueño es único. | UNIQUE en la base; **409** |
| **RN-02** | El nombre de una práctica es único. | UNIQUE en la base; **409** |
| **RN-03** | Un dueño tiene como máximo una ficha. | UNIQUE en `ficha_duenio.duenio_id`; **409** |
| **RN-04** | El precio de una práctica es mayor que cero. | CHECK en la base **y** validación del DTO |
| **RN-05** | Un turno se reserva con sus prácticas: viajan dentro del cuerpo del alta del turno, y tiene al menos una. | DTO anidado; **422** si la lista está vacía |
| **RN-06** | El precio de cada práctica se copia del catálogo al reservar el turno, y el total lo calcula el servidor. | Ni el precio ni el total viajan en el DTO |
| **RN-07** | Una misma práctica no aparece dos veces en un turno. | Clave primaria compuesta de `turno_practica`; **409** |
| **RN-08** | No se puede borrar un dueño que tenga mascotas a su nombre. | ON DELETE RESTRICT; **409** |
| **RN-09** | Al borrar un turno se borran sus prácticas. | ON DELETE CASCADE en la base |

## Dominio: Política de integridad (cruza RN-01, 02, 03, 07, 08)

- **RN-INT-01 (consigna, obligatoria)**: ninguna de las reglas RN-01/02/03/07/08 se verifica con una consulta previa del tipo "¿ya existe?". **Se escribe**, y si la base rechaza la escritura, el service atrapa el `IntegrityError`, deshace la transacción y responde **409 con un mensaje propio**.
  - Justificación de la consigna (sección 4.10): entre la pregunta y la escritura hay una ventana en la que otra petición puede escribir lo mismo; la única defensa real es que la base rechace la segunda.
- **RN-INT-02 (consigna, obligatoria)**: el borrado de las prácticas de un turno lo decide la **base** con `ON DELETE CASCADE` (sección 4.3), no el ORM. La relación `Turno.practicas` se declara con `passive_deletes` para que el ORM no intente vaciar ni borrar esas filas por su cuenta.

## Dominio: Transaccionalidad de altas con relaciones

- **RN-TX-01 (consigna, obligatoria)**: el turno se crea con sus prácticas en **una sola transacción** (cumpliendo RN-05 a RN-07). Si una de las prácticas no existe, **no queda guardado nada**: ni el turno ni ninguna de sus prácticas (todo-o-nada).

## Dominio: Contratos HTTP (ejercicio 2)

- **RN-HTTP-01**: códigos de respuesta — **201** al crear, **204** al borrar, **404** si el recurso no existe, **409** si la base rechaza la escritura, **422** si el cuerpo o los parámetros no cumplen el contrato.
- **RN-HTTP-02**: los DTO están separados de los modelos de tabla (sección 2.5) y los de alta no llevan `id`.
- **RN-HTTP-03 (PATCH)**: el PATCH del dueño aplica sólo los campos enviados, con `exclude_unset` (sección 2.6).
- **RN-HTTP-04 (paginación, sólo `GET /mascotas/`)**: envoltorio de la sección 2.9 `{ items, total, page, size, pages }`; `size` vale **20 por defecto** y va de **1 a 100**; una página más allá de `pages` responde **422**; la primera página **siempre responde**, aunque no haya resultados.

## Dominio: Salud del servicio (ejercicio 1)

- **RN-HL-01**: `GET /health/live` **no toca la base**.
- **RN-HL-02**: `GET /health/ready` ejecuta `SELECT 1` y responde **503** si la base no contesta.

## Dominio: Representación de dinero (transversal)

- **RN-DS-01 (consigna)**: el dinero se representa con **`Decimal`, nunca `float`** (sección 2.7); en PostgreSQL, tipos NUMERIC (10,2 en precios, 12,2 en el total).
- **RN-DS-02 (consigna)**: congelamiento de precios — al reservar el turno, el precio de cada práctica se **copia** a `turno_practica.precio_unitario`; si después cambia el precio del catálogo, los turnos ya reservados no cambian.

## Dominio: Asincronía (ejercicio 6)

- **RN-AS-01 (consigna)**: todos los handlers son `async def` y ninguno ejecuta una llamada bloqueante dentro del bucle de eventos (sección 3.6).
- **RN-AS-02 (consigna)**: la biblioteca del laboratorio (`consultar_stock`, sincrónica con `time.sleep(1)`) se llama **sin modificarla** y **fuera del bucle de eventos**; mientras consulta, el servidor sigue atendiendo (`GET /health/live` responde de inmediato aunque haya varias consultas en marcha — caso C-09).

## Dominio: Navegación de relaciones (ejercicio 3)

- **RN-REL-01 (consigna)**: cada relación se declara **en los dos extremos** con `Relationship(back_populates="...")` (sección 4.6).
- **RN-REL-02 (consigna)**: `Duenio.ficha` devuelve **un objeto, no una lista**.
- **RN-REL-03 (consigna)**: lecturas sin N+1 — toda respuesta que incluya datos de una relación los obtiene con carga anticipada declarada en la misma consulta: `joinedload` para relaciones «a uno», `selectinload` para colecciones (sección 4.6). Ninguna lectura puede depender de carga perezosa (fallaría con `MissingGreenlet`, sección 3.8).

## Dominio: Excepciones globales

- Los nombres de tablas y columnas son **obligatorios** (la corrección los usa): se pueden agregar columnas, pero **no quitar ni renombrar** las indicadas.
- Cualquier error de FK (dueño/mascota/práctica inexistente en una alta) es rechazado por la base → `IntegrityError` → **409** (caso C-04), con transacción deshecha (todo-o-nada en turnos).
