# Design — c-11-delivery-readme

## Context

Ver `proposal.md` §Why. El estado del repo que condiciona la entrega (verificado al proponer):

- `pytest -q` → **65 passed**; los 9 casos `C-01`..`C-09` corren contra la app real.
- `python reiniciar.py` funciona sobre base vacía: crea 6 tablas (`duenio`, `ficha_duenio`,
  `mascota`, `practica`, `turno`, `turno_practica`) + seed (2 dueños, 3 mascotas, 4 prácticas,
  1 turno con 2 prácticas).
- `turno_practica`: `turno_practica_pkey (turno_id, practica_id)` e `ix_turno_practica_practica_id
  (practica_id)`. No hay índice propio en `turno_id` — es intencional (KB 04 §turno_practica).
- `test/evidencia_c07.txt` ya existe: 2 consultas fijas con 1 y con 3 prácticas (capturada en C-10).
- `.env` está en `.gitignore` y no trackeado; `env.example` sólo tiene placeholders.
- **No hay `README.md` todavía** (este change lo crea).
- Fecha del contrato (QA-06): `2026-11-12T10:30:00-03:00` se devuelve como
  `2026-11-12T13:30:00Z` (UTC, sufijo `Z`).

## Goals / Non-Goals

**Goals:**
- Un README que un tercero pueda seguir de punta a punta sin conocimiento previo del repo.
- Que la evidencia C-07 y la explicación del índice queden **en el README** (no sólo en archivos
  sueltos), sin duplicar la fuente cruda.
- Que el formato de entrega sea verificable automáticamente, igual que el resto de los CA del TP.

**Non-Goals:**
- Tocar `app/**`, el esquema, `requirements.txt` o el comportamiento de la API.
- Reescribir los casos `.http`/`.sql` ni regenerar `test/evidencia_c07.txt` (C-10 ya los cerró).
- Agregar CI, Dockerfile, Alembic, badges o licencia (fuera de la consigna).
- Producir un PDF o empaquetar un ZIP: se entrega el repositorio.

## Decisions

### D1 — Un único `README.md` en la raíz, en español, con secciones fijas
Secciones: (1) descripción de 2–3 líneas + stack, (2) requisitos, (3) puesta en marcha desde cero,
(4) configuración `.env`, (5) chequeo de arranque, (6) modelo de datos e índice de `turno_practica`,
(7) evidencia C-07, (8) casos de prueba, (9) estructura del proyecto y notas de alcance.

Alternativa descartada: README por módulo + índice. La consigna pide **un** README con los pasos; varios
archivos dispersan la corrección y agregan riesgo de desactualización.

### D2 — Comandos para PowerShell y bash en los pasos que difieren
La cátedra no fija shell. Se documentan ambos caminos sólo donde el comando cambia (activación del
venv, variable de entorno `SQL_ECHO`); el resto usa `python`/`uvicorn` neutros. Se indica Python 3.12
y PostgreSQL 16 como requisitos, no se hardcodea ninguna credencial.

### D3 — Evidencia C-07: fragmento en el README + enlace a la fuente cruda
El README incluye el fragmento mínimo (las 2 consultas de cada caso y la conclusión "2 consultas con 1,
las mismas 2 con 3") y enlaza `test/evidencia_c07.txt`. La consigna acepta "README **o** entrega", así
que se cubren ambas: el corrector ve el fragmento sin abrir archivos y la evidencia completa sigue
siendo la fuente de verdad. No se copia el archivo entero para no duplicar 49 líneas de log que se
desincronizan.

Alternativa descartada: copiar `evidencia_c07.txt` completo dentro del README. Aumenta el ruido y crea
dos copias del mismo hecho.

### D4 — Test de contrato `test/test_entrega.py` sin base de datos
Verifica sobre archivos: (a) `README.md` existe y contiene las secciones/pasos obligatorios en orden;
(b) la explicación del índice menciona PK compuesta / primera columna; (c) la evidencia C-07 está
integrada o enlazada y el archivo crudo conserva los dos casos; (d) `.env` ignorado y `env.example`
sin credenciales (reutiliza el patrón `git check-ignore` de `test/test_config.py`); (e) `requirements.txt`,
`env.example`, `reiniciar.py` y `test/` existen.

Se escribe **antes** del README (RED → GREEN). No necesita PostgreSQL ni la app, por lo que corre en
cualquier entorno y no ralentiza la suite. Alternativa descartada: verificación manual con checklist;
no sobrevive a futuras ediciones del README.

### D5 — La explicación del índice se ancla al esquema real, no a una afirmación genérica
Se documenta que `turno_practica_pkey (turno_id, practica_id)` es un índice B-tree cuya primera columna
es `turno_id`, por lo que sirve para filtrar por turno; `practica_id` sí necesita
`ix_turno_practica_practica_id` porque queda segunda en la PK. Se sugiere (opcional) `\d turno_practica`
en `psql` como comprobación, sin convertirlo en paso obligatorio.

### D6 — Fecha del contrato en UTC con `Z` (QA-06)
Todos los ejemplos del README usan `2026-11-12T13:30:00Z` (normalizada) y aclaran que la entrada acepta
offset (`-03:00`). Evita que el README contradiga la respuesta real de la API.

### D7 — Sin cambios de aplicación; desvíos van a otro change
Si al escribir el README aparece una diferencia entre lo documentado y el código, se documenta lo que el
código hace y se anota el desvío para un change aparte. No se toca `app/**` acá (governance BAJO,
alcance documental).

## Risks / Trade-offs

- **El README se desactualiza respecto del código** → mitigado por `test/test_entrega.py` (falla si
  desaparece una sección o un paso) y por mantener comandos copiables desde `test/LEEME.md`.
- **Duplicar la evidencia C-07 genera deriva** → el README lleva el fragmento mínimo y delega el crudo
  en `test/evidencia_c07.txt`; el test verifica que el enlace/mención exista.
- **Diferencias PowerShell vs bash** → se documentan ambos en los pasos que difieren y se prueba el
  camino PowerShell en el apply (entorno Windows del repo).
- **Placeholders confundidos con credenciales** → `env.example` y README aclaran explícitamente que
  `usuario:password` es un placeholder y que `.env` no se versiona.
- **El test de entrega podría ser trivialmente verde** → cada aserción apunta a un CA concreto
  (secciones, orden, índice, evidencia, git), no a la mera existencia del archivo.

## Migration Plan

- Sólo documentación y tests: no hay migración de datos ni de esquema.
- Secuencia: escribir el test (RED) → escribir el README → GREEN → chequeo final CA-5 sobre base vacía.
- Rollback: borrar `README.md` y `test/test_entrega.py`; el resto del repo queda intacto.

## Open Questions

- Ninguna que cambie el alcance. El nombre exacto de las subsecciones del README queda a criterio del
  apply, siempre que el test de contrato verifique los contenidos exigidos.
