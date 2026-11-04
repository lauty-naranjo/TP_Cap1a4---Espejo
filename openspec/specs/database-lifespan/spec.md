# database-lifespan Specification

## Purpose

Ciclo de vida de la conexión a PostgreSQL: el servicio crea el motor asincrónico y la fábrica de
sesiones al arrancar, entrega una sesión nueva por petición a los handlers con
`expire_on_commit=False`, y libera el pool al apagarse (US-101, Épica 1).

## Requirements

### Requirement: Motor asíncrono y fábrica de sesiones en el lifespan
El servicio SHALL crear el motor asincrónico y la fábrica de sesiones a partir de `DATABASE_URL` en el
lifespan, almacenarlos en `app.state` y cerrar el motor al apagarse el proceso (US-101 CA-1).

#### Scenario: Motor y sessionmaker creados en el arranque
- **GIVEN** un archivo `.env` con `DATABASE_URL` apuntando a una base PostgreSQL asincrónica
- **WHEN** el proceso de la aplicación se inicia
- **THEN** el lifespan crea el motor asíncrono y la sessionmaker y los guarda en `app.state`

#### Scenario: Motor cerrado en el apagado
- **GIVEN** el servicio corriendo con el motor creado
- **WHEN** el proceso se apaga
- **THEN** el motor se cierra liberando el pool

### Requirement: Sesión por petición con expiración desactivada
El servicio SHALL proveer al handler una sesión nueva por petición mediante la dependencia
`get_session`, con `expire_on_commit=False` (US-101 CA-2).

#### Scenario: Sesión nueva por petición
- **GIVEN** una petición HTTP llega al servicio
- **WHEN** el router resuelve la dependencia `get_session`
- **THEN** se crea una sesión nueva con `expire_on_commit=False` y se cierra al finalizar la petición
