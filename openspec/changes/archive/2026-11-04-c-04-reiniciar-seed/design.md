# Design — c-04-reiniciar-seed

## Context

C-03 dejó los modelos (`SQLModel.metadata`) con las 6 tablas, pero `reiniciar.py` sigue siendo el
placeholder de C-01 (`raise NotImplementedError`). El Flujo 14 (`knowledge-base/07_flujos_principales.md`)
define el comportamiento: borrar tablas → `create_all` → seed (2 dueños, 3 mascotas, 4 prácticas,
1 turno con 2 prácticas). La consigna exige que funcione sobre base vacía (condición de corrección).

## Goals / Non-Goals

**Goals:**
- `python reiniciar.py` borra las tablas, las crea y carga el seed mínimo (US-302 CA-1/CA-2).
- Precios/ids coherentes con el ejemplo de `POST /turnos/` (Consulta=15000.00, Vacuna
  antirrábica=12000.00) para que C-06 reproduzca `total: "27000.00"`.

**Non-Goals:**
- CRUD/contratos HTTP (C-05/C-06); altas (C-07); lecturas N+1 (C-08); laboratorio (C-09);
  casos `.http` (C-10); README (C-11).

## Decisions

### D1 — Script de entrada síncrono con `asyncio.run`
- `reiniciar.py` expone `reiniciar(engine)` (async) y un `main()` que crea el motor desde
  `config.DATABASE_URL` y lo cierra; `if __name__ == "__main__": asyncio.run(main())`.

### D2 — Borrado + creación vía `metadata`
- `SQLModel.metadata.drop_all` y `create_all` con `engine.begin()` + `run_sync` (DD-03: sin Alembic).
  `drop_all` ordena por dependencias (no hay FKs cíclicas), así que no hace falta orden inverso manual.

### D3 — Seed determinístico
- Dueños: `Laura Pérez` (con ficha) y `Carlos Gómez` (sin ficha).
- Mascotas: `Toby` (perro, Laura), `Mishi` (gato, Laura), `Lola` (conejo, Carlos).
- Prácticas: `Consulta` 15000.00, `Desparasitación` 8000.00, `Vacuna antirrábica` 12000.00,
  `Corte de uñas` 5000.00 (los ids 1 y 3 quedan como Consulta y Vacuna, reproduciendo el ejemplo).
- Turno: mascota `Toby`, `fecha` fija con tz, `motivo` "Control anual", `total` 27000.00, con
  `TurnoPractica` de Consulta (15000.00) y Vacuna antirrábica (12000.00).
- `Decimal` para todo dinero (RN-DS-01); `session.flush()` para obtener ids antes de las relaciones.

## Risks / Trade-offs

- [Borrado destructivo] → `reiniciar.py` borra todo por diseño; es el punto. El test lo corre contra la
  base de desarrollo (scratch).
- [Dependencia de `.env`] → el script falla sin `DATABASE_URL` (fail-fast de C-01); esperado.

## Migration Plan

- Sin migración de datos (DD-03); el estado es reproducible desde cero.

## Open Questions

- Ninguna que bloquee. QA-01/QA-02/QA-03 no tocan este script.
