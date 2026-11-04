# Modelo de Datos

> Fuente: `docs/MiniTP_Cap1a4_Consigna.pdf` (Modelo de dominio, Figura 1). Los **nombres de tablas y columnas son obligatorios** (la corrección los usa): se pueden agregar columnas, pero no quitar ni renombrar las indicadas.

## Dominios

- **Dueños** (`duenio`, `ficha_duenio`): clientes de la veterinaria y su ficha de contacto. `FichaDuenio` vive en el módulo `duenios`.
- **Mascotas** (`mascota`): pacientes, a nombre de un dueño.
- **Prácticas** (`practica`): catálogo de servicios con precio (consulta, vacuna, desparasitación, ...).
- **Turnos** (`turno`, `turno_practica`): turnos de atención y las prácticas reservadas con el precio congelado. `TurnoPractica` vive en el módulo `turnos`.
- **Laboratorio** (`laboratorio`): integración simulada, sin persistencia propia.

## Relaciones requeridas por la consigna (una de cada tipo)

| Tipo | Entre | Por qué es de ese tipo |
|---|---|---|
| Uno a uno | Dueño ↔ Ficha | Un dueño tiene como máximo una ficha: FK + UNIQUE (sección 4.3) |
| Agregación | Dueño → Mascota | La mascota existe por sí misma y puede cambiar de dueño; mientras un dueño tenga mascotas a su nombre, no se puede borrar |
| Asociación | Turno → Mascota | El turno conoce a la mascota que atiende, pero ninguno es parte del otro |
| Composición | Turno → TurnoPractica | Una práctica reservada no tiene sentido sin su turno: nace con él y se borra con él |
| M:N con datos | Turno ↔ Practica (vía `turno_practica`) | Un turno lleva varias prácticas y una práctica figura en muchos turnos; el precio cobrado es de la **relación**, no de la práctica |

## ERD (texto)

```
duenio (1) ────[UNIQUE fk]──── ficha_duenio        (1:1; FK duenio.duenio_id UNIQUE)
duenio (1) ────[RESTRICT]──── mascota (N)         (agregación; FK mascota.duenio_id, índice)
mascota (1) ───[fk, índice]─── turno (N)          (asociación; FK turno.mascota_id)
turno (1) ─────[CASCADE]───── turno_practica (N)  (composición; FK turno_id, sin índice propio: cubierto por la PK compuesta)
practica (1) ──[fk, índice]─── turno_practica (N) (lado M:N; FK practica_id, índice)
```

## Entidades

### duenio
- `id` (PK), `nombre`, `email`
- Constraints: `email` UNIQUE
- Relaciones: `ficha` (1:1, devuelve **objeto, no lista**), `mascotas` (1:N agregación)

### ficha_duenio
- `id` (PK), `duenio_id` (FK → duenio), `telefono`, `direccion`
- Constraints: `duenio_id` UNIQUE (garantiza el 1:1)
- Relación: duenio (N:1)

### mascota
- `id` (PK), `nombre`, `especie`, `duenio_id` (FK → duenio)
- Constraints: `duenio_id` con **ON DELETE RESTRICT**; **índice** en `duenio_id` (PostgreSQL no crea solo el índice de una FK — sección 4.10)

### practica
- `id` (PK), `nombre`, `precio` (NUMERIC 10,2)
- Constraints: `nombre` UNIQUE; CHECK `precio > 0`

### turno
- `id` (PK), `mascota_id` (FK → mascota), `fecha` (con zona horaria), `motivo`, `total` (NUMERIC 12,2)
- Constraints: CHECK `total >= 0`; **índice** en `mascota_id`
- Composición con `turno_practica`: el borrado lo decide la base con ON DELETE CASCADE, no el ORM (`passive_deletes` para que el ORM no intente vaciar ni borrar esas filas por su cuenta).

### turno_practica
- `turno_id` + `practica_id` (**PK compuesta**), `precio_unitario` (NUMERIC 10,2)
- Constraints: `turno_id` FK con **ON DELETE CASCADE**; CHECK `precio_unitario > 0`; **índice** en `practica_id`
- `turno_id` **no lleva índice propio**: la pista está en la PK compuesta `(turno_id, practica_id)` — por diseño un índice compuesto cuya primera columna es `turno_id` ya sirve para las búsquedas por turno (explicación obligatoria en el README, 1–2 líneas).
- Representa el dato propio del M:N: el precio congelado en el turno.

## Reglas transversales de datos

- Cada relación se declara **en los dos extremos** con `Relationship(back_populates="...")` (sección 4.6).
- `Duenio.ficha` devuelve un objeto, no una lista.
- El dinero se representa con **`Decimal`, nunca `float`** (sección 2.7).
- Alta de turno: precio de cada práctica se copia del catálogo y el `total` lo calcula el **servidor**; ni precio ni total viajan en el DTO (RN-06).

## Seed data inicial (reiniciar.py)

`reiniciar.py` borra las tablas, las crea con `create_all` y carga estos datos mínimos:

- **2 dueños**, uno con ficha.
- **3 mascotas**.
- **4 prácticas**.
- **1 turno con 2 prácticas**.
