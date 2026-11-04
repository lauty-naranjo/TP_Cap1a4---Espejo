# Veterinaria (TP Programación III, Cap. 1–4) — Base de Conocimiento

Base de conocimiento generada a partir de la consigna del TP en modo **ingest** (silent) desde `docs/MiniTP_Cap1a4_Consigna.pdf` (extracto de texto: `docs/consigna_extracted.txt`).

## Resumen Ejecutivo

API REST **asincrónica** (Python 3.12 + FastAPI ≥ 0.111 + SQLModel ≥ 0.0.24 + SQLAlchemy 2.0 async + asyncpg ≥ 0.30 + **PostgreSQL 16**) para una veterinaria de barrio: registra dueños con ficha (1:1), mascotas (agregación), turnos (asociación) que nacen con sus prácticas (composición) y llevan varias prácticas del catálogo con **precio congelado** (M:N con datos). La integridad (UNIQUE, CHECK, FK RESTRICT/CASCADE + índices) se **delega en la base**; el service atrapa `IntegrityError` → 409, sin consultas previas "¿ya existe?". Los handlers son todos `async def`, se leen relaciones con carga anticipada (`joinedload`/`selectinload`, sin N+1) y la biblioteca sincrónica del laboratorio se corre **fuera del event loop**. Sin auth/repos/colas/Alembic (fuera de alcance por consigna). Entrega: repo con `requirements.txt`, `env.example`, `reiniciar.py`, `test/` (casos C-01..C-09) y `README.md` con pasos desde cero y la explicación del índice de `turno_practica.turno_id`.

## Índice de Archivos

| Archivo | Contenido |
|---------|-----------|
| [01_vision_y_objetivos.md](01_vision_y_objetivos.md) | Propósito, objetivos por actor, alcance v1.0, fuera de alcance, métricas de éxito (rúbrica de la cátedra) |
| [02_descripcion_general.md](02_descripcion_general.md) | Stack dictado por la consigna, arquitectura general, integraciones (laboratorio sincrónico), tabla completa de endpoints + códigos HTTP |
| [03_actores_y_roles.md](03_actores_y_roles.md) | Actores (dueño, mascota, turno, operador, laboratorio, cátedra), sin RBAC (no hay auth), rutas públicas |
| [04_modelo_de_datos.md](04_modelo_de_datos.md) | Entidades con columnas/restricciones obligatorias, los 5 tipos de relación con su justificación, ERD textual, seed de `reiniciar.py` |
| [05_reglas_de_negocio.md](05_reglas_de_negocio.md) | RN-01..RN-09 (consigna literal) + reglas transversales: IntegrityError→409, transacción todo-o-nada, paginación, Decimal, asincronía, relaciones |
| [06_funcionalidades.md](06_funcionalidades.md) | Historias de usuario por épica (un EP por ejercicio de la consigna) + casos de prueba C-01..C-09 + formato de entrega |
| [07_flujos_principales.md](07_flujos_principales.md) | 14 flujos extremo a extremo: lifespan, sesiones, CRUD, alta de turno (transacción única), lecturas sin N+1, borrados RESTRICT/CASCADE, laboratorio async |
| [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) | Patrones, estructura de directorios obligatoria, seguridad (sin auth; secrets vía `.env`/`env.example`), variables de entorno, formato de entrega |
| [09_decisiones_y_supuestos.md](09_decisiones_y_supuestos.md) | DD-01..DD-08 (la mayoría dictadas por la consigna) + SU-01..SU-07 (supuestos inferidos, con su riesgo y validación) |
| [10_preguntas_abiertas.md](10_preguntas_abiertas.md) | Ambigüedades del modo ingest, QA-01..QA-06 priorizadas e incertidumbres de discovery (`scale` con baja confianza) |

## Quick Start para Desarrolladores

1. Entender qué se entrega y cómo se corrige → [01](01_vision_y_objetivos.md), [06](06_funcionalidades.md) (épica 8)
2. Entender el dominio y sus relaciones → [04](04_modelo_de_datos.md), [03](03_actores_y_roles.md)
3. Entender las reglas → [05](05_reglas_de_negocio.md)
4. Entender los endpoints y el stack → [02](02_descripcion_general.md)
5. Entender cómo corre todo → [07](07_flujos_principales.md), [08](08_arquitectura_propuesta.md)
6. Antes de codificar → [10](10_preguntas_abiertas.md) y [09](09_decisiones_y_supuestos.md)

## Cobertura de la consigna

Cada sección del PDF está mapeada a un archivo canónico (ver resumen "TEMAS CUBIERTOS" del agente). No se dejó ninguna consigna sin documento: ejercicios 1–6, reglas RN-01..RN-09, estructura de proyecto, seed, casos C-01..C-09, criterios de evaluación y formato de entrega.
