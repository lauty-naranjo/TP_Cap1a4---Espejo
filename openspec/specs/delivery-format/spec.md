# delivery-format Specification

## Purpose
Define el contrato de entrega del repositorio: un README que permite levantar el proyecto desde cero,
la explicación del índice de `turno_practica.turno_id`, la evidencia del caso C-07 integrada y la
higiene de secretos (US-801).

## Requirements

### Requirement: Repositorio de entrega completo y sin secretos
El repositorio SHALL incluir el código fuente de la aplicación, `requirements.txt`, `env.example`,
`reiniciar.py` y la carpeta `test/`. El archivo `.env` NO SHALL estar versionado y el repositorio NO
SHALL contener credenciales reales: `env.example` sólo muestra la forma de `DATABASE_URL` con
placeholders.

#### Scenario: Artefactos obligatorios presentes
- **WHEN** se inspecciona la raíz del repositorio y la carpeta `test/`
- **THEN** están `app/`, `requirements.txt`, `env.example`, `reiniciar.py` y `test/` con los casos `C-01`..`C-09`

#### Scenario: `.env` fuera del versionado
- **WHEN** se consulta el estado de git para `.env`
- **THEN** el archivo está ignorado por `.gitignore` y no está trackeado

#### Scenario: `env.example` sin credenciales reales
- **WHEN** se lee `env.example`
- **THEN** sólo declara `DATABASE_URL` con usuario y password de placeholder apuntando a `localhost:5432/veterinaria`

### Requirement: README con puesta en marcha desde cero
El `README.md` SHALL documentar, en orden, los pasos para levantar el proyecto desde cero: crear y
activar el entorno virtual, instalar las dependencias, copiar `env.example` a `.env` y completar
`DATABASE_URL`, ejecutar `python reiniciar.py` y arrancar el servidor con `uvicorn`. SHALL indicar
Python 3.12 y PostgreSQL 16, y NO SHALL incluir credenciales reales.

#### Scenario: Pasos presentes y en orden
- **WHEN** se lee el README
- **THEN** aparecen, en ese orden, entorno virtual, dependencias, `.env`, `python reiniciar.py` y `uvicorn`

#### Scenario: Comandos para PowerShell y bash
- **WHEN** se sigue la puesta en marcha en Windows (PowerShell) o en bash
- **THEN** el README ofrece el comando equivalente para cada shell en los pasos que difieren

#### Scenario: Sin credenciales reales
- **WHEN** se revisan los fragmentos de configuración del README
- **THEN** la URL de ejemplo usa placeholders y no una credencial de trabajo

### Requirement: Explicación del índice de turno_practica.turno_id
El README SHALL explicar en 1–2 líneas por qué `turno_practica.turno_id` no lleva índice propio: la
PK compuesta `(turno_id, practica_id)` es un índice cuya primera columna es `turno_id`, por lo que ya
cubre las búsquedas por turno (US-301 CA-2, US-801 CA-3).

#### Scenario: Explicación del índice compuesto
- **WHEN** se lee la sección del modelo de datos del README
- **THEN** explica que la PK compuesta sirve como índice por su primera columna y que no hace falta un índice propio en `turno_id`

#### Scenario: Índice del lado M:N
- **WHEN** se describe el esquema de `turno_practica`
- **THEN** aclara que `practica_id` sí tiene índice propio porque no es la primera columna de la PK

### Requirement: Evidencia del caso C-07 en la entrega
La entrega SHALL incluir la evidencia del caso C-07: un fragmento de consola con el detalle de un turno
con una práctica y con tres prácticas, mostrando que ambos emiten las mismas 2 consultas fijas
(US-801 CA-4).

#### Scenario: README integra la evidencia
- **WHEN** se lee el README
- **THEN** incluye el fragmento de las consultas para 1 y para 3 prácticas, o un enlace directo a la evidencia cruda

#### Scenario: Evidencia cruda disponible
- **WHEN** se inspecciona `test/evidencia_c07.txt`
- **THEN** contiene los dos casos (1 y 3 prácticas) y la conclusión de 2 consultas fijas en ambos

### Requirement: Verificación automática del contrato de entrega
La suite SHALL incluir `test/test_entrega.py`, que verifica sin base de datos los CA de la entrega y
falla si falta el README, una sección obligatoria, la explicación del índice, la evidencia C-07 o la
higiene de secretos.

#### Scenario: README ausente
- **WHEN** se ejecuta `pytest` sin `README.md`
- **THEN** el test de entrega falla señalando el artefacto faltante

#### Scenario: Entrega completa
- **WHEN** se ejecuta `pytest` con el README completo y `.env` ignorado
- **THEN** el test de entrega pasa junto con el resto de la suite

### Requirement: Chequeo final sobre base vacía
El README SHALL documentar el chequeo final de corrección: sobre una base PostgreSQL vacía,
`python reiniciar.py` crea las 6 tablas (`duenio`, `ficha_duenio`, `mascota`, `practica`, `turno`,
`turno_practica`) y carga el seed, y el proyecto levanta con `uvicorn` y responde en `/health/live` y
`/health/ready`.

#### Scenario: Esquema y seed desde cero
- **WHEN** se ejecuta `python reiniciar.py` sobre una base vacía
- **THEN** se crean las 6 tablas y queda el seed de 2 dueños, 3 mascotas, 4 prácticas y 1 turno con 2 prácticas

#### Scenario: Proyecto operativo
- **WHEN** se arranca `uvicorn app.main:app` con la base creada
- **THEN** `/health/live` responde 200 y `/health/ready` responde 200 con la base disponible
