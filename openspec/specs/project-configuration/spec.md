# project-configuration Specification

## Purpose

Configuración por entorno del servicio: la API Veterinaria lee la dirección de su base de datos
PostgreSQL desde una variable de entorno no versionada y arranca (o falla) según cómo esté
configurada, garantizando que ningún secreto real viaje en el repositorio (US-103, Épica 1).

## Requirements

### Requirement: La configuración se lee del archivo .env
El servicio SHALL leer la variable de entorno `DATABASE_URL` desde un archivo `.env` cargado al
iniciar, y exponerla como la única configuración disponible desde el entorno.

#### Scenario: DATABASE_URL presente en .env
- **GIVEN** un archivo `.env` con `DATABASE_URL` apuntando a una base PostgreSQL asincrónica
- **WHEN** el proceso de la aplicación se inicia
- **THEN** la configuración carga `DATABASE_URL` desde el archivo y queda disponible para el
  arranque sin interacción adicional

#### Scenario: Variable definida en el entorno
- **GIVEN** `DATABASE_URL` definida directamente en el entorno (aunque `.env` no exista)
- **WHEN** el proceso de la aplicación se inicia
- **THEN** la configuración la detecta igualmente (el archivo `.env` no es obligatorio si la
  variable ya viene del entorno)

### Requirement: Arranque falla rápido sin DATABASE_URL
El servicio MUST fallar en el arranque con un error claro si `DATABASE_URL` no está definida
ni en `.env` ni en el entorno, sin aceptar un valor por defecto implícito.

#### Scenario: .env ausente y variable indefinida
- **GIVEN** que no existe `.env` y el entorno no define `DATABASE_URL`
- **WHEN** se inicia la aplicación
- **THEN** el proceso aborta antes de levantarse, con un mensaje que indique qué falta configurar

#### Scenario: .env presente pero sin la variable
- **GIVEN** un archivo `.env` que no contiene `DATABASE_URL` y entorno sin ella
- **WHEN** se inicia la aplicación
- **THEN** el proceso aborta con el mismo error claro de configuración faltante

### Requirement: env.example sin secretos y .env fuera del versionado
El repositorio MUST incluir un archivo `env.example` con la forma del valor de `DATABASE_URL`
usando solo placeholders, y MUST excluir el archivo `.env` del versionado para que no existan
credenciales reales en el repositorio (condición de corrección de la cátedra).

#### Scenario: env.example muestra la forma sin secretos
- **GIVEN** el archivo `env.example` del repositorio
- **WHEN** se lo inspecciona
- **THEN** contiene `DATABASE_URL` con la forma
  `postgresql+asyncpg://usuario:password@localhost:5432/veterinaria`, sin credenciales reales

#### Scenario: .env nunca entra al repositorio
- **GIVEN** un `env.example` en el repositorio y un `.env` local con credenciales de trabajo
- **WHEN** se versiona el proyecto (commit)
- **THEN** `.env` queda excluido por el `.gitignore` y su contenido real no queda registrado
