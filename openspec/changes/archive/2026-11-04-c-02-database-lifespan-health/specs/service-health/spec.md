# Spec Delta

## ADDED Requirements

### Requirement: Health check de liveness
El servicio SHALL exponer el endpoint `GET /health/live` que responde 200 con `{"estado": "vivo"}`
sin consultar la base de datos (RN-HL-01).

#### Scenario: Proceso vivo sin base disponible
- **GIVEN** el servicio corriendo
- **WHEN** se solicita `GET /health/live`
- **THEN** responde 200 con `{"estado": "vivo"}` sin tocar la base

### Requirement: Health check de readiness
El servicio SHALL exponer el endpoint `GET /health/ready` que ejecuta un `SELECT 1` contra la base
y responde 200 si la base contesta, o 503 si no la contesta (RN-HL-02).

#### Scenario: Base disponible
- **GIVEN** la base de datos responde al `SELECT 1`
- **WHEN** se solicita `GET /health/ready`
- **THEN** responde 200

#### Scenario: Base no disponible
- **GIVEN** la base de datos no contesta
- **WHEN** se solicita `GET /health/ready`
- **THEN** responde 503
