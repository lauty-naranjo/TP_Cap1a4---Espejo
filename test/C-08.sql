-- ============================================================
-- Caso C-08 — La base rechaza `precio <= 0` por el CHECK (RN-04)
-- ============================================================
-- El precio > 0 se garantiza en la BASE con el CHECK `precio > 0`
-- (constraint `ck_practica_precio_positivo`, definido en C-03), no sólo en el DTO.
-- Ejecutar directo contra la base (NO es un .http):
--
--   psql "postgresql://usuario:password@localhost:5432/veterinaria" -f test/C-08.sql
--
-- RESULTADO ESPERADO (la base lo rechaza):
--   ERROR:  new row for relation "practica" violates check constraint "ck_practica_precio_positivo"
--   DETAIL:  Failing row contains (1, Consulta, 0.00).
-- ============================================================

UPDATE practica SET precio = 0 WHERE id = 1;
