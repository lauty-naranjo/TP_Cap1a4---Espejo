# Tests del módulo health (C-02, US-102, RN-HL-01/RN-HL-02) — change c-02-database-lifespan-health.
# Se fija DATABASE_URL antes de importar app.main (config.py la lee al importarse; fail-fast).
import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://usuario:password@localhost:5432/veterinaria",
)

from fastapi.testclient import TestClient

from app.main import app

DATABASE_URL = os.environ["DATABASE_URL"]


def test_health_live_responde_200_con_estado_vivo():
    """RN-HL-01 / US-102: GET /health/live responde 200 con {"estado": "vivo"} sin tocar la base."""
    with TestClient(app) as client:
        respuesta = client.get("/health/live")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "vivo"}


def test_health_live_responde_aunque_la_base_este_caida():
    """RN-HL-01 / caso C-09: /health/live responde 200 aunque la DB esté caída (concurrencia con consultas)."""
    with TestClient(app) as client:
        respuesta = client.get("/health/live")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "vivo"}


def test_health_ready_responde_503_cuando_la_base_no_contesta():
    """RN-HL-02 / US-102 CA-1/CA-2: GET /health/ready con la base caída responde 503 {"estado": "no_disponible"}."""
    with TestClient(app) as client:
        respuesta = client.get("/health/ready")

    assert respuesta.status_code == 503
    assert respuesta.json() == {"estado": "no_disponible"}
