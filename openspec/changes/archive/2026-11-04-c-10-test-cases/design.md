# Design — c-10-test-cases

## Context

La consigna (Épica 7, US-701) exige 9 casos mínimos en `test/`, corribles después de
`python reiniciar.py`, cada uno con la respuesta esperada en un comentario. El caso C-08 va en `.sql`
(se ejecuta directo contra la base); los demás en `.http`. QA-04 deja la organización a criterio del
alumno.

## Goals / Non-Goals

**Goals:**
- Un archivo por caso (`C-01`..`C-09`), autoexplicativo y con la respuesta esperada.
- Evidencia de consultas fijas del C-07 (echo=True) capturada para la entrega.
- Caso C-08 en `.sql` demostrando el CHECK de la base.

**Non-Goals:**
- El README de entrega y la explicación del índice (C-11, a cargo de otro integrante).
- Automatizar la ejecución de `.http` (los casos se corren con un cliente HTTP).

## Decisions

### D1 — Un archivo por caso (QA-04)
- `C-01.http` … `C-07.http`, `C-09.http` + `C-08.sql`. Formato compatible con VS Code REST Client e
  IntelliJ HTTP Client (`###` separa peticiones, `#` comenta la respuesta esperada).

### D2 — Orden sobre el seed de C-04
- Los casos se corren en orden. C-05 borra el turno del seed (204) y C-06/C-07 crean turnos nuevos;
  C-07 usa variables del cliente (`# @name`) para tomar los ids devueltos, así no depende del orden.

### D3 — Evidencia de C-07 con `SQL_ECHO`
- Se agrega `SQL_ECHO=true` a `create_engine` (default apagado) para ver las consultas en la consola
  al correr el caso. Además se captura `test/evidencia_c07.txt` con un engine `echo=True`, mostrando
  las 2 consultas fijas con 1 y con 3 prácticas.

### D4 — C-08 en `.sql`
- `UPDATE practica SET precio = 0 WHERE id = 1;` → la base responde `CheckViolationError`
  (`ck_practica_precio_positivo`), demostrando que el CHECK, no el DTO, es el último garante.

## Risks / Trade-offs

- La simultaneidad real del C-09 no se puede forzar con un cliente `.http` (manda secuencial); el
  archivo lo documenta y se remite a la prueba programática `test_laboratorio.py` (3 consultas
  paralelas ≈ 1 s).

## Migration Plan

- Sin cambios de esquema. Rollback = eliminar los archivos de `test/` y el toggle `SQL_ECHO`.
