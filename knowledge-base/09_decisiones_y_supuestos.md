# Decisiones y Supuestos

> Fuente: `docs/MiniTP_Cap1a4_Consigna.pdf`. Importante: la consigna **dicta** casi todas las decisiones técnicas; lo verdaderamente abierto queda marcado como QA en `10_preguntas_abiertas.md`.

## Decisiones documentadas

### DD-01 — Stack tecnológico fijado por la cátedra
**Decisión**: Python 3.12, FastAPI ≥ 0.111 (todo `async def`), SQLModel ≥ 0.0.24, SQLAlchemy 2.0 asincrónico, asyncpg ≥ 0.30, PostgreSQL 16, python-dotenv 1.0, uvicorn (el de `fastapi[standard]`).
**Contexto**: la consigna trae la tabla de "Requisitos técnicos" con versiones mínimas y uso.
**Alternativas consideradas**: ninguna — es una condición del TP.
**Justificación**: el TP evalúa específicamente estos conceptos (capítulos 1 a 4).
**Trade-offs aceptados**: ninguno libre; cambiar el stack rompe la corrección.

### DD-02 — Sin autenticación/autorización, sin repositorios/UoW, sin colas, sin Alembic
**Decisión**: no implementar auth, capa de repositorios ni Unit of Work, colas de tareas ni migraciones.
**Contexto**: sección "Qué queda afuera".
**Justificación**: no se evalúan; la lógica vive en el `service` de cada módulo y recibe la sesión como parámetro.
**Trade-offs aceptados**: endpoints públicos; es lo pedido.

### DD-03 — Esquema creado con `create_all`, no con migraciones
**Decisión**: `SQLModel.metadata.create_all` crea el esquema, ejecutado (con borrado previo y seed) por `reiniciar.py`.
**Contexto**: explícito en la consigna (secciones "Qué queda afuera" y ejercicio 3).
**Justificación**: reproducibilidad del estado para los casos de prueba; base vacía → TP corregible.
**Trade-offs aceptados**: sin historial de migraciones; aceptable para un TP.

### DD-04 — Integridad vía base de datos y patrón IntegrityError → 409
**Decisión**: las unicidades, CHECKs y FKs son restricciones de la base; el service escribe primero y atrapa `IntegrityError` (rollback + 409 con mensaje propio). Cero consultas previas "¿ya existe?".
**Contexto**: regla explícita de la consigna (sección 4.10, RN-01..RN-09).
**Alternativas consideradas**: validación previa por query — **prohibida** por la ventana de carrera.
**Trade-offs aceptados**: mensajes de error dependen de traducir el error del driver.

### DD-05 — Borrado de prácticas del turno decidido por la base (pasivo para el ORM)
**Decisión**: ON DELETE CASCADE en `turno_practica.turno_id` + declaración de `Turno.practicas` con `passive_deletes` para que el ORM no intente vaciar/borrar filas.
**Contexto**: ejercicio 3 (pista explícita de la consigna).
**Trade-offs aceptados**: el borrado lógico vive en la DB; probarlo (C-05).

### DD-06 — Precios congelados por copia en la relación (M:N con datos)
**Decisión**: `turno_practica.precio_unitario` guarda el precio cobrado al reservar; `total` del turno lo calcula el servidor; ni precio ni total viajan en el DTO.
**Contexto**: RN-06, contexto de negocio en la consigna.
**Trade-offs aceptados**: datos duplicados por diseño (snapshot histórico).

### DD-07 — Llamada sincrónica al laboratorio fuera del bucle de eventos
**Decisión**: llamar a `consultar_stock` sin modificarla, descargándola fuera del event loop (hilo) para que `/health/live` siga respondiendo.
**Contexto**: ejercicio 6 + caso C-09.
**Alternativas consideradas**: `ThreadPoolExecutor` vs `anyio.to_thread.run_sync` (u otro mecanismo análogo) — la consigna **no impone el mecanismo exacto**.
**Justificación**: requisito es el resultado (no bloquear el bucle), no el detalle.
**Trade-offs aceptados**: overhead de hilo por llamada; aceptable con latencia de 1 s.
**Estado**: ⚠ mecanismo concreto por elegir — ver QA-03 en `10_preguntas_abiertas.md`.

### DD-08 — Superficie HTTP mínima dictada por la consigna
**Decisión**: implementar **exactamente** los endpoints de la tabla de referencia (17 rutas). Ej.: no hay `GET /duenios/` (listado general), no hay `PATCH/DELETE` en `mascotas`, no hay `PATCH` de turno ni `GET/PATCH` de ficha (la ficha se lee embebida).
**Contexto**: "Endpoints de referencia" (páginas 9-10).
**Justificación**: la cátedra corrige contra esa tabla; endpoints extra no son evaluados (agregarlos no está prohibido, pero tampoco pedido — ver QA-05).
**Trade-offs aceptados**: superficie de API limitada; es una API de TP, no de producto.

## Supuestos inferidos

### SU-01 — Escala del sistema (baja confianza)
**Supuesto**: el sistema opera a escala de **una sola veterinaria de barrio** con usuarios anónimos/no autenticados (equivalente a single_user en clasificación de descubrimiento); sin multi-tenant ni concurrencia alta.
**Origen**: "Una veterinaria de barrio necesita una API..." (Contexto) + ausencia de auth.
**Riesgo si es falso**: irrelevante para el TP (no hay requisitos de escala).
**Cómo validar**: es un TP académico — asumir y no complicar.

### SU-02 — Nombres de tablas/columnas exactos según consigna (alta confianza)
**Supuesto**: usar los nombres literales `duenio` (sin eñe), `ficha_duenio`, `mascota`, `practica`, `turno`, `turno_practica` y sus columnas, tal cual el PDF.
**Origen**: "Los nombres de tablas y columnas son obligatorios, porque la corrección los usa".
**Riesgo si es falso**: corrección fallida por desvío de nombres.
**Cómo validar**: revisar la tabla del modelo de dominio (página 4) al escribir los `models.py`.

### SU-03 — Normalización de zona horaria en la respuesta (media confianza)
**Supuesto**: `fecha` se guarda como `timestamptz`; en la respuesta se muestra normalizada (el ejemplo de la consigna convierte `-03:00` a `Z`, misma hora). No es obligatorio devolver en UTC — probablemente lo importante es conservar el instante.
**Origen**: ejemplo de POST /turnos/ (página 8): entra `2026-11-12T10:30:00-03:00`, sale `2026-11-12T13:30:00Z`.
**Riesgo si es falso**: solo cambia el formato de la respuesta; los casos C-06 no dependen del formato (pruebas sobre precios/total).
**Cómo validar**: devolver el instante equivalente es válido; el formato exacto es libre mientras se conserve la misma hora.

### SU-04 — Forma del `DuenioRead` en el alta (media confianza)
**Supuesto**: `POST /duenios/` devuelve el dueño; si aún no tiene ficha, la ficha aparece como `null`/ausente. El GET con ficha embebida es lo garantizado.
**Origen**: la tabla de endpoints distingue `DuenioRead` (alta) de "Dueño con su ficha" (detalle).
**Riesgo si es falso**: desvío menor en el contrato de respuesta.
**Cómo validar**: ver QA-02.

### SU-05 — El módulo `laboratorio/cliente.py` lo entrega la cátedra (alta confianza)
**Supuesto**: el archivo `app/modules/laboratorio/cliente.py` con `consultar_stock` **no lo implementa el alumno**; llega con la estructura del TP y solo se escribe su service/router.
**Origen**: "La cátedra entrega el módulo app/modules/laboratorio/cliente.py" (ejercicio 6).
**Riesgo si es falso**: menor; reimplementarlo con el código exacto del PDF es trivial.
**Cómo validar**: preguntar a la cátedra o fijarlo en el setup del repositorio.

### SU-06 — El listado de prácticas no necesita paginación de la sección 2.9 (baja confianza)
**Supuesto**: el envoltorio `{items,total,page,size,pages}` se exige solo en `GET /mascotas/` ("El listado de mascotas" — ejercicio 2); `GET /practicas/` puede devolver una lista simple.
**Origen**: la consigna nombra el envoltorio únicamente al hablar del listado de mascotas.
**Riesgo si es falso**: sobre-ingeniería o sub-entrega en un listado secundario.
**Cómo validar**: ver QA-01.

### SU-07 — Único `requirements.txt` sin lockfile (alta confianza)
**Supuesto**: la entrega requiere un `requirements.txt`; no hay constraint de lockfile (pip-tools/poetry no se mencionan).
**Origen**: "Formato de entrega".
**Riesgo si es falso**: nulo encontrado; elegir pinning razonable (`>=` versiones mínimas de la tabla).
**Cómo validar**: verificar si la cátedra espera versiones fijas completas.
