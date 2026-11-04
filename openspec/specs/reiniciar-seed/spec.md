# reiniciar-seed Specification

## Purpose

Provee un estado de base de datos reproducible: `reiniciar.py` borra las tablas, las crea con
`create_all` y carga un seed mínimo, funcionando sobre una base vacía (US-302).

## Requirements

### Requirement: reiniciar.py deja la base en un estado conocido
El sistema SHALL proveer un script `reiniciar.py` que borre las tablas, las cree con
`SQLModel.metadata.create_all` y cargue datos iniciales, funcionando sobre una base vacía.

#### Scenario: Script corre de punta a punta
- **GIVEN** una base de datos PostgreSQL vacía y accesible vía `DATABASE_URL`
- **WHEN** se ejecuta `python reiniciar.py`
- **THEN** las tablas se crean y quedan pobladas sin errores

### Requirement: Seed mínimo obligatorio
El script SHALL cargar al menos 2 dueños (uno con ficha), 3 mascotas, 4 prácticas y 1 turno con 2
prácticas.

#### Scenario: Conteo del seed
- **WHEN** se inspecciona la base después de `python reiniciar.py`
- **THEN** hay 2 dueños, 1 ficha, 3 mascotas, 4 prácticas, 1 turno y 2 filas en `turno_practica`

### Requirement: Precios coherentes con el contrato del turno
El seed SHALL fijar los precios `Consulta` = 15000.00 y `Vacuna antirrábica` = 12000.00, con el turno
de ejemplo con total 27000.00, para reproducir el caso C-06.

#### Scenario: Precios congelados en el turno
- **WHEN** se consulta el catálogo y el turno sembrados
- **THEN** `Consulta` vale 15000.00, `Vacuna antirrábica` vale 12000.00 y el turno tiene total 27000.00
