# Tasks

> Regla dura afectada por tarea se marca inline con `<!-- rn: … -->`. Nota TDD: Strict TDD en el apply.

## 1. Casos `.http` de la consigna (US-701)

- [x] 1.1 `test/C-01.http` (422 path param no entero) y `test/C-02.http` (409 email/nombre repetido)
- [x] 1.2 `test/C-03.http` (409 segunda ficha) y `test/C-04.http` (409 mascota/turno con FK inexistente)
  <!-- rn: sin consulta previa; la base rechaza → 409 (RN-INT-01) -->
- [x] 1.3 `test/C-05.http` (409 dueño con mascotas RESTRICT; 204 turno con CASCADE)
  <!-- rn: RESTRICT (RN-08) y CASCADE (RN-09) decididos por la base -->
- [x] 1.4 `test/C-06.http` (201 turno válido con 2 prácticas, total y fecha del contrato)
- [x] 1.5 `test/C-07.http` (detalle con 1 y con 3 prácticas, consultas fijas) y `test/C-09.http`
  (laboratorio + health/live)

## 2. Caso C-08 en `.sql`

- [x] 2.1 `test/C-08.sql`: `UPDATE practica SET precio = 0` → rechazado por el CHECK `ck_practica_precio_positivo`
  <!-- rn: CHECK de la base como garante de precio > 0 (RN-04) -->

## 3. Evidencia y guía

- [x] 3.1 Toggle `SQL_ECHO=true` en `app/core/database.py` (default apagado) para ver el SQL en la consola
  <!-- rn: no cambia el comportamiento por defecto -->
- [x] 3.2 `test/evidencia_c07.txt`: fragmento echo=True con 2 consultas fijas (1 y 3 prácticas)
- [x] 3.3 `test/LEEME.md`: cómo correr los casos (servidor, orden, SQL_ECHO, `.sql`)

## 4. Integración del cambio

- [x] 4.1 Verificar los 9 casos contra la app real → todos con el código esperado (422/409/204/404/201/200)
- [x] 4.2 Suite completa verde (`pytest` → 65 passed)

## Workflow follow-up

- `/opsx:archive c-10-test-cases`.
- Marcar `[x]` en la entrada `[C-10]` de `CHANGES.md`.
- C-11 (`delivery-readme`) a cargo de Lautaro: usar `test/evidencia_c07.txt` para la evidencia.
